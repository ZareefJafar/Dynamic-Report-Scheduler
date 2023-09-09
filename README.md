# Dynamic-Report-Scheduler

Test environment:

Ubuntu 20.04.6 LTS\
Python 3.10\
[APScheduler](https://github.com/agronholm/apscheduler) 3.10.4\
SQLite3: A lightweight C-language library. It comes preinstalled with Python Standard Library as sqlite3 module. So it can be used without any separate installation.\
PostgreSQL\
[pycryptodome](https://github.com/Legrandin/pycryptodome) : For AES-256 Encryption and Decryption.

The sample scheduler can generate reports everyday in the specified time. PostgreSQL is being used to store data for reports. In SQLite3 credential of senders mail, credential of PostgreSQL,  list of receiver mails, subject text, body text in html format, stored procedures are stored. Implemented AES-256 based encrypt and decryptfor some sensitive credentials. Can easily be implemented for encrypting for all the credential.
