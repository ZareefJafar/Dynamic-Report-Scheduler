from time import sleep
from apscheduler.schedulers.background import BlockingScheduler
import sqlite3
from urllib.parse import urlparse
from Sftp import Sftp
from Mail import Mail  # Assuming you have Mail class in Mail module
from pathlib import Path
from DatabaseDump import DatabaseDump



if __name__ == '__main__':
    key = input(
        "Enter password if credentials are encrypted (press ENTER otherwise): ")
    print("Dynamic-Report-Scheduler running..........\n")
    sched = BlockingScheduler()

    def create_folder(folder_name):
        # Get the parent directory
        parent_directory = Path.cwd().parent
        
        # Create the full path for the new folder in the parent directory
        folder_path = parent_directory / folder_name
        
        # Create the folder if it doesn't exist
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Display a message based on whether the folder was created or already exists
        status = "created" if folder_path.is_dir() else "already exists"
        print(f"Folder '{folder_name}' {status} at: {folder_path}")
        
        # Return the folder path
        return folder_path

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

    folder_name = "reports_repository"
    created_folder_path = create_folder(folder_name)

    for i in range(len(res)):
        job_args = dict(zip(column_names, res[i]))
        if job_args['active'] == '1':
            print("Active report id: "+job_args['id'])
            if job_args['receiver_type'] == 'email':
                mail_instance = Mail(job_args,created_folder_path)
                sched.add_job(mail_instance.email_dispatch, 'cron',
                            hour=job_args['date_time'].split(',')[0],
                            minute=job_args['date_time'].split(',')[1])

            elif job_args['receiver_type'] == 'sftp':
                sftp_instance = Sftp(job_args,created_folder_path)
                sched.add_job(sftp_instance.sftp_upload, 'cron',
                            hour=job_args['date_time'].split(',')[0],
                            minute=job_args['date_time'].split(',')[1])
            elif job_args['receiver_type'] == 'data_dump':
                # Create a new instance of DatabaseDump for each data_dump job
                db_dump = DatabaseDump(job_args)

                sched.add_job(db_dump.dump_to_database, 'cron',
                            hour=job_args['date_time'].split(',')[0],
                            minute=job_args['date_time'].split(',')[1])

    sched.start()
