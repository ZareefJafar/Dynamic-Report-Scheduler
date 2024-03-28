import os
import subprocess
import logging
import paramiko
from logger_config import setup_logger

class DatabaseDump:
    def __init__(self, record):
        self.record = record
        self.logger = setup_logger()

    def dump_to_database(self):
        self.logger.info("Dumping data to database process started.")

        dump_name = self.record['report_name'].split(',')
        source_config = self.record['sender_creds'].split(',')
        dest_config = self.record['receiver_creds'].split(',')
        dest_password = dest_config[2]

        try:
            # Specify the absolute path for the dump file
            dump_file_path = os.path.join(os.path.dirname(__file__), f'{dump_name[0]}_dump_source.sql')

            # Dump data from the specified source database
            self.logger.info(f"Dumping data from source database {source_config[3]} on server {source_config[0]}...")
            dump_command = [
                "/usr/bin/mysqldump",
                "-h", source_config[0],
                "-u", source_config[1],
                f"--password={source_config[2]}",
                "--databases", source_config[3],
                "--skip-lock-tables"
            ]
            with open(dump_file_path, 'w') as dump_file:
                subprocess.run(dump_command, stdout=dump_file, check=True)
            self.logger.info("Data dumped from source database successfully.")

            # Transfer dump file to destination server using SSH
            self.logger.info(f"Transferring dump file from {source_config[0]} to {dest_config[0]}...")
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=dest_config[0], username=dest_config[5], password=dest_config[6])
            sftp = ssh_client.open_sftp()
            sftp.put(dump_file_path, f'{dump_name[0]}_dump_destination.sql')
            sftp.close()
            self.logger.info("Dump file transferred to destination server successfully.")

            # Drop and recreate the destination database
            self.logger.info(f"Dropping and recreating the destination database {dest_config[3]} on server {dest_config[0]}...")
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(
                f"mysql -u {dest_config[1]} --password='{dest_password}' -e \"DROP DATABASE IF EXISTS `{dest_config[3]}`; CREATE DATABASE `{dest_config[3]}`;\""
            )

            # Load data into destination database
            self.logger.info(f"Loading data into destination database {dest_config[3]} on server {dest_config[0]}...")
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(
                f"mysql -u {dest_config[1]} --password='{dest_password}' --database={dest_config[3]} < {dump_name[0]}_dump_destination.sql"
            )

            # Log any errors or output from the command
            error_output = ssh_stderr.read().decode().strip()
            if error_output:
                self.logger.error(f"Error while executing MySQL command: {error_output}")
            else:
                self.logger.info("Data loaded into the destination database successfully.")

            # Final log message with source and destination server information
            self.logger.info(f"Data successfully transferred from {source_config[0]}::{source_config[3]} to {dest_config[0]}::{dest_config[3]}.")

        except subprocess.CalledProcessError as err:
            self.logger.error(f"Subprocess Error: {err}")
        except paramiko.SSHException as ssh_err:
            self.logger.error(f"SSH Error: {ssh_err}")
        except Exception as err:
            self.logger.error(f"Unexpected Error: {err}")

        finally:
            # Clean up dump file
            if os.path.exists(dump_file_path):
                os.remove(dump_file_path)
                self.logger.info("Dump file cleaned up.")

        self.logger.info("Dumping data to database process completed.")

