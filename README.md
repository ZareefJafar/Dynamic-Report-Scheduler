# Dynamic-Report-Scheduler

### Test environment:

**OS**:              Ubuntu 20.04.6 LTS\
**Python version**:  3.11.5\
**SQLite3**:         For credentials and queries. No need for a separate setup. 
                     Comes with python by default.  
                     Need a GUI tool like [DB Browser](https://sqlitebrowser.org/) for editing SQLite.\
**PostgreSQL/MySQL**:      For report data

### Sample Report database:
[DVD rental database](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/)


### Libraries:
[APScheduler](https://github.com/agronholm/apscheduler) 3.11.5\
[pycrypto](https://anaconda.org/anaconda/pycrypto) : For AES-256 Encryption and Decryption.

Features:
* Extracts unique specifications for report generation tasks from a centralized SQLite3 table.
* Dynamically creates and schedules jobs based on extracted specifications.
* Optional AES-256 based encrypt and decrypt for some sensitive credentials.
* Can pool data from an unlimited number of database servers.


Upcoming features:
* Add options for Microsoft SQL Server for report data storage (PostgreSQL and MySQL are currently implemented and tested).
* Enable uploading and downloading reports from FTP and SFTP servers.
* Support for monthly, yearly, weekly, and custom intervals for enhanced task management.




creating ```reports``` table of ```creads.db``` SQLite database:

```
CREATE TABLE "reports" (
	"id"	text,
	"report_name"	text,
	"database_type"	text,
	"ip_port"	text,
	"database_creds"	text,
	"sender_creds"	text,
	"receiver_type"	TEXT,
	"to_mail"	text,
	"cc"	text,
	"bcc"	TEXT,
	"subject"	text,
	"body"	text,
	"date_time"	text,
	"query"	text
);
```


### Reports table attributes
```
id -             {id of report}
report_name -    {genrated report file name}
database_type -  {type of database. e.g. postgresql, mssql, mysql where report data is stored}
ip_port -        {ip and port of database server. e.g. 127.0.0.1,5432}
database_creds - {username,password,database_name}
sender_creds -   {gmail_id,Gmail_App_Password}
to_mail -        {mail_id1,mail_id2,mail_id3.....}
cc -             {mail_id1,mail_id2,mail_id3.....}
bcc -            {mail_id1,mail_id2,mail_id3.....}
subject -        {subject text}
body -           {body in html}
date_time -      {trigger date time}
query -          {sql query for report/Stored Procedures}

```

If you want to contribute please read the CONTRIBUTING.md