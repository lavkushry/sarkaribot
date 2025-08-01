#!/bin/bash
# SarkariBot Backend Development Server

echo "Starting SarkariBot Backend..."

cd "/home/lavku/govt/sarkaribot/backend"
source venv/bin/activate

echo "Running system checks..."
python manage.py check --settings=config.settings_dev

echo "Running migrations..."
python manage.py migrate --settings=config.settings_dev

echo "Creating sample data..."
python create_sample_data.py

echo "Starting Django server on http://127.0.0.1:8000"
python manage.py runserver 8000 --settings=config.settings_dev
