- git pull
- Create venv if haven't already and pip install Django==5.0.3
- DB file is included in repo so shouldn't have to migrate anything
- python manage.py runserver
<br>
<br>
If you want to test the data transfer then just have the front-end and back-end running at the same time. Right now it happens automatically, if you want to stop it then just comment out the updateWebServer() call on line 39 in index.js on the FE.
