#!/bin/bash

echo "Running Django makemigrations..."
python3 manage.py makemigrations
if [ "$?" -ne 0 ]; then
    echo "makemigrations failed, stopping script."
    exit 1
fi

echo "Running Django migrate..."
attempt=1
while true; do
    python3 manage.py migrate
    if [ "$?" -eq 0 ]; then
        echo "Migrate successful."
        break
    else
        echo "Attempt $attempt: Migrate failed, retrying in 3 seconds..."
        attempt=$((attempt+1))
        sleep 3
    fi
    if [ $attempt -gt 5 ]; then
        echo "Migrate failed after 5 attempts, stopping script."
        exit 1
    fi
done
