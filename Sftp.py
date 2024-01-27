import datetime
import os
from pathlib import Path
import logging
import pysftp
import pandas as pd
from sqlalchemy import create_engine

class Sftp:
    def __init__(self, record):
        self.connection = None
        self.record = record

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

    def connect(self, hostname, username, password, port=22):
        try:
            self.connection = pysftp.Connection(
                host=hostname,
                username=username,
                password=password,
                port=port,
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

    def upload(self, source_local_path, remote_path):
        try:
            self.connection.put(source_local_path, remote_path)

        except Exception as err:
            raise Exception(err)

    def sftp_upload(self):
        Current_Date = datetime.datetime.today()
        Current_Date_Formatted = Current_Date.strftime("%Y/%m/%d, %H:%M:%S")
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
            elif databaseType == "mssql":
                db_uri = (
                    f"mssql+pyodbc://{database_creds[0]}:{database_creds[1]}@"
                    f"{server_creds[0]}:{server_creds[1]}/{database_creds[2]}?"
                    "driver=ODBC+Driver+18+for+SQL+Server;"
                    "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
                )
            elif databaseType == "mysql":
                db_uri = (
                    f"mysql+mysqlconnector://{database_creds[0]}:{database_creds[1]}@"
                    f"{server_creds[0]}:{server_creds[1]}/{database_creds[2]}"
                )

            engine = create_engine(db_uri)
            conn = engine.connect()


            df = pd.read_sql_query(query, conn)

            file_path = Path('/home/zareef/projects/reportScheduler/reports') / report_name
            df.to_csv(file_path, header=True, index=False, mode='w')
            # print(f"{report_name} created")

            sftp_creds = self.record['receiver_creds'].split(',')
            hostname, username, password = sftp_creds[0], sftp_creds[1], sftp_creds[2]

            self.connect(hostname, username, password)
            
            with self.connection:
                local_path = Path('/home/zareef/projects/reportScheduler/reports') / report_name
                remote_path = sftp_creds[3] + report_name
                self.upload(hostname, username, local_path, remote_path)

            print(f"\n{Current_Date_Formatted} {report_name} REPORT UPLOADED SUCCESSFULLY")

        except Exception as e:
            logging.error(f"Error: {e}")
