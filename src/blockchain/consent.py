"""
consent.py - Python interface for blockchain-based consent management

This module provides functions to interact with the DataConsent smart contract
for verifying and managing patient consent for data access.
"""

import os
import json
import time
from typing import Dict, Any, Optional
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock implementation for development
# In production, this would connect to an actual blockchain network
MOCK_MODE = True

# Sample mock consent database for development
_mock_consent_db = {
    "patient123": {
        "requester_addr1": int(time.time()) + 86400*30,  # 30 days from now
        "requester_addr2": int(time.time()) - 86400,     # Expired 1 day ago
    },
    "patient456": {
        "requester_addr1": int(time.time()) + 86400*7,   # 7 days from now
    }
}

def _get_contract():
    """
    Initialize and return the Web3 contract instance
    """
    if MOCK_MODE:
        return None
        
    # In production mode, connect to blockchain
    blockchain_url = os.getenv("BLOCKCHAIN_URL", "http://localhost:8545")
    contract_address = os.getenv("CONSENT_CONTRACT_ADDRESS")
    contract_abi_path = os.getenv("CONSENT_CONTRACT_ABI", "../blockchain/consent_abi.json")
    
    # Initialize Web3 connection
    web3 = Web3(Web3.HTTPProvider(blockchain_url))
    
    # Load contract ABI
    with open(contract_abi_path, 'r') as abi_file:
        contract_abi = json.load(abi_file)
    
    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    
    return contract

def verify_consent(patient_id: str, token_or_requester: str) -> bool:
    """
    Verify if the requester has valid consent to access patient data
    
    Args:
        patient_id: The patient's unique identifier
        token_or_requester: Either a JWT token containing requester info,
                            or the requester's address/identifier
    
    Returns:
        bool: True if consent exists and is valid, False otherwise
    """
    # Extract requester from token if needed
    # In a real implementation, we would decode the JWT token to extract the requester ID
    # For simplicity in this implementation, we assume token_or_requester is the requester ID
    requester = token_or_requester
    
    if MOCK_MODE:
        # Use mock consent database
        if patient_id in _mock_consent_db:
            if requester in _mock_consent_db[patient_id]:
                # Check if consent is still valid (not expired)
                expiration = _mock_consent_db[patient_id][requester]
                return expiration > int(time.time())
        return False
    else:
        # Use blockchain contract
        contract = _get_contract()
        if not contract:
            raise RuntimeError("Failed to initialize blockchain contract")
            
        # Call the consent verification function on the blockchain
        return contract.functions.hasValidConsent(patient_id, requester).call()


def verify_admin_role(token: str) -> bool:
    """
    Verify if the user has admin role/permissions
    
    Args:
        token: JWT token containing user info and roles
        
    Returns:
        bool: True if user has admin role, False otherwise
    """
    # Check if we're in testing mode
    admin_test_mode = os.getenv("ADMIN_TEST_MODE", "False").lower() == "true"
    
    # For testing, accept specific test tokens
    if admin_test_mode or MOCK_MODE:
        # Accept test tokens for automated tests
        if token in ["admin_test_token", "test_admin_token"]:
            return True
    
    # For production, decode the JWT token and verify admin role
    import jwt
    
    try:
        # Decode the JWT token
        secret_key = os.getenv("JWT_SECRET_KEY", "development_secret_key")
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # Check if user has admin role
        if "roles" in decoded_token and "admin" in decoded_token["roles"]:
            return True
            
        return False
    except Exception as e:
        print(f"Error verifying admin role: {e}")
        return False
    



