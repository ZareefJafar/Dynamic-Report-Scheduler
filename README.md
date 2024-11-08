# Dynamic-Report-Scheduler
Scheduling report generation and automatic delivery.

In financial institutions, daily and monthly reports are essential for reconciliation and operational oversight. Reconciliation is the process of verifying and matching financial records, such as transactions or balances, to ensure they are accurate and consistent across different systems or ledgers. This is a critical task for ensuring financial accuracy, detecting errors, and maintaining compliance.

Service-wise data, especially from the previous day or month, is frequently required for reconciliation to confirm that all transactions and balances align properly. The Dynamic Report Scheduler automates the generation and distribution of these reports, streamlining data delivery to various stakeholders and reducing manual workload.

### Features:

Data Source Management:

- Centralized SQLite3 table to store unique report generation specifications.
- Ability to pool data from multiple database servers seamlessly.

Dynamic Job Creation and Scheduling:

- Generates and schedules jobs based on extracted specifications.
- Supports both daily and monthly frequency for job execution.

Report Delivery Options:

- Dispatches reports as attachments via email.
- Offers the option to dispatch reports in the body of the email text.
- Facilitates uploading reports to SFTP servers.

Automated Database Backup:

- Performs daily MySQL database backups from one server to another.


### Upcoming features:
- Multiple Files in Mail Attachment
- Multi-Sheet CSV Support
- Additional Scheduling Options: Yearly, Weekly, Custom Intervals
- Automation of Daily Backups for PostgreSQL and Microsoft SQL Server Databases



### Test environment:

**OS**:              Ubuntu 20.04.6 LTS\
**Python version**:  3.11.5\
**SQLite3**:         For credentials and queries. No need for a separate setup. 
                     Comes with python by default.  
                     Need a GUI tool like [DB Browser](https://sqlitebrowser.org/) for editing SQLite.\
**PostgreSQL, MySQL, Microsoft SQL Server**:      For report data

**Microsoft ODBC 18** : [Install the Microsoft ODBC driver for SQL Server (Linux)](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver16&tabs=ubuntu18-install%2Calpine17-install%2Cdebian8-install%2Credhat7-13-install%2Crhel7-offline#18)

### Sample Report database:
[DVD rental database](https://www.postgresqltutorial.com/postgresql-getting-started/postgresql-sample-database/)


### Reports table

Creating ```reports``` table of ```creads.db``` SQLite database:

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
	"frequency"	TEXT,
	"date_time"	text,
	"query"	text,
	"active"	TEXT
)
```


Reports table description

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
frequency -      {daily/weekly/monthly/yearly ......}
date_time -      {trigger date time}

```

### Installation

Refer to **INSTALL.md** for installation instructions.

### Contribution

Check **CONTRIBUTING.md** to contribute. Your input is appreciated!

