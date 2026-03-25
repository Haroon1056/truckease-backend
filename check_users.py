import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def check_user(email, password, user_type):
    """Check if user exists and can login"""
    print(f"\nChecking {user_type}: {email}")
    
    # Try to login
    login_data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    if response.status_code == 200:
        result = response.json()
        token = result['tokens']['access']
        print(f"  [OK] Login successful!")
        print(f"  Token: {token[:50]}...")
        return token
    else:
        print(f"  [FAIL] Login failed: {response.json()}")
        return None

def main():
    print("\n" + "="*60)
    print("CHECKING EXISTING USERS")
    print("="*60)
    
    # Check each user
    customer_token = check_user("test_customer@example.com", "TestPass123!", "Customer")
    driver_token = check_user("test_driver@example.com", "DriverPass123!", "Driver")
    admin_token = check_user("admin@truckease.com", "Admin123!", "Admin")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if customer_token:
        print("[OK] Customer login works")
    else:
        print("[FAIL] Customer login failed - password might be incorrect")
        
    if driver_token:
        print("[OK] Driver login works")
    else:
        print("[FAIL] Driver login failed - password might be incorrect")
        
    if admin_token:
        print("[OK] Admin login works")
    else:
        print("[FAIL] Admin login failed - password might be incorrect")
    
    print("="*60)

if __name__ == "__main__":
    main()