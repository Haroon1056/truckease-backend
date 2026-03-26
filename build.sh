#!/bin/bash
set -o errexit

echo "========================================="
echo "Building TruckEase Backend"
echo "========================================="

# Set Django settings module
export DJANGO_SETTINGS_MODULE=config.settings

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Collect static files (MUST run before migrations)
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser
echo "Creating superuser..."
python manage.py shell <<EOF
from accounts.models import User

# Delete existing superusers
User.objects.filter(is_superuser=True).delete()

# Create new superuser
User.objects.create_superuser(
    email='admin@truckease.com',
    password='Admin123!',
    first_name='System',
    last_name='Admin',
    user_type='admin',
    phone_number='03187040876'
)
print("Superuser created: admin@truckease.com / Admin123!")

# Create test users
if not User.objects.filter(email='customer@example.com').exists():
    User.objects.create_user(
        email='customer@example.com',
        password='customer123',
        first_name='Test',
        last_name='Customer',
        user_type='customer',
        phone_number='1111151111'
    )
    print("Customer created: customer@example.com / customer123")

if not User.objects.filter(email='driver@example.com').exists():
    User.objects.create_user(
        email='driver@example.com',
        password='driver123',
        first_name='Test',
        last_name='Driver',
        user_type='driver',
        phone_number='2242222222'
    )
    print("Driver created: driver@example.com / driver123")
EOF

echo "========================================="
echo "Build completed successfully!"
echo "========================================="