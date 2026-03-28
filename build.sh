#!/bin/bash
set -o errexit

echo "========================================="
echo "Building TruckEase Backend"
echo "========================================="

# First install setuptools before anything else
echo "Installing setuptools first..."
pip install setuptools==65.5.0

# Now install all dependencies
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
    phone_number='0100000000'
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
        phone_number='1111111112'
    )
    print("Customer created: customer@example.com / customer123")

if not User.objects.filter(email='driver@example.com').exists():
    User.objects.create_user(
        email='driver@example.com',
        password='driver123',
        first_name='Test',
        last_name='Driver',
        user_type='driver',
        phone_number='2222222242'
    )
    print("Driver created: driver@example.com / driver123")
EOF

echo "========================================="
echo "Build completed successfully!"
echo "========================================="