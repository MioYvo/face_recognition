#!/usr/bin/env sh
until nc -z rabbit 5672; do
    echo "$(date) - waiting for rabbit..."
    sleep 1
done
echo "rabbit ok"

until nc -z mongo 27017; do
    echo "$(date) - waiting for mongo..."
    sleep 1
done
echo "mongo ok"

until nc -z redis 6379; do
    echo "$(date) - waiting for redis..."
    sleep 1
done
echo "redis ok"

python app.py