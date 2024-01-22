
from time import sleep
from apscheduler.schedulers.background import BlockingScheduler
import pyodbc
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
from Sftp import Sftp


class Mail:
    def __init__(self, record):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.record = record



    def email_dispatch (self):

        Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
        Previous_Date_Formatted = Previous_Date.strftime(
            '%Y%m%d')  # format the date to ddmmyyyy

        server_creds = self.record['ip_port'].split(',')
        database_creds = self.record['database_creds'].split(',')
        sender_creds = self.record['sender_creds'].split(',')
        to = self.record['to_mail']
        cc = self.record['cc']
        bcc = self.record['bcc']
        report_name = self.record['report_name']+'_'+Previous_Date_Formatted+'.csv'
        query = self.record['query']

        sender_address = sender_creds[0]
        password = sender_creds[1]

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

        message = MIMEMultipart("")
        message["Subject"] = self.record['subject']
        message["From"] = sender_address
        message["To"] = to
        message['Cc'] = cc
        message['Bcc'] = bcc

        # Create the HTML version of your message
        html = self.record['body']

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
