#!/usr/bin/env python3
"""
Simple test script for HealthData Gateway core functions.
This script directly tests the key components without relying on the API server.
"""

import sys
import json
from src.blockchain.consent import verify_consent, grant_consent
from src.ai.standardizer import standardize_to_fhir
from src.ai.anonymizer import Anonymizer
from src.api.hospitals import retrieve_from_hospital_system
from src.api.pharmacies import retrieve_from_pharmacy_system
from src.api.wearables import retrieve_from_wearable_system
from src.integrations.healthdata_rewards import sync_data_sharing_rewards, get_user_reward_balance

def test_consent_management():
    """Test the consent management system including granting, verifying, and revoking consent"""
    print("\n===== Testing Consent Management =====")
    all_tests_passed = True
    
    # Test 1: Grant consent
    print("\nTest 1: Granting consent")
    patient_id = "patient123"
    requester = "test_requester"
    result = grant_consent(patient_id, requester, 30)
    print(f"  Grant consent result: {result}")
    if not result:
        print("  [FAIL] Failed to grant consent")
        all_tests_passed = False
    else:
        print("  [PASS] Successfully granted consent")
    
    # Test 2: Verify consent - should be valid
    print("\nTest 2: Verifying valid consent")
    has_consent = verify_consent(patient_id, requester)
    print(f"  Verify consent result: {has_consent}")
    if not has_consent:
        print("  [FAIL] Consent verification failed when it should have passed")
        all_tests_passed = False
    else:
        print("  [PASS] Successfully verified consent")
    
    # Test 3: Verify consent for incorrect requester - should fail
    print("\nTest 3: Verifying consent with wrong requester")
    wrong_requester = "wrong_requester"
    has_wrong_consent = verify_consent(patient_id, wrong_requester)
    print(f"  Verify wrong consent result: {has_wrong_consent}")
    if has_wrong_consent:
        print("  [FAIL] Consent verification passed when it should have failed")
        all_tests_passed = False
    else:
        print("  [PASS] Successfully rejected unauthorized requester")
    
    # Test 4: Revoke consent
    from src.blockchain.consent import revoke_consent
    print("\nTest 4: Revoking consent")
    revoke_result = revoke_consent(patient_id, requester)
    print(f"  Revoke consent result: {revoke_result}")
    if not revoke_result:
        print("  [FAIL] Failed to revoke consent")
        all_tests_passed = False
    else:
        print("  [PASS] Successfully revoked consent")
    
    # Test 5: Verify consent after revocation - should fail
    print("\nTest 5: Verifying consent after revocation")
    has_consent_after_revoke = verify_consent(patient_id, requester)
    print(f"  Verify consent after revoke: {has_consent_after_revoke}")
    if has_consent_after_revoke:
        print("  [FAIL] Consent verification passed when it should have failed after revocation")
        all_tests_passed = False
    else:
        print("  [PASS] Successfully confirmed consent was revoked")
    
    # Overall result
    if all_tests_passed:
        print("\n✅ All consent management tests PASSED")
    else:
        print("\n❌ Some consent management tests FAILED")
    
    return all_tests_passed

def test_data_retrieval():
    """Test data retrieval from different sources"""
    print("\n===== Testing Data Retrieval =====")
    
    # Hospital data
    print("\nHospital data:")
    hospital_data = retrieve_from_hospital_system("epic", "patient123")
    print(json.dumps(hospital_data, indent=2))
    
    # Pharmacy data
    print("\nPharmacy data:")
    pharmacy_data = retrieve_from_pharmacy_system("cvs", "patient123")
    print(json.dumps(pharmacy_data, indent=2))
    
    # Wearable data
    print("\nWearable data:")
    wearable_data = retrieve_from_wearable_system("fitbit", "user123", 7)
    print(json.dumps(wearable_data, indent=2))
    
    return hospital_data, pharmacy_data, wearable_data

