from time import sleep
from apscheduler.schedulers.background import BlockingScheduler
import sqlite3
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import psycopg2
import psycopg2.extras
import pyodbc
import mysql.connector
from mysql.connector import Error
import datetime
import pandas as pd
import base64
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib
import pysftp
from urllib.parse import urlparse
import os


def decrypt(password, cipher_message):
    IV_LENGTH = 12
    SALT_LENGTH = 16
    TAG_LENGTH = 16
    decoded_cipher_byte = base64.b64decode(cipher_message)

    salt = decoded_cipher_byte[:SALT_LENGTH]
    iv = decoded_cipher_byte[SALT_LENGTH: (SALT_LENGTH + IV_LENGTH)]
    encrypted_message_byte = decoded_cipher_byte[
        (IV_LENGTH + SALT_LENGTH): -TAG_LENGTH
    ]
    tag = decoded_cipher_byte[-TAG_LENGTH:]
    secret = get_secret_key(password, salt)
    cipher = AES.new(secret, AES.MODE_GCM, iv)

    decrypted_message_byte = cipher.decrypt_and_verify(
        encrypted_message_byte, tag)
    return decrypted_message_byte.decode("utf-8")


def get_secret_key(password, salt):
    HASH_NAME = "SHA512"
    ITERATION_COUNT = 65535
    KEY_LENGTH = 32
    return hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode(), salt, ITERATION_COUNT, KEY_LENGTH
    )


sched = BlockingScheduler()


def report_pass(unlockKey, record):

    Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
    Previous_Date_Formatted = Previous_Date.strftime(
        '%Y%m%d')  # format the date to ddmmyyyy

    server_creds = decrypt(unlockKey, record['ip_port']).split(',')

    database_creds = record['database_creds'].split(',')
    sender_creds = decrypt(unlockKey, record['sender_creds']).split(',')
    to_list = record['to_mail']
    cc_list = record['cc']
    bcc_list = record['bcc']
    report_name = record['report_name']+'_'+Previous_Date_Formatted+'.csv'
    query = record['query']

    sender_address = sender_creds[0]
    password = sender_creds[1]
    to = to_list
    cc = cc_list
    bcc = bcc_list

    conn = psycopg2.connect(
        host=server_creds[0],
        database=database_creds[2],
        user=database_creds[0],
        password=database_creds[1],
        port=server_creds[1])

    # Open the file
    f = open('/home/sched/projects/Dynamic-Report-Scheduler-main/' +
             report_name, 'w')
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

    message = MIMEMultipart("")
    message["Subject"] = record['subject']
    message["From"] = sender_address
    message["To"] = to
    message['Cc'] = cc
    message['Bcc'] = bcc

    # Create the HTML version of your message
    html = record['body']

    # Create both plain and HTML text objects
    body = MIMEText(html, "html")

    attachment = open(
        '/home/sched/projects/Dynamic-Report-Scheduler-main/' + report_name, "rb")

    obj = MIMEBase('application', 'octet-stream')
    name = report_name
    print("Generated ", name)
    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition', "attachment", filename=name)

    message.attach(obj)

    # Attach both versions to the outgoing message
    message.attach(body)

    # Send the email with your SMTP server
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_address, password)
        server.sendmail(
            sender_address, to, message.as_string()
        )

    print(name, "REPORT HAS BEEN SENT SUCCESSFULLY")


def report(record):

    Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
    Previous_Date_Formatted = Previous_Date.strftime(
        '%Y%m%d')  # format the date to ddmmyyyy

    server_creds = record['ip_port'].split(',')
    database_creds = record['database_creds'].split(',')
    sender_creds = record['sender_creds'].split(',')
    to = record['to_mail']
    cc = record['cc']
    bcc = record['bcc']
    report_name = record['report_name']+'_'+Previous_Date_Formatted+'.csv'
    query = record['query']

    sender_address = sender_creds[0]
    password = sender_creds[1]

    databaseType = record["database_type"].lower()

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

    message = MIMEMultipart("")
    message["Subject"] = record['subject']
    message["From"] = sender_address
    message["To"] = to
    message['Cc'] = cc
    message['Bcc'] = bcc

    # Create the HTML version of your message
    html = record['body']

    # Create both plain and HTML text objects
    body = MIMEText(html, "html")

    attachment = open(
        '/home/zareef/projects/reportScheduler/reports/' + report_name, "rb")

    obj = MIMEBase('application', 'octet-stream')
    name = report_name
    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition', "attachment", filename=name)

    message.attach(obj)

    # Attach both versions to the outgoing message
    message.attach(body)

    to_list = []
    cc_list = []
    bcc_list = []
    if to != None:
        to_list = to.split(',')
    if cc != None:
        cc_list = cc.split(',')
    if bcc != None:
        bcc_list = bcc.split(',')
    toAddress = to_list + cc_list + bcc_list

    # Send the email with your SMTP server
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_address, password)
        server.sendmail(
            sender_address, toAddress, message.as_string()
        )

    print(name, " REPORT HAS BEEN SENT SUCCESSFULLY")


