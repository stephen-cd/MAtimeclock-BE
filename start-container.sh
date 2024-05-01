#!/bin/bash

# Set permissions for the data directory
chown -R 33:33 data/

# Start Docker Compose or a Docker container
docker-compose up
