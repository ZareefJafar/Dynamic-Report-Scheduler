from time import sleep
from apscheduler.schedulers.background import BlockingScheduler
import csv
import pymssql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import psycopg2
import itertools
import psycopg2.extras
import datetime





sched = BlockingScheduler()

def report():

    rec={}

    try:
        userName = input("Enter username:")
        userPassword = input("Enter user password:")
        ipAddress = input("Enter ip of the database:")
        port = input("Enter port:")
        databaseName = input("Enter database name:")
        tableName = input("Enter table name:")

        connection = psycopg2.connect(
                        user=(userName),
                        password=(userPassword),
                        host=(ipAddress),
                        port=(port),
                        database=(databaseName)
                        )

        dict_cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        credsQuery = "select * from "+ tableName +" where id="+1
        dict_cur.execute(credsQuery)
        rec = dict_cur.fetchone()


    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from Database", error)


       

    
    db_creds = rec['db_creds'].split(',')
    db_ip_port = rec['db_ip_port']
    conn = pymssql.connect(db_ip_port, db_creds[0], db_creds[1])
    cursor = conn.cursor()


    query = rec['sp']



    cursor.execute(query)
    print(cursor)

    

 
    Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
    Previous_Date_Formatted = Previous_Date.strftime ('%Y%m%d') # format the date to ddmmyyyy
    print ('Previous Date: ' + str(Previous_Date_Formatted))


    with open("/home/air/projects/scheduler/"+rec['report_name']+Previous_Date_Formatted+".csv", "w") as outfile:
        writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(col[0] for col in cursor.description)
        for row in cursor:
            writer.writerow(row)






    sender_creds=rec['sender_creds'].split(',')
    
    sender_email = sender_creds[0]
    receiver_email = rec['to_mail']

    message = MIMEMultipart()

    message["From"] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "Test report for new Report Scheduling System"


    html = rec['body']

    message.attach(MIMEText(html, 'html'))

    
    name=rec['report_name']+Previous_Date_Formatted+".csv"
    attachment = open("/home/air/projects/scheduler/" + name, "rb")


    obj = MIMEBase('application','octet-stream')

    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition',"attachment",filename=name)

    message.attach(obj)

    my_message = message.as_string()
    email_session = smtplib.SMTP(sender_creds[2],sender_creds[3])
    email_session.starttls()
    email_session.login(sender_email,sender_creds[1])

    email_session.sendmail(sender_email,receiver_email.split(','),my_message)
    email_session.quit()
    print("YOUR MAIL HAS BEEN SENT SUCCESSFULLY")





sched.add_job(report(), 'cron', hour='15', minute= '24')
sched.add_job(report(), 'cron', hour='13', minute= '24')

sched.start()