def test_standardization():
    """Test data standardization to FHIR"""
    print("\n===== Testing Standardization =====")
    
    # Get data from different sources
    hospital_data = retrieve_from_hospital_system("epic", "patient123")
    pharmacy_data = retrieve_from_pharmacy_system("cvs", "patient123")
    wearable_data = retrieve_from_wearable_system("fitbit", "user123", 7)
    
    # Standardize to FHIR
    hospital_fhir = standardize_to_fhir(hospital_data, "hospital")
    pharmacy_fhir = standardize_to_fhir(pharmacy_data, "pharmacy")
    wearable_fhir = standardize_to_fhir(wearable_data, "wearable")
    
    print("\nHospital FHIR data (sample):")
    print(json.dumps(hospital_fhir["entry"][0] if "entry" in hospital_fhir else hospital_fhir, indent=2))
    
    return hospital_fhir, pharmacy_fhir, wearable_fhir

def test_anonymization():
    """Test data anonymization"""
    print("\n===== Testing Anonymization =====")
    
    # Get standardized data
    hospital_data = retrieve_from_hospital_system("epic", "patient123")
    fhir_data = standardize_to_fhir(hospital_data, "hospital")
    
    # Anonymize data
    anonymizer = Anonymizer()
    anonymized_data = anonymizer.anonymize(fhir_data)
    
    print("\nAnonymized FHIR data (sample):")
    print(json.dumps(anonymized_data["entry"][0] if "entry" in anonymized_data else anonymized_data, indent=2))
    
    return anonymized_data

def test_provider_registry():
    """Test the provider registry functionality including registration requests and admin approval"""
    print("\n===== Testing Provider Registry =====")
    all_tests_passed = True
    
    try:
        # Import necessary modules
        import asyncio
        from src.models.provider_registry import ProviderRegistrationRequest, ProviderType, ProviderStatus, ContactInfo
        from src.api.provider_registry import register_provider, get_pending_requests, approve_provider
        from src.blockchain.consent import verify_admin_role
        
        # Create API request model for FastAPI endpoints
        test_request = ProviderRegistrationRequest(
            # Required ProviderBase fields
            name="Memorial Hospital",
            type=ProviderType.HOSPITAL,
            description="Regional hospital with comprehensive care services",
            # Required ContactInfo field
            contact=ContactInfo(
                name="John Smith",
                email="admin@memorial-hospital.org",
                phone="555-123-4567"
            ),
            # Required ProviderRegistrationRequest fields
            submitted_by="test_admin_user"
        )
        
        # Mock OAuth token for testing
        mock_token = "admin_test_token"  # This token is accepted in verify_admin_role when in test mode
        
        # Use python's asyncio to run the coroutines
        loop = asyncio.get_event_loop()
        
        # Test 1: Create provider registration request
        print("\nTest 1: Creating provider registration request")
        # Register the provider and get the response
        response = loop.run_until_complete(register_provider(request=test_request, token=mock_token))
        request_id = response.get("id", None) if isinstance(response, dict) else None
        
        print(f"  Provider registration request ID: {request_id if request_id else 'None'}")
        if not request_id:
            print("  [FAIL] Failed to create provider registration request")
            all_tests_passed = False
        else:
            print("  [PASS] Successfully created provider registration request")
        
        # Test 2: Get pending registration requests
        print("\nTest 2: Getting pending registration requests")
        pending_requests_response = loop.run_until_complete(get_pending_requests(token=mock_token))
        provider_requests = pending_requests_response.get("provider_requests", [])
        print(f"  Number of pending requests: {len(provider_requests)}")
        if not provider_requests:
            print("  [FAIL] No pending requests found")
            all_tests_passed = False
        else:
            print("  [PASS] Successfully retrieved pending requests")
            has_new_request = False
            for req in provider_requests:
                # Handle both dictionary and Pydantic model cases
                if isinstance(req, dict) and req.get("name") == test_request.name:
                    has_new_request = True
                elif hasattr(req, "name") and req.name == test_request.name:
                    has_new_request = True
            if not has_new_request:
                print("  [FAIL] New request not found in pending requests")
                all_tests_passed = False
        
        # Test 3: Admin approval of provider registration
        print("\nTest 3: Admin approval of provider registration")
        admin_token = "admin_test_token"  # In a real scenario, this would be a valid admin JWT token
        
        # Make sure we have a valid request_id
        if request_id:
            try:
                # Run the async function using asyncio
                approval_result = loop.run_until_complete(approve_provider(request_id=request_id, token=admin_token))
                print(f"  Approval result: {approval_result}")
                if not approval_result:
                    print("  [FAIL] Failed to approve provider registration")
                    all_tests_passed = False
                else:
                    print("  [PASS] Successfully approved provider registration")
            except Exception as e:
                print(f"  [ERROR] Exception during provider approval: {str(e)}")
                all_tests_passed = False
        else:
            print("  [SKIP] Skipping approval test since no valid request ID was created")
        
    except Exception as e:
        print(f"  [ERROR] Exception during provider registry testing: {str(e)}")
        all_tests_passed = False
    
    # Overall result
    if all_tests_passed:
        print("\n✅ All provider registry tests PASSED")
    else:
        print("\n❌ Some provider registry tests FAILED")
    
    return all_tests_passed

