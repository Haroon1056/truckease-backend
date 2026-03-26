#!/bin/bash
set -o errexit

echo "========================================="
echo "Building TruckEase Backend"
echo "========================================="

export DJANGO_SETTINGS_MODULE=config.settings

echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Making migrations (IMPORTANT)..."
python manage.py makemigrations --noinput

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating superuser (safe way)..."
python manage.py shell <<EOF
from accounts.models import User

if not User.objects.filter(email='admin@truckease.com').exists():
    User.objects.create_superuser(
        email='admin@truckease.com',
        password='Admin123!',
        first_name='System',
        last_name='Admin',
        user_type='admin',
        phone_number='03187040876'
    )
    print("Superuser created")
else:
    print("Superuser already exists")
EOF

echo "========================================="
echo "Build completed successfully!"
echo "========================================="