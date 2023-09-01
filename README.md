# Dynamic-Report-Scheduler

Test environment:

Ubuntu 20.04.6 LTS\
Python 3.10\
[APScheduler](https://github.com/agronholm/apscheduler) 3.10.4\
PostgreSQL\
Microsoft SQL Server

The sample scheduler can generate reports everyday in the specified time. Microsoft SQL Server is being used to store data for reports. In PostgreSQL credential of senders mail, credential of MS SQL Server,  list of receiver mails, subject text, body text in html format, stored procedures are stored.      
