#!/bin/bash

set -Eeuo pipefail

cd /opt/star-burgers
export $(xargs < ./star_burger/.env)
docker-compose up -d --build
echo "Deploy succesful"
