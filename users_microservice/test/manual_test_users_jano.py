"""
Manual testing script for Users Microservice with JANO integration.
Tests user creation with password/username validation.
"""
import asyncio
import httpx
import json
from datetime import datetime


BASE_URL = "http://localhost:8006"
AUTH_URL = "http://localhost:8001"


async def get_root_token():
    """Get JWT token for ROOT user."""
    print("\n" + "="*60)
    print("Authenticating as ROOT user")
    print("="*60)
    
    payload = {
        "username": "admin",
        "password": "Admin123!@#"  # Default password from schema
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AUTH_URL}/api/v1/auth/login",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print(f"✅ Authentication successful")
                print(f"Token: {token[:20]}...")
                return token
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return None


async def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("Testing Health Check")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200


async def test_create_user_valid_password(token: str):
    """Test creating user with JANO-compliant password."""
    print("\n" + "="*60)
    print("Testing Create User - Valid Password (JANO compliant)")
    print("="*60)
    
    payload = {
        "username": "testuser001",
        "email": "testuser001@siata.gov.co",
        "password": "SecureP@ss123",  # Meets JANO requirements
        "name": "Test",
        "last_name": "User",
        "role": "USER",
        "team_name": "Development"
    }
    
    print(f"Request payload:")
    print(json.dumps({**payload, "password": "***"}, indent=2))
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/users",
            json=payload,
            headers=headers
        )
        
        print(f"\nStatus: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 201:
            print("✅ User created successfully (JANO validation passed)")
            return True, response_data.get("id")
        else:
            print("❌ User creation failed")
            return False, None


async def test_create_user_weak_password(token: str):
    """Test creating user with weak password (should fail JANO)."""
    print("\n" + "="*60)
    print("Testing Create User - Weak Password (should fail)")
    print("="*60)
    
    payload = {
        "username": "weakuser001",
        "email": "weakuser001@siata.gov.co",
        "password": "weak",  # Too short, missing requirements
        "name": "Weak",
        "last_name": "User",
        "role": "USER",
        "team_name": "Development"
    }
    
    print(f"Request payload:")
    print(json.dumps({**payload, "password": "weak"}, indent=2))
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/users",
            json=payload,
            headers=headers
        )
        
        print(f"\nStatus: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 400:
            detail = response_data.get("detail", {})
            if isinstance(detail, dict):
                violations = detail.get("violations", [])
                print(f"\n✅ Correctly rejected by JANO")
                print(f"Violations: {', '.join(violations)}")
                return True
            
        print("❌ Expected 400 with JANO violations")
        return False


async def test_create_user_invalid_username(token: str):
    """Test creating user with invalid username (should fail JANO)."""
    print("\n" + "="*60)
    print("Testing Create User - Invalid Username (should fail)")
    print("="*60)
    
    payload = {
        "username": "ab",  # Too short
        "email": "shortuser@siata.gov.co",
        "password": "ValidP@ss123",
        "name": "Short",
        "last_name": "User",
        "role": "USER",
        "team_name": "Development"
    }
    
    print(f"Request payload:")
    print(json.dumps({**payload, "password": "***"}, indent=2))
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/users",
            json=payload,
            headers=headers
        )
        
        print(f"\nStatus: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 400:
            detail = response_data.get("detail", {})
            if isinstance(detail, dict):
                violations = detail.get("violations", [])
                print(f"\n✅ Correctly rejected by JANO")
                print(f"Violations: {', '.join(violations)}")
                return True
        
        print("❌ Expected 400 with JANO violations")
        return False


async def test_get_user(token: str, user_id: str):
    """Test retrieving a user by ID."""
    print("\n" + "="*60)
    print(f"Testing Get User by ID: {user_id}")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/users/{user_id}",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ User retrieved successfully")
            return True
        else:
            print("❌ Failed to retrieve user")
            return False


async def test_duplicate_user(token: str):
    """Test creating duplicate user (should fail)."""
    print("\n" + "="*60)
    print("Testing Duplicate User Creation")
    print("="*60)
    
    # Create first user
    payload = {
        "username": "duplicate001",
        "email": "duplicate001@siata.gov.co",
        "password": "SecureP@ss123",
        "name": "Duplicate",
        "last_name": "Test",
        "role": "USER"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # First creation - should succeed
        response1 = await client.post(
            f"{BASE_URL}/api/users",
            json=payload,
            headers=headers
        )
        
        print(f"First creation status: {response1.status_code}")
        
        if response1.status_code != 201:
            print("❌ First creation failed")
            return False
        
        print("✅ First user created")
        
        # Second creation - should fail (duplicate)
        response2 = await client.post(
            f"{BASE_URL}/api/users",
            json=payload,
            headers=headers
        )
        
        print(f"\nSecond creation status: {response2.status_code}")
        response_data = response2.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response2.status_code == 409:
            print("✅ Correctly rejected duplicate user")
            return True
        else:
            print("❌ Expected 409 Conflict")
            return False


async def run_all_tests():
    """Run all test scenarios."""
    print("\n")
    print("*" * 80)
    print(" USERS MICROSERVICE + JANO INTEGRATION TESTS ")
    print("*" * 80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Users Service URL: {BASE_URL}")
    print(f"Auth Service URL: {AUTH_URL}")
    
    results = {}
    
    try:
        # Test 1: Health Check
        results["health_check"] = await test_health_check()
        
        # Get ROOT token for protected endpoints
        token = await get_root_token()
        
        if not token:
            print("\n❌ ERROR: Could not authenticate as ROOT user")
            print("   Make sure auth_microservice is running and ROOT user exists")
            return False
        
        # Test 2: Create user with valid password (JANO compliant)
        success, user_id = await test_create_user_valid_password(token)
        results["create_user_valid"] = success
        
        # Test 3: Get created user
        if user_id:
            results["get_user"] = await test_get_user(token, user_id)
        
        # Test 4: Create user with weak password (should fail JANO)
        results["weak_password_rejection"] = await test_create_user_weak_password(token)
        
        # Test 5: Create user with invalid username (should fail JANO)
        results["invalid_username_rejection"] = await test_create_user_invalid_username(token)
        
        # Test 6: Duplicate user (should fail)
        results["duplicate_user_rejection"] = await test_duplicate_user(token)
        
    except httpx.ConnectError as e:
        print(f"\n❌ ERROR: Could not connect to service: {str(e)}")
        print("   Make sure users_microservice is running")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    print("\n" + "="*80)
    print(" TEST SUMMARY ")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print("\n" + "-"*80)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    print("\n🚀 Starting Users Microservice + JANO Tests...")
    print("\nPrerequisites:")
    print("1. users_microservice must be running on http://localhost:8006")
    print("2. auth_microservice must be running on http://localhost:8001")
    print("3. jano_microservice must be running on http://localhost:8005")
    print("4. PostgreSQL database must be running and initialized")
    print("5. ROOT user must exist (username: admin)")
    
    input("\nPress Enter to continue with tests...")
    
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        exit(1)
