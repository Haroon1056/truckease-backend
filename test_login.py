import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_login(email, password, user_type):
    """Test login for a user"""
    print(f"\n{'='*50}")
    print(f"Testing {user_type} Login")
    print('='*50)
    
    data = {"email": email, "password": password}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=data, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] {user_type} logged in successfully!")
            print(f"  User: {result['user']['first_name']} {result['user']['last_name']}")
            print(f"  Email: {result['user']['email']}")
            print(f"  Type: {result['user']['user_type']}")
            print(f"  Token: {result['tokens']['access'][:60]}...")
            return result['tokens']['access']
        else:
            print(f"[FAILED] {user_type} login failed!")
            print(f"Response: {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server. Make sure Django is running!")
        return None
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return None

def main():
    print("\n" + "="*60)
    print("TRUCKEASE LOGIN TEST")
    print("="*60)
    
    # Test all users
    customer_token = test_login("test_customer@example.com", "TestPass123!", "Customer")
    driver_token = test_login("test_driver@example.com", "DriverPass123!", "Driver")
    admin_token = test_login("admin@truckease.com", "Admin123!", "Admin")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    results = {
        "Customer": customer_token,
        "Driver": driver_token,
        "Admin": admin_token
    }
    
    all_passed = all(results.values())
    
    for role, token in results.items():
        status = "[PASS]" if token else "[FAIL]"
        print(f"{role:10} {status}")
    
    print("="*60)
    
    if all_passed:
        print("\n[SUCCESS] All logins working!")
        print("\nNow you can run:")
        print("  python final_verification.py")
    else:
        print("\n[WARNING] Some logins failed. Please check:")
        print("  1. Django server is running")
        print("  2. Passwords are correct")
        print("  3. Users exist in database")
    
    print("="*60)

if __name__ == "__main__":
    main()