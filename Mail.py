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
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from pathlib import Path
from sqlalchemy.sql import text
import calendar
from datetime import datetime, timedelta
from logger_config import setup_logger




class Mail:
    def __init__(self, record,created_folder_path):
        self.record = record
        self.created_folder_path = created_folder_path
        self.logger = setup_logger()

    def append_or_create_file(self, file_path, line):
        file_path = Path(file_path)

        # Use 'x' flag to open the file for exclusive creation
        with file_path.open(mode='a' if file_path.exists() else 'x') as file:
            file.write(line + '\n')


    def email_dispatch(self):
        Current_Date = datetime.today()
        Current_Date_Formatted = Current_Date.strftime("%Y/%m/%d, %H:%M:%S")
        Current_Date_Formatted_for_list_file = Current_Date.strftime('%Y%m%d')
        Previous_Date = Current_Date - timedelta(days=1)
        Previous_Date_Formatted = Previous_Date.strftime('%Y%m%d')
        Previous_Date_Formatted_subject = Previous_Date.strftime("%d %B %Y")

        server_creds = self.record['ip_port'].split(',')
        database_creds = self.record['database_creds'].split(',')
        sender_creds = self.record['sender_creds'].split(',')
        to = self.record['to_mail']
        cc = self.record['cc']
        bcc = self.record['bcc']
        message = MIMEMultipart("")

        if self.record['frequency'] == 'monthly':
    
            # Get the current date
            current_date = datetime.now()

            # Calculate the first day of the current month
            first_day_of_current_month = current_date.replace(day=1)

            # Calculate the last day of the previous month
            last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

            # Get the name and year of the previous month
            previous_month_name = calendar.month_name[last_day_of_previous_month.month]
            previous_month_year = last_day_of_previous_month.year
            report_name = f"{self.record['report_name']}_{previous_month_name}{previous_month_year}.csv"
            message["Subject"] = f"{self.record['subject']} of {previous_month_name} {previous_month_year}"
        else:
            report_name = f"{self.record['report_name']}_{Previous_Date_Formatted}.csv"
            message["Subject"] = f"{self.record['subject']} of {Previous_Date_Formatted_subject}"

        self.logger.info(f"Starting {report_name} process..")
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
        
            if self.record['body'] == 'by_sql':
                query = text(query)
                
                result = conn.execute(query)
    
                html = result.scalar()
            else:
            # Execute the query and directly read the result into a DataFrame
                df = pd.read_sql_query(query, conn)

                # Open the file
                file_path = os.path.join(self.created_folder_path,  str(report_name))

                # Save the DataFrame to a CSV file
                df.to_csv(file_path, header=True, index=False, mode='w')

                # Create the HTML version of your message
                html = self.record['body']

            self.logger.info(f"{report_name} created")

            # Sending email code...
            
            
            message["From"] = sender_address
            message["To"] = to
            message['Cc'] = cc
            message['Bcc'] = bcc

            # Create the HTML version of your message
            # html = self.record['body']

            # Create both plain and HTML text objects
            body = MIMEText(html, "html")

            if self.record['body'] != 'by_sql':
                attachment = open(os.path.join(str(self.created_folder_path), report_name), "rb")

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

            max_retries = 1
            retry_count = 0
            sent_successfully = False

            while not sent_successfully and retry_count < max_retries:
                try:
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
                    report_list_name = f"A_reportList_{Current_Date_Formatted_for_list_file}.txt"
                    report_list_file_path = os.path.join(self.created_folder_path, report_list_name)
                    success_message  = f"{Current_Date_Formatted} {report_name} REPORT MAILED SUCCESSFULLY"
                    log_message  = f"{report_name} REPORT MAILED SUCCESSFULLY"
                    # self.append_or_create_file(report_list_file_path,success_message)
                    sent_successfully = True
                    self.logger.info(log_message)

                except smtplib.SMTPException as smtp_exception:
                    self.logger.info(f"SMTP Exception: {smtp_exception}")
                    retry_count += 1
                    self.logger.info(f"{report_name} mail sending failed. Retrying ({retry_count}/{max_retries}) after 2 seconds...")
                    sleep(2)

                except Exception as e:
                    self.logger.info(f"Mail Error: {e}")
                    retry_count += 1
                    self.logger.info(f"{report_name} mail sending failed. Retrying ({retry_count}/{max_retries}) after 2 seconds...")
                    sleep(2)


        except Exception as e:
            self.logger.error(f"Error: {e}")
        finally:
            # Close the database connection
            if conn:
                conn.close()

                