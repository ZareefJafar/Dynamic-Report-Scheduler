from time import sleep
from apscheduler.schedulers.background import BlockingScheduler
import sqlite3
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import psycopg2
import psycopg2.extras
import datetime
import pandas as pd
import base64
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib





def decrypt(password, cipher_message):
    IV_LENGTH = 12
    SALT_LENGTH = 16
    TAG_LENGTH = 16
    decoded_cipher_byte = base64.b64decode(cipher_message)

    salt = decoded_cipher_byte[:SALT_LENGTH]
    iv = decoded_cipher_byte[SALT_LENGTH : (SALT_LENGTH + IV_LENGTH)]
    encrypted_message_byte = decoded_cipher_byte[
        (IV_LENGTH + SALT_LENGTH) : -TAG_LENGTH
    ]
    tag = decoded_cipher_byte[-TAG_LENGTH:]
    secret = get_secret_key(password, salt)
    cipher = AES.new(secret, AES.MODE_GCM, iv)

    decrypted_message_byte = cipher.decrypt_and_verify(encrypted_message_byte, tag)
    return decrypted_message_byte.decode("utf-8")


def get_secret_key(password, salt):
    HASH_NAME = "SHA512"
    ITERATION_COUNT = 65535
    KEY_LENGTH = 32
    return hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode(), salt, ITERATION_COUNT, KEY_LENGTH
    )



sched = BlockingScheduler()

def report(unlockKey, record):


    Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
    Previous_Date_Formatted = Previous_Date.strftime ('%Y%m%d') # format the date to ddmmyyyy

    
    server_creds = decrypt(unlockKey, record['ip_port']).split(',')     



    print("SERVER: ",server_creds)
    database_creds = record['database_creds'].split(',')
    sender_creds = decrypt(unlockKey,record['sender_creds']).split(',')
    to_list = record['to_mail']
    cc_list = record['cc']
    bcc_list = record['bcc']
    report_name = record['report_name']+'_'+Previous_Date_Formatted+'.csv'
    query = record['query']



    sender_address = sender_creds[0]
    password =sender_creds[1]
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
    f = open('/home/sched/projects/Dynamic-Report-Scheduler-main/'+ report_name , 'w')
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





    attachment = open('/home/sched/projects/Dynamic-Report-Scheduler-main/'+ report_name , "rb")


    obj = MIMEBase('application','octet-stream')
    name=report_name
    print(name)
    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition',"attachment",filename=name)

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


    print("YOUR MAIL HAS BEEN SENT SUCCESSFULLY")










if __name__ == '__main__':
    key = input("Enter pass: ")


    rec={}

    try:
        

        
        db = sqlite3.connect("creds.db")
        curCreds = db.cursor()
        res = curCreds.execute("select * from reports").fetchall()
        rec = dict(zip([c[0] for c in curCreds.description], res[0]))
        print(rec)
        curCreds.close()



    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from Database", error)

    sched.add_job(report, 'cron', hour='13', minute= '45', args=(key,rec,))

    sched.start()