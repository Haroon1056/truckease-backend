#!/bin/bash
set -o errexit

echo "========================================="
echo "Building TruckEase Backend"
echo "========================================="

# Add this after the echo statements
export DJANGO_SETTINGS_MODULE=config.settings

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

# Create superuser (delete existing and create fresh one)
echo "Creating superuser..."
python manage.py shell <<EOF
from accounts.models import User

# Delete all existing superusers first to avoid conflicts
deleted_count = User.objects.filter(is_superuser=True).delete()[0]
print(f"Deleted {deleted_count} existing superuser(s)")

# Create new superuser
email = "admin@truckease.com"
password = "Admin123!"
first_name = "System"
last_name = "Admin"

user = User.objects.create_superuser(
    email=email,
    password=password,
    first_name=first_name,
    last_name=last_name,
    user_type='admin',
    phone_number="0000000000"
)
print(f"Superuser created: {email} / {password}")

# Create test customer user
if not User.objects.filter(email='customer@example.com').exists():
    User.objects.create_user(
        email='customer@example.com',
        password='customer123',
        first_name='Test',
        last_name='Customer',
        user_type='customer',
        phone_number='1234567899'
    )
    print("Test customer created: customer@example.com / customer123")

# Create test driver user
if not User.objects.filter(email='driver@example.com').exists():
    User.objects.create_user(
        email='driver@example.com',
        password='driver123',
        first_name='Test',
        last_name='Driver',
        user_type='driver',
        phone_number='9876543210'
    )
    print("Test driver created: driver@example.com / driver123")

print("\n=== All Users ===")
for u in User.objects.all():
    print(f"  {u.email} ({u.user_type}) - is_superuser: {u.is_superuser}")
EOF

echo "========================================="
echo "Build completed successfully!"
echo "========================================="