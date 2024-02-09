import datetime
import os
from pathlib import Path
import logging
import pysftp
import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from pathlib import Path

class Sftp:
    def __init__(self, record,created_folder_path):
        self.connection = None
        self.record = record
        self.created_folder_path = created_folder_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

    def connect(self, hostname, username, password, port):
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None 

            self.connection = pysftp.Connection(
                host=hostname,
                username=username,
                password=password,
                port=int(port),
                cnopts=cnopts
            )
        except Exception as err:
            raise Exception(err)

    def listdir(self, remote_path):
        return self.connection.listdir(remote_path)

    def listdir_attr(self, remote_path):
        return self.connection.listdir_attr(remote_path)

    def download(self, hostname, username, remote_path, target_local_path):
        try:
            path, _ = os.path.split(target_local_path)
            Path(path).mkdir(parents=True, exist_ok=True)
            self.connection.get(remote_path, target_local_path)
            print("Download completed")

        except Exception as err:
            raise Exception(err)

    def upload(self, hostname, username, source_local_path, remote_path):
        try:
            self.connection.put(source_local_path, remote_path)

        except Exception as err:
            raise Exception(err)
        
    def append_or_create_file(self, file_path, line):
        file_path = Path(file_path)

        # Use 'x' flag to open the file for exclusive creation
        with file_path.open(mode='a' if file_path.exists() else 'x') as file:
            file.write(line + '\n')

    def sftp_upload(self):
        Current_Date = datetime.datetime.today()
        Current_Date_Formatted = Current_Date.strftime("%Y/%m/%d, %H:%M:%S")
        Current_Date_Formatted_for_list_file = Current_Date.strftime('%Y%m%d')
        Previous_Date = Current_Date - datetime.timedelta(days=1)
        Previous_Date_Formatted = Previous_Date.strftime('%Y%m%d')

        server_creds = self.record['ip_port'].split(',')
        database_creds = self.record['database_creds'].split(',')
        report_name = f"{self.record['report_name']}_{Previous_Date_Formatted}.csv"
        query = self.record['query']

        databaseType = self.record["database_type"].lower()

        # Database connection
        db_uri = None
        engine = None
        conn = None


        try:
            if databaseType == "postgresql":
                db_uri = (
                    f"postgresql://{database_creds[0]}:{database_creds[1]}@"
                    f"{server_creds[0]}:{server_creds[1]}/{database_creds[2]}"
                )
                engine = create_engine(db_uri)

            elif databaseType == "mssql":
                params = quote_plus(
                    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                    f"SERVER={server_creds[0]},{server_creds[1]};"
                    f"DATABASE={database_creds[2]};"
                    f"UID={database_creds[0]};"
                    f"PWD={database_creds[1]};"
                    "Encrypt=yes;"
                    "TrustServerCertificate=yes;"  # Disable SSL certificate check
                    "Connection Timeout=30;"
                )
                engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

            elif databaseType == "mysql":
                db_uri = (
                    f"mysql+mysqlconnector://{database_creds[0]}:{database_creds[1]}@"
                    f"{server_creds[0]}:{server_creds[1]}/{database_creds[2]}"
                )
                engine = create_engine(db_uri)


        
            conn = engine.connect()


            df = pd.read_sql_query(query, conn)

            file_path = Path(self.created_folder_path) / report_name
            df.to_csv(file_path, header=True, index=False, mode='w')
            # print(f"{report_name} created")

            sftp_creds = self.record['receiver_creds'].split(',')
            hostname, port, username, password = sftp_creds[0], sftp_creds[1], sftp_creds[2],sftp_creds[3]

            self.connect(hostname, username, password, port)
            
            with self.connection:
                local_path = Path(self.created_folder_path) / report_name
                remote_path = sftp_creds[4] + report_name
                self.upload(hostname, username, local_path, remote_path)

            report_list_name = f"A_reportList_{Current_Date_Formatted_for_list_file}.txt"
            report_list_file_path = os.path.join(self.created_folder_path, report_list_name)
            message = f"{Current_Date_Formatted} {report_name} REPORT Uploaded SUCCESSFULLY"
            self.append_or_create_file(report_list_file_path,message)
            print(message)

        except Exception as e:
            logging.error(f"Error: {e}")