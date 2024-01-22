from time import sleep
from apscheduler.schedulers.background import BlockingScheduler
import sqlite3
from urllib.parse import urlparse
from Sftp import Sftp
from Mail import Mail  # Assuming you have Mail class in Mail module



if __name__ == '__main__':
    key = input(
        "Enter password if credentials are encrypted (press ENTER otherwise): ")
    print("Dynamic-Report-Scheduler running..........\n")
    sched = BlockingScheduler()

    try:
        db = sqlite3.connect("creads.db")
        curCreds = db.cursor()
        res = curCreds.execute("select * from reports").fetchall()

        # Get column names from the table
        column_names = [description[0] for description in curCreds.description]

    except (Exception, sqlite3.Error) as error:
        print("Error while fetching data from Database", error)
        res = []  # Set res to an empty list in case of an error
        column_names = []  # Set column_names to an empty list

    for i in range(len(res)):
        job_args = dict(zip(column_names, res[i]))

        if job_args['receiver_type'] == 'email':
            mail_instance = Mail(job_args)
            sched.add_job(mail_instance.email_dispatch, 'cron',
                          hour=job_args['date_time'].split(',')[0],
                          minute=job_args['date_time'].split(',')[1])

        elif job_args['receiver_type'] == 'sftp':
            sftp_instance = Sftp(job_args)
            sched.add_job(sftp_instance.sftp_upload, 'cron',
                          hour=job_args['date_time'].split(',')[0],
                          minute=job_args['date_time'].split(',')[1])

    sched.start()
