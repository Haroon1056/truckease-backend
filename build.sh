#!/bin/bash
set -o errexit

echo "========================================="
echo "Building TruckEase Backend"
echo "========================================="

# Upgrade pip and setuptools
echo "Upgrading pip and setuptools..."
python -m pip install --upgrade pip setuptools wheel

# Install dependencies with special handling for Pillow
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt || {
    echo "Retrying with --no-cache-dir..."
    pip install --no-cache-dir -r requirements.txt
}

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput || {
    echo "Migration failed, retrying..."
    python manage.py migrate --noinput
}

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
EOF

echo "========================================="
echo "Build completed successfully!"
echo "========================================="