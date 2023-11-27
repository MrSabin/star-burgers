#!/bin/bash

set -Eeuo pipefail

cd /opt/star-burgers/
git pull
. ./.venv/bin/activate
pip install -r requirements.txt
npm ci --include=dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

python manage.py collectstatic --noinput
python manage.py migrate --noinput

systemctl restart sb-gunicorn.service
systemctl reload nginx.service

export $(xargs <.env)

last_commit=$(git rev-parse HEAD)

curl -H "X-Rollbar-Access-Token: '${ROLLBAR_TOKEN}'" \
     -H "Content-Type: application/json" \
     -X POST 'https://api.rollbar.com/api/1/deploy' \
     -d '{"environment": "production", "revision": "'${last_commit}'", "rollbar_username": "'${ROLLBAR_USERNAME}'", "status": "succeeded"}'

echo Updated
