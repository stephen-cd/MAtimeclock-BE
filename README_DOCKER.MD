# Setup
- First: copy db.sqlite3 with a superuser added in (or do the create superuser step later)
- to build, run command: sudo docker-compose build

# Run (deploy to server) (exposed to port 8000 by default)
sudo docker-compose up

# Access
Should be accessible through 127.0.0.1:8000

# Create superuser [only if you don't have a db.sqlite3 with a superuser to login with]
docker-compose run matimeclock-server python manage.py createsuperuser

# Troubleshooting
- Access the running docker and troubleshoot things with the following command
```
sudo docker exec -it matimeclock-server /bin/bash
```
- Check access.log and error.log (note: currently only accessable by accessing the docker itself, need to fix this)

