import psycopg2
import psycopg2.extras
import mysql.connector
import datetime
import pandas as pd
import pysftp
import os
import pyodbc


class Sftp:
    def __init__(self,record):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.connection = None
        self.record = record

    def connect(self,hostname,username,password,port=22):
        """Connects to the sftp server and returns the sftp connection object"""

        try:
            # Get the sftp connection object
            self.connection = pysftp.Connection(
                host=hostname,
                username=username,
                password=password,
                port=port,
            )
        except Exception as err:
            raise Exception(err)
        finally:
            print(f"Connected to {hostname} as {username}.")

    def disconnect(self, hostname):
        """Closes the sftp connection"""
        self.connection.close()
        print(f"Disconnected from host {hostname}")

    def listdir(self, remote_path):
        """lists all the files and directories in the specified path and returns them"""
        for obj in self.connection.listdir(remote_path):
            yield obj

    def listdir_attr(self, remote_path):
        """lists all the files and directories (with their attributes) in the specified path and returns them"""
        for attr in self.connection.listdir_attr(remote_path):
            yield attr

    def download(self, hostname, username, remote_path, target_local_path):
        """
        Downloads the file from remote sftp server to local.
        Also, by default extracts the file to the specified target_local_path
        """

        try:
            print(
                f"downloading from {hostname} as {username} [(remote path : {remote_path});(local path: {target_local_path})]"
            )

            # Create the target directory if it does not exist
            path, _ = os.path.split(target_local_path)
            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except Exception as err:
                    raise Exception(err)

            # Download from remote sftp server to local
            self.connection.get(remote_path, target_local_path)
            print("download completed")

        except Exception as err:
            raise Exception(err)

    def upload(self, hostname,username,source_local_path, remote_path):
        """
        Uploads the source files from local to the sftp server.
        """

        try:
            print(
                f"uploading to {hostname} as {username} [(remote path: {remote_path});(source local path: {source_local_path})]"
            )

            # Download file from SFTP
            self.connection.put(source_local_path, remote_path)
            print("upload completed")

        except Exception as err:
            raise Exception(err)
        
    def sftp_upload(self):


        Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
        Previous_Date_Formatted = Previous_Date.strftime(
            '%Y%m%d')  # format the date to ddmmyyyy

        server_creds = self.record['ip_port'].split(',')
        database_creds = self.record['database_creds'].split(',')
        report_name = self.record['report_name']+'_'+Previous_Date_Formatted+'.csv'
        query = self.record['query']


        databaseType = self.record["database_type"].lower()

        match databaseType:
            case "postgresql":
                conn = psycopg2.connect(
                    host=server_creds[0],
                    database=database_creds[2],
                    user=database_creds[0],
                    password=database_creds[1],
                    port=server_creds[1])
            # case "mssql":
            #     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
            #             SERVER='+server_creds[0]+';\
            #             DATABASE='+database_creds[2]+';\
            #             UID='+database_creds[0]+';\
            #             PWD='+ database_creds[1])
                
            case "mysql":
                conn = mysql.connector.connect(host=server_creds[0],
                                            database=database_creds[2],
                                            user=database_creds[0],
                                            password=database_creds[1],
                                            port=server_creds[1])




        # Open the file
        f = open('/home/zareef/projects/reportScheduler/reports/' + report_name, 'w')
        # Create a connection and get a cursor
        curReport = conn.cursor()
        # Execute the query
        curReport.execute(query)
        # Get Header Names (without tuples)
        colnames = [desc[0] for desc in curReport.description]
        # Get data in batches
        while True:
            # Read the data
            df = pd.DataFrame(curReport.fetchall())
            # We are done if there are no data
            if len(df) == 0:
                break
            # Let us write to the file
            else:
                df.to_csv(f, header=colnames)

        # Clean up
        f.close()
        curReport.close()

        sftp_creds = self.record['receiver_creds'].split(',')

        
        hostname=sftp_creds[0]
        username=sftp_creds[1]
        password=sftp_creds[2]
        
        

        # Connect to SFTP
        self.connect(hostname,username,password)

        # Lists files with attributes of SFTP
        path = "/"
        print(f"List of files with attributes at location {path}:")
        for file in self.listdir_attr(path):
            print(file.filename, file.st_mode, file.st_size, file.st_atime, file.st_mtime)

        # Upload files to SFTP location from local
        local_path = '/home/zareef/projects/reportScheduler/reports/' + report_name
        remote_path = sftp_creds[3]+report_name
        self.upload(hostname,username, local_path, remote_path)

        # Lists files of SFTP location after upload
        print(f"List of files at location {path}:")
        print([f for f in self.listdir(path)])

        # Download files from SFTP
        # sftp.download(
        #     remote_path, os.path.join(hostname,username,remote_path, local_path + '.backup')
        # )

        # Disconnect from SFTP
        self.disconnect(hostname)
            
