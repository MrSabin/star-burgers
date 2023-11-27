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
echo Updated
