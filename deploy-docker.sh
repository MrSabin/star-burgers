#!/bin/bash

set -Eeuo pipefail

cd /opt/star-burgers
export $(xargs < ./star_burger/.env)
docker-compose build
docker-compose pull
docker-compose up -d
echo "Deploy succesful"
