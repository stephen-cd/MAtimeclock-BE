# Setup
sudo docker-compose build

# Run
sudo docker-compose up

# Access
Should be accessible through 127.0.0.1:8000

# Create superuser
docker-compose run matimeclock-server python manage.py createsuperuser

# Troubleshooting
- Check access.log and error.log
- Access the running docker and troubleshoot things with the following command
```
sudo docker exec -it matimeclock-server /bin/bash
```

