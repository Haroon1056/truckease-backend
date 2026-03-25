import subprocess
import sys
import time
import os

def run_test(test_file):
    """Run a single test file"""
    print("\n" + "="*80)
    print(f"RUNNING: {test_file}")
    print("="*80)
    
    try:
        # Set PYTHONIOENCODING to utf-8 to handle Unicode
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        # Print output safely
        if result.stdout:
            print(result.stdout.encode('ascii', 'ignore').decode('ascii'))
        if result.stderr:
            print("Errors:", result.stderr.encode('ascii', 'ignore').decode('ascii'))
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"[FAIL] Test {test_file} timed out!")
        return False
    except Exception as e:
        print(f"[FAIL] Error running {test_file}: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("TRUCKEASE COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nMake sure Django server is running on http://127.0.0.1:8000")
    print("Press Enter to continue...")
    input()
    
    tests = [
        "test_1_auth.py",
        "test_2_vehicle.py",
        "test_3_booking.py",
        "test_4_review.py",
        "test_5_notification.py",
        "test_6_admin.py"
    ]
    
    results = {}
    
    for test in tests:
        print(f"\n{'='*80}")
        print(f"Starting {test}...")
        print('='*80)
        
        if results:
            time.sleep(2)
        
        success = run_test(test)
        results[test] = success
        
        if not success:
            print(f"\n[WARNING] {test} failed! Do you want to continue? (y/n): ", end="")
            choice = input().lower()
            if choice != 'y':
                break
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test:30} {status}")
    
    total = len(results)
    passed = sum(1 for p in results.values() if p)
    
    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED! Ready for deployment! [SUCCESS]")
    else:
        print("\n[WARNING] Some tests failed. Please fix issues before deployment.")

if __name__ == "__main__":
    main()