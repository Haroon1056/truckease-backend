#!/bin/bash
set -o errexit

echo "========================================="
echo "Building TruckEase Backend"
echo "========================================="

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser
echo "Creating superuser..."
python manage.py shell <<EOF
import os
from accounts.models import User

email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@truckease.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Truck!213')
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'TruckEase')

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name='System',
        last_name='Admin',
        user_type='admin'
    )
    print(f"Superuser created: {email}")
else:
    print(f"Superuser already exists: {email}")

# Create test users for demo (optional)
if not User.objects.filter(email='demo@example.com').exists():
    User.objects.create_user(
        email='demo@example.com',
        password='demo123',
        first_name='Demo',
        last_name='User',
        user_type='customer',
        phone_number='1234567899'
    )
    print("Demo user created: demo@example.com")
EOF

echo "========================================="
echo "Build completed successfully!"
echo "========================================="