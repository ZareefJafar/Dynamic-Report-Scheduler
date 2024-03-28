from time import sleep
from apscheduler.schedulers.background import BlockingScheduler
import sqlite3
from urllib.parse import urlparse
from Sftp import Sftp
from Mail import Mail  # Assuming you have Mail class in Mail module
from pathlib import Path
from DatabaseDump import DatabaseDump
import calendar
from datetime import datetime, timedelta
from logger_config import setup_logger



if __name__ == '__main__':

    logger = setup_logger()

    # Log an info message
    logger.info("Dynamic-Report-Scheduler running..........\n")
    # print("Dynamic-Report-Scheduler running..........\n")

    sched = BlockingScheduler()

    def create_folder(folder_name):
        # Get the parent directory
        parent_directory = Path.cwd().parent
        
        # Create the full path for the new folder in the parent directory
        folder_path = parent_directory / folder_name
        
        # Create the folder if it doesn't exist
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Check if the folder already exists
        if folder_path.is_dir():
            status = "already exists"
        else:
            # Create the folder if it doesn't exist
            folder_path.mkdir(parents=True, exist_ok=True)
            status = "created"

        logger.info(f"Folder '{folder_name}' {status} at: {folder_path}")
        
        # Return the folder path
        return folder_path

    try:
        db = sqlite3.connect("creads.db")
        curCreds = db.cursor()
        res = curCreds.execute("select * from reports").fetchall()

        # Get column names from the table
        column_names = [description[0] for description in curCreds.description]

    except (Exception, sqlite3.Error) as error:
        logger.info("Error while fetching data from Database", error)
        res = []  # Set res to an empty list in case of an error
        column_names = []  # Set column_names to an empty list

    folder_name = "report_repository"
    created_folder_path = create_folder(folder_name)

    for i in range(len(res)):
        job_args = dict(zip(column_names, res[i]))
        if job_args['active'] == '1':
            logger.info("Active report id: %s", job_args['id'])
            if job_args['receiver_type'] == 'email' and job_args['frequency'] == 'daily':
                mail_instance = Mail(job_args,created_folder_path)
                sched.add_job(mail_instance.email_dispatch, 'cron',
                            hour=job_args['date_time'].split(',')[0],
                            minute=job_args['date_time'].split(',')[1])
                
                

            elif job_args['receiver_type'] == 'sftp'and job_args['frequency'] == 'daily':
                sftp_instance = Sftp(job_args,created_folder_path)
                sched.add_job(sftp_instance.sftp_upload, 'cron',
                            hour=job_args['date_time'].split(',')[0],
                            minute=job_args['date_time'].split(',')[1])
                
                

            elif job_args['receiver_type'] == 'data_dump'and job_args['frequency'] == 'daily':
                # Create a new instance of DatabaseDump for each data_dump job
                db_dump = DatabaseDump(job_args)
                sched.add_job(db_dump.dump_to_database, 'cron',
                            hour=job_args['date_time'].split(',')[0],
                            minute=job_args['date_time'].split(',')[1])
                

                
            elif job_args['receiver_type'] == 'email'and job_args['frequency'] == 'monthly':
                # Create a new instance of DatabaseDump for each data_dump job
                mail_instance = Mail(job_args,created_folder_path)

                sched.add_job(mail_instance.email_dispatch, 'cron',
                            day=job_args['date_time'].split(',')[0],
                            hour=job_args['date_time'].split(',')[1],
                            minute=job_args['date_time'].split(',')[2])

    sched.start()