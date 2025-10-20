"""
Manual testing script for OTP microservice endpoints.
Run this script to test OTP generation and validation.
"""
import asyncio
import httpx
import json
from datetime import datetime


BASE_URL = "http://localhost:8003"


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


async def test_generate_otp():
    """Test OTP generation endpoint."""
    print("\n" + "="*60)
    print("Testing OTP Generation")
    print("="*60)
    
    payload = {
        "user_id": "test_user_12345",
        "delivery_method": "email",
        "recipient": "test@example.com"
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/otp/generate",
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            return response_data.get("otp_id"), response_data.get("code")
        return None, None


async def test_validate_otp(otp_id: str, code: str, user_id: str):
    """Test OTP validation endpoint."""
    print("\n" + "="*60)
    print("Testing OTP Validation")
    print("="*60)
    
    payload = {
        "otp_id": otp_id,
        "code": code,
        "user_id": user_id
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/otp/validate",
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        return response.status_code == 200 and response_data.get("valid") is True


async def test_invalid_otp(otp_id: str, user_id: str):
    """Test validation with invalid OTP code."""
    print("\n" + "="*60)
    print("Testing Invalid OTP Code")
    print("="*60)
    
    payload = {
        "otp_id": otp_id,
        "code": "000000",  # Invalid code
        "user_id": user_id
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/otp/validate",
            json=payload
        )
        
        print(f"\nStatus: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        return response.status_code == 200 and response_data.get("valid") is False


async def test_max_attempts():
    """Test maximum attempts exceeded."""
    print("\n" + "="*60)
    print("Testing Max Attempts Exceeded")
    print("="*60)
    
    # Generate new OTP
    user_id = "test_user_max_attempts"
    payload = {
        "user_id": user_id,
        "delivery_method": "email",
        "recipient": "maxattempts@example.com"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/otp/generate",
            json=payload
        )
        
        if response.status_code != 200:
            print("Failed to generate OTP for max attempts test")
            return False
        
        data = response.json()
        otp_id = data.get("otp_id")
        
        print(f"Generated OTP ID: {otp_id}")
        
        # Try 3 times with wrong code
        for attempt in range(3):
            print(f"\nAttempt {attempt + 1}/3 with invalid code...")
            validate_payload = {
                "otp_id": otp_id,
                "code": "999999",
                "user_id": user_id
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/otp/validate",
                json=validate_payload
            )
            
            print(f"Status: {response.status_code}")
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            if attempt == 2:  # Last attempt
                # Should indicate max attempts exceeded
                return "attempts" in response_data.get("message", "").lower()


async def test_complete_flow():
    """Test complete OTP flow: generate -> validate successfully."""
    print("\n" + "="*80)
    print(" COMPLETE OTP FLOW TEST ")
    print("="*80)
    
    user_id = "test_user_complete_flow"
    
    # Step 1: Generate OTP
    print("\nStep 1: Generating OTP...")
    otp_id, code = await test_generate_otp()
    
    if not otp_id or not code:
        print("❌ Failed to generate OTP")
        return False
    
    print(f"✅ OTP generated successfully")
    print(f"   OTP ID: {otp_id}")
    print(f"   Code: {code}")
    
    # Step 2: Validate with correct code
    print("\nStep 2: Validating OTP with correct code...")
    success = await test_validate_otp(otp_id, code, "test_user_12345")
    
    if success:
        print("✅ OTP validated successfully")
        return True
    else:
        print("❌ OTP validation failed")
        return False


async def run_all_tests():
    """Run all test scenarios."""
    print("\n")
    print("*" * 80)
    print(" OTP MICROSERVICE INTEGRATION TESTS ")
    print("*" * 80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    results = {}
    
    try:
        # Test 1: Health Check
        results["health_check"] = await test_health_check()
        
        # Test 2: Complete Flow
        results["complete_flow"] = await test_complete_flow()
        
        # Test 3: Invalid OTP
        print("\n")
        otp_id, code = await test_generate_otp()
        if otp_id:
            results["invalid_otp"] = await test_invalid_otp(otp_id, "test_user_12345")
        
        # Test 4: Max Attempts
        results["max_attempts"] = await test_max_attempts()
        
    except httpx.ConnectError:
        print("\n❌ ERROR: Could not connect to OTP microservice")
        print(f"   Make sure the service is running on {BASE_URL}")
        return
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
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
    print("\n🚀 Starting OTP Microservice Tests...")
    print("\nPrerequisites:")
    print("1. OTP microservice must be running on http://localhost:8003")
    print("2. PostgreSQL database must be running and initialized")
    print("3. Database migrations must be applied")
    
    input("\nPress Enter to continue with tests...")
    
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        exit(1)
