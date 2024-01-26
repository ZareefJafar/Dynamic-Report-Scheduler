# Dynamic-Report-Scheduler

Scheduling report generation and automatic delivery.


### Test environment:

**OS**:              Ubuntu 20.04.6 LTS\
**Python version**:  3.11.5\
**SQLite3**:         For credentials and queries. No need for a separate setup. 
                     Comes with python by default.  
                     Need a GUI tool like [DB Browser](https://sqlitebrowser.org/) for editing SQLite.\
**PostgreSQL, MySQL, Microsoft SQL Server**:      For report data

### Sample Report database:
[DVD rental database](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/)


### Libraries:
[APScheduler](https://github.com/agronholm/apscheduler) 3.11.5\
[pycrypto](https://anaconda.org/anaconda/pycrypto) : For AES-256 Encryption and Decryption.


```
conda create --name sched python=3.11.5
```
```
conda activate sched
```
```
conda install -c conda-forge apscheduler pyodbc psycopg2 mysql-connector-python pandas pysftp
```
Features:
* Extracts unique specifications for report generation tasks from a centralized SQLite3 table.
* Dynamically creates and schedules jobs based on extracted specifications.
* Generate reports and send them via email.
* Uploloading reports to SFTP servers.
* Optional AES-256 based encrypt and decrypt for some sensitive credentials.
* Can pool data from an unlimited number of database servers.


Upcoming features:
* Instructions for monthly, yearly, weekly, and more custom intervals.




creating ```reports``` table of ```creads.db``` SQLite database:

```
CREATE TABLE "reports" (
	"id"	text,
	"report_name"	text,
	"database_type"	text,
	"ip_port"	text,
	"database_creds"	text,
	"sender_creds"	text,
	"sender_type"	TEXT,
	"receiver_creds"	TEXT,
	"receiver_type"	TEXT,
	"to_mail"	text,
	"cc"	text,
	"bcc"	TEXT,
	"subject"	text,
	"body"	text,
	"date_time"	text,
	"query"	text,
	"active"	TEXT
)
```


### Reports table attributes
```
id -             {id of report}
report_name -    {genrated report file name}
database_type -  {type of database. e.g. postgresql, mssql, mysql where report data is stored}
ip_port -        {ip and port of database server. e.g. 127.0.0.1,5432}
database_creds - {username,password,database_name}
sender_creds -   {gmail_id,Gmail_App_Password}
receiver_creds	 {sftp_ip,user_name,sftp_password,save_location},
receiver_type -  {mail/sftp server/sms/......}
to_mail -        {mail_id1,mail_id2,mail_id3.....}
cc -             {mail_id1,mail_id2,mail_id3.....}
bcc -            {mail_id1,mail_id2,mail_id3.....}
subject -        {subject text}
body -           {body in html}
date_time -      {trigger date time}
query -          {sql query for report/Stored Procedures}
active -         {0 for inactive and 1 for active}
```

If you want to contribute please read the CONTRIBUTING.md