def test_healthdata_rewards():
    """Test the HealthData Rewards integration"""
    print("\n==========================================")
    print("Testing HealthData Rewards Integration")
    print("==========================================")
    all_tests_passed = True
    
    # Test 1: Issue rewards for hospital data sharing
    print("\nTest 1: Issuing rewards for hospital data sharing")
    user_id = "patient123"  # Use same ID as in consent tests for consistency
    data_type = "hospital"
    data_points = 10
    
    try:
        result = sync_data_sharing_rewards(user_id, data_type, data_points)
        print(f"  Reward issuance result: {result}")
        if not result:
            print("  ❌ Failed to issue rewards for hospital data")
            all_tests_passed = False
        else:
            print("  ✅ Successfully issued rewards for hospital data")
    except Exception as e:
        print(f"  ❌ Exception occurred: {str(e)}")
        all_tests_passed = False
    
    # Test 2: Issue rewards for wearable data sharing
    print("\nTest 2: Issuing rewards for wearable data sharing")
    data_type = "wearable"
    data_points = 7  # 7 days of data
    
    try:
        result = sync_data_sharing_rewards(user_id, data_type, data_points)
        print(f"  Reward issuance result: {result}")
        if not result:
            print("  ❌ Failed to issue rewards for wearable data")
            all_tests_passed = False
        else:
            print("  ✅ Successfully issued rewards for wearable data")
    except Exception as e:
        print(f"  ❌ Exception occurred: {str(e)}")
        all_tests_passed = False
    
    # Test 3: Check user reward balance
    print("\nTest 3: Checking user reward balance")
    
    try:
        balance = get_user_reward_balance(user_id)
        print(f"  User balance: {balance}")
        if not balance:
            print("  ❌ Failed to retrieve user balance")
            all_tests_passed = False
        else:
            print("  ✅ Successfully retrieved user balance")
            print(f"    Tokens: {balance.get('tokens', 0)}")
            print(f"    Data contributions: {balance.get('data_contributions', 0)}")
    except Exception as e:
        print(f"  ❌ Exception occurred: {str(e)}")
        all_tests_passed = False
    
    # Summary
    if all_tests_passed:
        print("\n✅ All HealthData Rewards tests PASSED")
    else:
        print("\n❌ Some HealthData Rewards tests FAILED")
    
    return all_tests_passed

def main():
    """Main test function"""
    print("==========================================")
    print("HealthData Gateway Core Functionality Test")
    print("==========================================")
    
    # Test consent management
    consent_result = test_consent_management()
    
    # Test data retrieval
    hospital_data, pharmacy_data, wearable_data = test_data_retrieval()
    
    # Test standardization
    hospital_fhir, pharmacy_fhir, wearable_fhir = test_standardization()
    
    # Test anonymization
    anonymized_data = test_anonymization()
    
    # Test provider registry functionality
    provider_registry_result = test_provider_registry()
    
    # Test HealthData Rewards integration
    rewards_result = test_healthdata_rewards()
    
    print("\n==========================================")
    print("Test Summary:")
    print(f"- Consent management: {'PASSED' if consent_result else 'FAILED'}")
    print(f"- Data retrieval: {'PASSED' if all([hospital_data, pharmacy_data, wearable_data]) else 'FAILED'}")
    print(f"- Data standardization: {'PASSED' if all([hospital_fhir, pharmacy_fhir, wearable_fhir]) else 'FAILED'}")
    print(f"- Data anonymization: {'PASSED' if anonymized_data else 'FAILED'}")
    print(f"- Provider registry: {'PASSED' if provider_registry_result else 'FAILED'}")
    print(f"- HealthData Rewards: {'PASSED' if rewards_result else 'FAILED'}")
    print("=================================================")

if __name__ == "__main__":
    main()
