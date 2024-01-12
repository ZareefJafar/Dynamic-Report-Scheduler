# Dynamic-Report-Scheduler

### Test environment:

OS: Ubuntu 20.04.6 LTS\
Python version:  3.11.5\
Databases: SQLite3 (for credentials and queries) , PostgreSQL (reports data)

### Sample Report database:
[DVD rental database](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/)


### Libraries:
[APScheduler](https://github.com/agronholm/apscheduler) 3.10.4\
[pycryptodome](https://github.com/Legrandin/pycryptodome) : For AES-256 Encryption and Decryption.\
[pycrypto](https://anaconda.org/anaconda/pycrypto)

The sample scheduler can generate reports everyday in the specified time. PostgreSQL is being used to store data for reports. In SQLite3 credential of senders mail, credential of PostgreSQL,  list of receiver mails, subject text, body text in html format, stored procedures are stored.\
Optional: AES-256 based encrypt and decryptfor some sensitive credentials. 


creating ```reports``` table in SQLite:

```
CREATE TABLE reports(id text, report_name text, database_type text, ip_port text,database_creds text,sender_creds text,to_mail text, cc text, bcc TEXT, subject text, body text,date_time text, query text);
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