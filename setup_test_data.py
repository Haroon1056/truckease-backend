import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

def create_user(email, password, first_name, last_name, user_type, phone_number):
    """Create a test user"""
    data = {
        "email": email,
        "password": password,
        "confirm_password": password,
        "first_name": first_name,
        "last_name": last_name,
        "user_type": user_type,
        "phone_number": phone_number
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"  [OK] Created {user_type}: {email}")
        return result['tokens']['access']
    elif response.status_code == 400:
        print(f"  [WARN] {user_type} already exists: {email}")
        # Try to login
        login_response = requests.post(f"{BASE_URL}/auth/login/", 
                                       json={"email": email, "password": password})
        if login_response.status_code == 200:
            return login_response.json()['tokens']['access']
    else:
        print(f"  [FAIL] Could not create {user_type}: {response.json()}")
    
    return None

def create_vehicle(driver_token):
    """Create a test vehicle for driver"""
    vehicle_data = {
        "vehicle_type": "medium",
        "make": "Toyota",
        "model": "Hilux",
        "year": 2022,
        "license_plate": "TEST-123",
        "color": "White",
        "capacity_tons": 3.5,
        "dimensions": "5.2m x 2.1m x 2.0m",
        "description": "Well-maintained truck with AC",
        "features": "GPS, AC, Hydraulic lift",
        "current_city": "Karachi",
        "current_area": "Gulshan",
        "base_price_per_km": 50.00,
        "base_price_per_hour": 500.00
    }
    
    headers = {"Authorization": f"Bearer {driver_token}"}
    response = requests.post(f"{BASE_URL}/vehicles/", json=vehicle_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"  [OK] Vehicle created: {vehicle_data['license_plate']}")
        # The response might be a list or a dict
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('id')
        elif isinstance(result, dict):
            return result.get('id')
        else:
            print(f"  [WARN] Vehicle created but couldn't get ID")
            return None
    elif response.status_code == 400:
        print(f"  [WARN] Vehicle may already exist")
        # Try to list existing vehicles
        list_response = requests.get(f"{BASE_URL}/vehicles/", headers=headers)
        if list_response.status_code == 200:
            vehicles = list_response.json()
            if vehicles and isinstance(vehicles, list) and len(vehicles) > 0:
                return vehicles[0].get('id')
    else:
        print(f"  [FAIL] Could not create vehicle: {response.json()}")
    
    return None

def create_booking(customer_token, vehicle_id=None):
    """Create a test booking"""
    pickup_time = (datetime.now() + timedelta(hours=2)).isoformat()
    
    booking_data = {
        "pickup_address": "123 Main Street, Karachi",
        "pickup_latitude": 24.8607,
        "pickup_longitude": 67.0011,
        "dropoff_address": "456 Korangi Road, Karachi",
        "dropoff_latitude": 24.8463,
        "dropoff_longitude": 67.1269,
        "cargo_type": "Electronics",
        "cargo_weight": 2.5,
        "pickup_time": pickup_time,
        "customer_notes": "Handle with care - fragile items"
    }
    
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = requests.post(f"{BASE_URL}/bookings/", json=booking_data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"  [OK] Booking created with ID: {result.get('id')}")
        return result.get('id')
    else:
        print(f"  [FAIL] Could not create booking: {response.json()}")
        return None

def accept_booking(driver_token, booking_id):
    """Driver accepts a booking"""
    headers = {"Authorization": f"Bearer {driver_token}"}
    response = requests.post(f"{BASE_URL}/bookings/{booking_id}/accept/", headers=headers)
    
    if response.status_code == 200:
        print(f"  [OK] Booking {booking_id} accepted")
        return True
    else:
        print(f"  [WARN] Could not accept booking: {response.json() if response.status_code != 200 else 'Already accepted'}")
        return False

def main():
    print("\n" + "="*60)
    print("SETTING UP TEST DATA")
    print("="*60)
    
    # Create test users
    print("\n1. Creating test users...")
    customer_token = create_user(
        "test_customer@example.com",
        "TestPass123!",
        "Test",
        "Customer",
        "customer",
        "1234567890"
    )
    
    driver_token = create_user(
        "test_driver@example.com",
        "DriverPass123!",
        "Test",
        "Driver",
        "driver",
        "0987654321"
    )
    
    admin_token = create_user(
        "admin@truckease.com",
        "Admin123!",
        "System",
        "Admin",
        "admin",
        "0000000000"
    )
    
    if not customer_token or not driver_token or not admin_token:
        print("\n  [ERROR] Could not get tokens for all users!")
        return
    
    # Create vehicle for driver
    print("\n2. Creating vehicle for driver...")
    vehicle_id = create_vehicle(driver_token)
    
    if not vehicle_id:
        print("  [WARN] Could not create or find vehicle")
    
    # Create booking for customer
    print("\n3. Creating booking for customer...")
    booking_id = create_booking(customer_token)
    
    if booking_id:
        # Accept booking as driver
        print("\n4. Accepting booking as driver...")
        accept_booking(driver_token, booking_id)
    
    print("\n" + "="*60)
    print("TEST DATA SETUP COMPLETE")
    print("="*60)
    print("\nSummary:")
    print(f"  Customer Token: {customer_token[:30]}...")
    print(f"  Driver Token: {driver_token[:30]}...")
    print(f"  Admin Token: {admin_token[:30]}...")
    if vehicle_id:
        print(f"  Vehicle ID: {vehicle_id}")
    if booking_id:
        print(f"  Booking ID: {booking_id}")
    print("\nNow you can run: python final_verification.py")
    print("="*60)

if __name__ == "__main__":
    main()