class Sftp:
    def __init__(self, hostname, username, password, port=22):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.connection = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        try:
            # Get the sftp connection object
            self.connection = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
            )
        except Exception as err:
            raise Exception(err)
        finally:
            print(f"Connected to {self.hostname} as {self.username}.")

    def disconnect(self):
        """Closes the sftp connection"""
        self.connection.close()
        print(f"Disconnected from host {self.hostname}")

    def listdir(self, remote_path):
        """lists all the files and directories in the specified path and returns them"""
        for obj in self.connection.listdir(remote_path):
            yield obj

    def listdir_attr(self, remote_path):
        """lists all the files and directories (with their attributes) in the specified path and returns them"""
        for attr in self.connection.listdir_attr(remote_path):
            yield attr

    def download(self, remote_path, target_local_path):
        """
        Downloads the file from remote sftp server to local.
        Also, by default extracts the file to the specified target_local_path
        """

        try:
            print(
                f"downloading from {self.hostname} as {self.username} [(remote path : {remote_path});(local path: {target_local_path})]"
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

    def upload(self, source_local_path, remote_path):
        """
        Uploads the source files from local to the sftp server.
        """

        try:
            print(
                f"uploading to {self.hostname} as {self.username} [(remote path: {remote_path});(source local path: {source_local_path})]"
            )

            # Download file from SFTP
            self.connection.put(source_local_path, remote_path)
            print("upload completed")

        except Exception as err:
            raise Exception(err)
        

def sftp_upload(record):


    Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
    Previous_Date_Formatted = Previous_Date.strftime(
        '%Y%m%d')  # format the date to ddmmyyyy

    server_creds = record['ip_port'].split(',')
    database_creds = record['database_creds'].split(',')
    report_name = record['report_name']+'_'+Previous_Date_Formatted+'.csv'
    query = record['query']


    databaseType = record["database_type"].lower()

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

    sftp_creds = record['receiver_creds'].split(',')

    sftp = Sftp(
        hostname=sftp_creds[0],
        username=sftp_creds[1],
        password=sftp_creds[2],
    )

    # Connect to SFTP
    sftp.connect()

    # Lists files with attributes of SFTP
    path = "/"
    print(f"List of files with attributes at location {path}:")
    for file in sftp.listdir_attr(path):
        print(file.filename, file.st_mode, file.st_size, file.st_atime, file.st_mtime)

    # Upload files to SFTP location from local
    local_path = '/home/zareef/projects/reportScheduler/reports/' + report_name
    remote_path = sftp_creds[3]+report_name
    sftp.upload(local_path, remote_path)

    # Lists files of SFTP location after upload
    print(f"List of files at location {path}:")
    print([f for f in sftp.listdir(path)])

    # Download files from SFTP
    # sftp.download(
    #     remote_path, os.path.join(remote_path, local_path + '.backup')
    # )

    # Disconnect from SFTP
    sftp.disconnect()
        

if __name__ == '__main__':
    key = input(
        "Enter password if credentials are encrypted (press ENTER otherwise): ")
    print("Dynamic-Report-Scheduler running..........\n")

    try:

        db = sqlite3.connect("creads.db")
        curCreds = db.cursor()
        res = curCreds.execute("select * from reports").fetchall()

        curCreds.close()

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from Database", error)

    for i in range(len(res)):
        job_args = dict(zip([c[0] for c in curCreds.description], res[i]))
        if(job_args['receiver_type']=='email'):
            sched.add_job(report, 'cron',
                        hour=job_args['date_time'].split(',')[0],
                        minute=job_args['date_time'].split(',')[1],
                        args=(job_args,))
        elif(job_args['receiver_type']=='sftp'):
            sched.add_job(sftp_upload, 'cron',
                hour=job_args['date_time'].split(',')[0],
                minute=job_args['date_time'].split(',')[1],
                args=(job_args,))

    sched.start()
