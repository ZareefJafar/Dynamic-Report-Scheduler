# DatabaseDump.py

import os
import mysql.connector
import subprocess
import logging
import paramiko

class DatabaseDump:
    def __init__(self, record):
        self.record = record
        self.logger = logging.getLogger(__name__)

    def dump_to_database(self):
        logging.basicConfig(level=logging.INFO)

        dump_name = self.record['report_name'].split(',')
        source_config = self.record['sender_creds'].split(',')
        dest_config = self.record['receiver_creds'].split(',')
        dest_password = dest_config[2]

        try:
            # Connect to the destination database
            with mysql.connector.connect(
                host=dest_config[0],
                user=dest_config[1],
                password=dest_password,
                database=dest_config[3]
            ) as connection:
                with connection.cursor() as cursor:
                    # Drop and recreate the destination database
                    cursor.execute(f"DROP DATABASE IF EXISTS `{dest_config[3]}`")
                    cursor.execute(f"CREATE DATABASE `{dest_config[3]}`")
                    connection.commit()

                    self.logger.info(f"Database `{dest_config[3]}` created")

                    # Specify the absolute path for the dump file
                    dump_file_path = os.path.join(os.path.dirname(__file__), f'{dump_name[0]}_dump_source.sql')

                    # Dump data from the specified source database
                    dump_command = [
                        "/usr/bin/mysqldump",
                        "-h", source_config[0],
                        "-u", source_config[1],
                        f"--password={source_config[2]}",  # Use --password option
                        "--databases", source_config[3],  # Avoid backticks
                        "--skip-lock-tables"
                    ]
                    with open(dump_file_path, 'w') as dump_file:
                        subprocess.run(dump_command, stdout=dump_file, check=True)

                    # Transfer dump file to destination server using paramiko
                    transport = paramiko.Transport((dest_config[0], 22))
                    transport.connect(username=dest_config[5], password=dest_config[6])
                    sftp = paramiko.SFTPClient.from_transport(transport)

                    sftp.put(dump_file_path, f'{dump_name[0]}_dump_destination.sql')

                    sftp.close()
                    transport.close()

                    # Load data into destination database
                    load_command = [
                        "mysql",
                        "-h", dest_config[0],
                        "-u", dest_config[1],
                        f"--password={dest_password}",
                        "--database", f"{dest_config[3]}"  # Use backticks (`) to quote the database name
                    ]
                    with open(dump_file_path, 'rb') as dump_file:
                        subprocess.run(load_command, stdin=dump_file, check=True)

                    self.logger.info(f"Data dumped from `{source_config[3]}` to `{dest_config[3]}`")

        except mysql.connector.Error as err:
            self.logger.error(f"MySQL Error: {err}")
        except subprocess.CalledProcessError as err:
            self.logger.error(f"Subprocess Error: {err}")
        except Exception as err:
            self.logger.error(f"Unexpected Error: {err}")

        finally:
            # Clean up dump file
            if os.path.exists(dump_file_path):
                os.remove(dump_file_path)
