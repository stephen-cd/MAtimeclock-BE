<h1>Overview</h1>

An application that serves as a time clock as well as an employee management system. By logging in with a PIN and choosing a job, employees can clock in and have their work session tracked. Managers can add/edit employees, jobs, and work sessions. Data is saved to a local SQLite file and is transferred to a web server either manually or periodically. Managers can log into the web server and select a range of dates from which they can generate a report of work session data. The report displays separate tables of the hours worked per employee and the hours worked on each job, giving total hours for each employee and total hours put into each job. Built using Electron for the front-end, Django for the back-end web server, and SQLite for data storage.

This is the back-end repository, which involves the Django code for the web server.

Note: This application was built to be used with a Raspberry Pi and the official Raspberry Pi touchscreen. It can be used without it, but it has not been adapted for other screen sizes and will start up in a resolution of 800x480.

<h1>Setup</h1>

<h2>Prerequisites: set up virtualenv</h2>

virtualenv -p python3 venv<br>
source venv/bin/activate<br>
pip install -r requirements.txt

<h3>create database</h3>
While in the same directory as manage.py, run python manage.py migrate to create a blank database<br>

run python manage.py createsuperuser to create a user.<br>

finally, create the 'backup database' by running this in the data folder: cp db.sqlite3 db-backup.sqlite3

<h3>run server</h3>
Run python manage.py runserver to run the server and visit 127.0.0.1:8000 to see the login page.

<h1>Report Generation</h1>
Login in as the user made in Setup, then select a start date and and end date and click Generate Report. Results will show only if the back-end SQLite database has been synced by the front-end (See MAtimeclock repository for more information on how this is accomplished). If results are shown, there will be 2 tables, one that displays hours per employee per job with totals and one that displays hours per job per employee with totals.

<h1>Server Deployment</h1>
Please see README_DOCKER.MD for next steps
