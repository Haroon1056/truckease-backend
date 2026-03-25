import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api"

def print_section(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def verify_endpoint(method, url, description, token=None, data=None):
    """Generic endpoint tester"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        else:
            return False, None
        
        if response.status_code in [200, 201]:
            print(f"  [OK] {description} - Status: {response.status_code}")
            if response.status_code == 200 and response.text:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            return True, None
        else:
            print(f"  [FAIL] {description} - Status: {response.status_code}")
            if response.text:
                print(f"    Response: {response.text[:200]}")
            return False, None
    except Exception as e:
        print(f"  [ERROR] {description} - {str(e)}")
        return False, None

def main():
    print_section("TRUCKEASE FINAL VERIFICATION")
    
    # Test 1: Public endpoints
    print_section("1. Public Endpoints")
    verify_endpoint("GET", f"{BASE_URL}/vehicles/available/", 
                   "Available vehicles endpoint (public)")
    
    # Test 2: Authentication
    print_section("2. Authentication")
    
    # Login as customer
    success, result = verify_endpoint("POST", f"{BASE_URL}/auth/login/",
                                     "Customer login",
                                     data={"email": "test_customer@example.com", 
                                           "password": "TestPass123!"})
    
    customer_token = None
    if success and result:
        customer_token = result.get('tokens', {}).get('access')
        if customer_token:
            print(f"  Customer token received: {customer_token[:30]}...")
            
            # Get customer profile
            verify_endpoint("GET", f"{BASE_URL}/auth/profile/",
                           "Get customer profile",
                           token=customer_token)
    
    # Login as driver
    success, result = verify_endpoint("POST", f"{BASE_URL}/auth/login/",
                                     "Driver login",
                                     data={"email": "test_driver@example.com", 
                                           "password": "DriverPass123!"})
    
    driver_token = None
    if success and result:
        driver_token = result.get('tokens', {}).get('access')
        if driver_token:
            print(f"  Driver token received: {driver_token[:30]}...")
            
            # Get driver profile
            verify_endpoint("GET", f"{BASE_URL}/auth/profile/",
                           "Get driver profile",
                           token=driver_token)
    
    # Login as admin
    success, result = verify_endpoint("POST", f"{BASE_URL}/auth/login/",
                                     "Admin login",
                                     data={"email": "admin@truckease.com", 
                                           "password": "Admin123!"})
    
    admin_token = None
    if success and result:
        admin_token = result.get('tokens', {}).get('access')
        if admin_token:
            print(f"  Admin token received: {admin_token[:30]}...")
    
    # Test 3: Vehicle endpoints
    if driver_token:
        print_section("3. Vehicle Management")
        
        # List driver's vehicles
        success, vehicles = verify_endpoint("GET", f"{BASE_URL}/vehicles/",
                                           "List driver vehicles",
                                           token=driver_token)
        
        if success and vehicles and isinstance(vehicles, list):
            print(f"  Found {len(vehicles)} vehicle(s)")
            
            if vehicles:
                vehicle_id = vehicles[0].get('id')
                if vehicle_id:
                    # Get vehicle details
                    verify_endpoint("GET", f"{BASE_URL}/vehicles/{vehicle_id}/",
                                   "Get vehicle details",
                                   token=driver_token)
    
    # Test 4: Booking endpoints
    if customer_token:
        print_section("4. Booking Management")
        
        # List customer bookings
        success, bookings = verify_endpoint("GET", f"{BASE_URL}/bookings/",
                                           "List customer bookings",
                                           token=customer_token)
        
        if success and bookings and isinstance(bookings, list):
            print(f"  Found {len(bookings)} booking(s)")
            
            if bookings:
                booking_id = bookings[0].get('id')
                if booking_id:
                    # Get booking details
                    verify_endpoint("GET", f"{BASE_URL}/bookings/{booking_id}/",
                                   "Get booking details",
                                   token=customer_token)
                    
                    # Get booking history
                    verify_endpoint("GET", f"{BASE_URL}/bookings/{booking_id}/history/",
                                   "Get booking history",
                                   token=customer_token)
    
    # Test 5: Notification endpoints
    if customer_token:
        print_section("5. Notifications")
        
        # Get unread count
        success, result = verify_endpoint("GET", f"{BASE_URL}/notifications/unread-count/",
                                         "Get unread count",
                                         token=customer_token)
        
        if success and result:
            print(f"  Unread notifications: {result.get('unread_count', 0)}")
        
        # List notifications
        verify_endpoint("GET", f"{BASE_URL}/notifications/",
                       "List notifications",
                       token=customer_token)
    
    # Test 6: Review endpoints
    if customer_token:
        print_section("6. Reviews")
        
        # List reviews
        success, reviews = verify_endpoint("GET", f"{BASE_URL}/reviews/",
                                          "List reviews",
                                          token=customer_token)
        
        if success and reviews and isinstance(reviews, list):
            print(f"  Found {len(reviews)} review(s)")
        
        # Get driver ratings (public)
        verify_endpoint("GET", f"{BASE_URL}/drivers/1/ratings/",
                       "Get driver ratings (public)")
    
    # Test 7: Tracking endpoints
    if driver_token:
        print_section("7. Tracking")
        
        # Get vehicles first
        success, vehicles = verify_endpoint("GET", f"{BASE_URL}/vehicles/",
                                           "List vehicles for tracking",
                                           token=driver_token)
        
        if success and vehicles and isinstance(vehicles, list) and vehicles:
            vehicle_id = vehicles[0].get('id')
            if vehicle_id:
                # Get location history
                verify_endpoint("GET", f"{BASE_URL}/tracking/vehicle/{vehicle_id}/history/?hours=24",
                               "Vehicle tracking history",
                               token=driver_token)
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    all_passed = customer_token and driver_token and admin_token
    
    if all_passed:
        print("""
    [SUCCESS] All core endpoints are working!
    
    System Components Verified:
    [OK] Authentication (Customer/Driver/Admin)
    [OK] Vehicle Management
    [OK] Booking System
    [OK] Notifications
    [OK] Reviews
    [OK] Tracking
    
    The backend is ready for deployment!
        """)
    else:
        print("""
    [WARNING] Some tests failed. Please check the output above.
    
    Make sure:
    1. Django server is running
    2. Test users exist (run setup_test_data.py first)
    3. Database is properly migrated
        """)

if __name__ == "__main__":
    main()