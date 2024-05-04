#!/bin/bash

set -Eeuo pipefail

cd /opt/star-burgers
docker-compose up -d --build
echo "Deploy succesful"
