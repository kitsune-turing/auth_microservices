"""Test script for Users Microservice.

This script tests the basic functionality of the users_microservice.
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8006"


async def test_health_check():
    """Test the health check endpoint."""
    print("\n" + "=" * 70)
    print("TEST 1: Health Check")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
            print("✅ Health check passed")
        except Exception as e:
            print(f"❌ Health check failed: {e}")


async def test_validate_credentials():
    """Test the validate credentials endpoint with default user."""
    print("\n" + "=" * 70)
    print("TEST 2: Validate Credentials (Default ROOT User)")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/users/validate-credentials",
                json={
                    "username": "admin",
                    "password": "Admin123!",
                }
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                assert data["is_valid"] == True
                assert data["username"] == "admin"
                assert data["role"] == "ROOT"
                print("✅ Credentials validation passed")
                return data["user_id"]
            else:
                print("❌ Credentials validation failed")
                return None
        except Exception as e:
            print(f"❌ Credentials validation failed: {e}")
            return None


async def test_validate_credentials_invalid():
    """Test the validate credentials endpoint with invalid password."""
    print("\n" + "=" * 70)
    print("TEST 3: Validate Credentials (Invalid Password)")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/users/validate-credentials",
                json={
                    "username": "admin",
                    "password": "WrongPassword",
                }
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 401:
                print("✅ Invalid credentials correctly rejected")
            else:
                print(f"❌ Expected 401, got {response.status_code}")
        except Exception as e:
            print(f"❌ Test failed: {e}")


async def test_get_user(user_id: str):
    """Test the get user endpoint."""
    print("\n" + "=" * 70)
    print("TEST 4: Get User by ID")
    print("=" * 70)
    
    if not user_id:
        print("⚠️  Skipping test (no user_id from previous test)")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/users/{user_id}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                assert data["username"] == "admin"
                print("✅ Get user passed")
            else:
                print("❌ Get user failed")
        except Exception as e:
            print(f"❌ Get user failed: {e}")


async def test_create_user():
    """Test creating a new user."""
    print("\n" + "=" * 70)
    print("TEST 5: Create New User")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/users",
                json={
                    "username": "test_user",
                    "email": "test@siata.gov.co",
                    "password": "TestPass123!",
                    "name": "Test",
                    "last_name": "User",
                    "role": "USER_SIATA",
                    "team_name": "Testing Team",
                }
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 201:
                data = response.json()
                print("✅ User created successfully")
                return data["user_id"]
            elif response.status_code == 409:
                print("⚠️  User already exists (this is expected if running test multiple times)")
                return None
            else:
                print("❌ User creation failed")
                return None
        except Exception as e:
            print(f"❌ User creation failed: {e}")
            return None


async def test_validate_new_user_credentials():
    """Test validating the newly created user's credentials."""
    print("\n" + "=" * 70)
    print("TEST 6: Validate New User Credentials")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/users/validate-credentials",
                json={
                    "username": "test_user",
                    "password": "TestPass123!",
                }
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data}")
                assert data["is_valid"] == True
                assert data["username"] == "test_user"
                assert data["role"] == "USER_SIATA"
                print("✅ New user credentials validation passed")
            elif response.status_code == 401:
                print("❌ Credentials validation failed (user may not exist)")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Test failed: {e}")


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("USERS MICROSERVICE TEST SUITE")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print("=" * 70)
    
    try:
        # Test 1: Health check
        await test_health_check()
        
        # Test 2: Validate default user credentials
        user_id = await test_validate_credentials()
        
        # Test 3: Validate invalid credentials
        await test_validate_credentials_invalid()
        
        # Test 4: Get user by ID
        await test_get_user(user_id)
        
        # Test 5: Create new user
        new_user_id = await test_create_user()
        
        # Test 6: Validate new user credentials
        await test_validate_new_user_credentials()
        
        print("\n" + "=" * 70)
        print("TEST SUITE COMPLETED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
