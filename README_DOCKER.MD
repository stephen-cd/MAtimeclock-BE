# Pre-requisites
you need to a create a directory called 'data' that contains db.sqlite3,
if you need this, please follow the database setup in README.MD

# Setup
to build, run command: sudo docker-compose build

# Run the script to bring up the docker. This script needs to be run to ensure permissions are set for the data folder, after, you can run docker-compose up
# _note: you may need to run the below command as sudo depending on your system permissions_
./start-container.sh

# Access (the exposed port can be configured in docker-compose.yaml)
Should be accessible through 127.0.0.1:8888 with default settings.

# Create superuser [only if you don't have a db.sqlite3 with a superuser to login with]
docker-compose run matimeclock-server python manage.py createsuperuser

# Troubleshooting
- Access the running docker and troubleshoot things with the following command
```
sudo docker exec -it matimeclock-server /bin/bash
```
- Check access.log and error.log in the root directory
- If you get an error about not being able to open or read the database, the permissions for the data directory are not set correctly on the host. Running the following command should fix it
```
chown -R 33:33 data/
```
