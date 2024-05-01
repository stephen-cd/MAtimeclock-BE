#!/bin/bash
#

# initialize files
touch data/access.log
touch data/error.log
touch data/last-updated.txt

# Set permissions for the data directory
chown -R 33:33 data/

# Start Docker Compose or a Docker container
docker-compose up
