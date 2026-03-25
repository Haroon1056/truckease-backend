#!/bin/bash
set -o errexit

echo "========================================="
echo "Building TruckEase Backend"
echo "========================================="

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Create superuser using management command
python manage.py createsu

echo "========================================="
echo "Build completed successfully!"
echo "========================================="