#!/usr/bin/env sh
until nc -z mariadb 3306; do
    echo "$(date) - waiting for maria ..."
    sleep 1
done
echo "maria ok"


python app.py