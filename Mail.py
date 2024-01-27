from time import sleep
from apscheduler.schedulers.background import BlockingScheduler
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from sqlalchemy import create_engine
import pandas as pd
import datetime
from urllib.parse import quote_plus

class Mail:
    def __init__(self, record):
        self.record = record

    def email_dispatch(self):
        Current_Date = datetime.datetime.today()
        Current_Date_Formatted = Current_Date.strftime("%Y/%m/%d, %H:%M:%S")
        Previous_Date = Current_Date - datetime.timedelta(days=1)
        Previous_Date_Formatted = Previous_Date.strftime('%Y%m%d')

        server_creds = self.record['ip_port'].split(',')
        database_creds = self.record['database_creds'].split(',')
        sender_creds = self.record['sender_creds'].split(',')
        to = self.record['to_mail']
        cc = self.record['cc']
        bcc = self.record['bcc']
        report_name = f"{self.record['report_name']}_{Previous_Date_Formatted}.csv"
        query = self.record['query']

        sender_address = sender_creds[0]
        password = sender_creds[1]

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
        

            # Execute the query and directly read the result into a DataFrame
            df = pd.read_sql_query(query, conn)

            # Open the file
            file_path = os.path.join('/home/zareef/projects/reportScheduler/reports/', report_name)

            # Save the DataFrame to a CSV file
            df.to_csv(file_path, header=True, index=False, mode='w')

            # print(report_name, " CREATED")

            # Sending email code...
            
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


            if self.record['sender_type']=='gmail':
                host = "smtp.gmail.com"
                port = 465
                
                # Send the email with your SMTP server
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(host, port, context=context) as server:
                    server.login(sender_address, password)
                    server.sendmail(
                        sender_address, toAddress, message.as_string()
                    )

            elif self.record['sender_type']=='outlook':
                host = "smtp.office365.com"
                port = 587

                # Connect to the SMTP server and send the email
                context = ssl.create_default_context()

                with smtplib.SMTP(host, port) as server:
                    server.starttls(context=context)  # Use starttls for a secure connection
                    server.login(sender_address, password)
                    server.sendmail(sender_address, toAddress, message.as_string())

            
            print(f"\n{Current_Date_Formatted} {report_name} REPORT MAILED SUCCESSFULLY")


        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the database connection
            if conn:
                conn.close()

                