def grant_consent(patient_id: str, requester: str, duration_days: int = 30) -> bool:
    """
    Grant consent for a requester to access patient data
    
    Args:
        patient_id: The patient's unique identifier
        requester: The requester's address/identifier
        duration_days: Number of days the consent remains valid
    
    Returns:
        bool: True if consent was successfully granted
    """
    if MOCK_MODE:
        # Update mock consent database
        if patient_id not in _mock_consent_db:
            _mock_consent_db[patient_id] = {}
        
        expiration = int(time.time()) + (86400 * duration_days)
        _mock_consent_db[patient_id][requester] = expiration
        return True
    
    # Real blockchain implementation
    contract = _get_contract()
    if not contract:
        raise Exception("Failed to initialize contract")
    
    # Get account to send transaction from
    account = os.getenv("BLOCKCHAIN_ACCOUNT")
    private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
    
    # Build transaction
    tx = contract.functions.grantConsent(patient_id, requester, duration_days).build_transaction({
        'from': account,
        'nonce': Web3.eth.get_transaction_count(account),
    })
    
    # Sign and send transaction
    signed_tx = Web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = Web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Wait for transaction receipt
    receipt = Web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return receipt.status == 1

def revoke_consent(patient_id: str, requester: str) -> bool:
    """
    Revoke previously granted consent
    
    Args:
        patient_id: The patient's unique identifier
        requester: The requester's address/identifier
    
    Returns:
        bool: True if consent was successfully revoked
    """
    if MOCK_MODE:
        # Update mock consent database
        if patient_id in _mock_consent_db and requester in _mock_consent_db[patient_id]:
            # Set expiration to a time in the past
            _mock_consent_db[patient_id][requester] = int(time.time()) - 1
            return True
        return False
    
    # Real blockchain implementation
    contract = _get_contract()
    if not contract:
        raise Exception("Failed to initialize contract")
    
    # Get account to send transaction from
    account = os.getenv("BLOCKCHAIN_ACCOUNT")
    private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
    
    # Build transaction
    tx = contract.functions.revokeConsent(patient_id, requester).build_transaction({
        'from': account,
        'nonce': Web3.eth.get_transaction_count(account),
    })
    
    # Sign and send transaction
    signed_tx = Web3.eth.account.sign_transaction(tx, private_key)
    tx_hash = Web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    # Wait for transaction receipt
    receipt = Web3.eth.wait_for_transaction_receipt(tx_hash)
    
    return receipt.status == 1

def get_consent_expiration(patient_id: str, requester: str) -> Optional[int]:
    """
    Get the expiration timestamp for a consent record
    
    Args:
        patient_id: The patient's unique identifier
        requester: The requester's address/identifier
    
    Returns:
        int: Timestamp when consent expires, or None if no consent exists
    """
    if MOCK_MODE:
        # Check mock consent database
        if patient_id in _mock_consent_db and requester in _mock_consent_db[patient_id]:
            return _mock_consent_db[patient_id][requester]
        return None
    
    # Real blockchain implementation
    contract = _get_contract()
    if not contract:
        raise Exception("Failed to initialize contract")
    
    # Call the smart contract to get expiration
    expiration = contract.functions.getConsentExpiration(patient_id, requester).call()
    
    return expiration if expiration > 0 else None


def get_user_consents(patient_id: str) -> Dict[str, int]:
    """
    Get all active consents for a specific patient/user
    
    Args:
        patient_id: The patient's unique identifier
        
    Returns:
        Dict[str, int]: Dictionary of requester IDs to expiration timestamps
    """
    # Check if in mock mode
    if MOCK_MODE:
        # Return data from mock consent database
        if patient_id in _mock_consent_db:
            # Filter only active consents (expiration > current time)
            current_time = int(time.time())
            return {requester: expiration 
                   for requester, expiration in _mock_consent_db[patient_id].items()
                   if expiration > current_time}
        return {}
    
    # Real blockchain implementation
    contract = _get_contract()
    if not contract:
        raise Exception("Failed to initialize contract")
    
    # Call the smart contract to get all consents for the patient
    # Note: In a real implementation, this would call a smart contract function
    # that returns all active consents for a patient
    requesters = contract.functions.getPatientRequesters(patient_id).call()
    
    # Get expiration for each requester
    consents = {}
    for requester in requesters:
        expiration = contract.functions.getConsentExpiration(patient_id, requester).call()
        if expiration > 0 and expiration > int(time.time()):
            consents[requester] = expiration
    
    return consents
