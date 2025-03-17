"""
Blockchain Rewards Module for HealthData Gateway

This module handles interaction with the HealthData Rewards smart contract,
allowing users to earn tokens for sharing health data and contributing to research.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from web3 import Web3
from web3.exceptions import ContractLogicError
from hexbytes import HexBytes
from eth_account import Account
from eth_utils import to_checksum_address
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("blockchain_rewards")

# Load blockchain configuration from environment
BLOCKCHAIN_PROVIDER_URL = os.getenv("BLOCKCHAIN_PROVIDER_URL", "http://localhost:8545")
REWARDS_CONTRACT_ADDRESS = os.getenv("REWARDS_CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")
REWARDS_CONTRACT_ABI_PATH = os.getenv("REWARDS_CONTRACT_ABI_PATH", "src/blockchain/abi/rewards_abi.json")
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY", "")

# Initialize Web3 connection
w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_PROVIDER_URL))

# Load contract ABI
try:
    with open(REWARDS_CONTRACT_ABI_PATH, 'r') as abi_file:
        contract_abi = json.load(abi_file)
except FileNotFoundError:
    logger.warning(f"Rewards ABI file not found at {REWARDS_CONTRACT_ABI_PATH}. Using placeholder ABI.")
    # Placeholder ABI for development
    contract_abi = [
        {
            "inputs": [
                {"name": "userId", "type": "string"},
                {"name": "dataType", "type": "string"},
                {"name": "dataPoints", "type": "uint256"}
            ],
            "name": "issueReward",
            "outputs": [{"name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "userId", "type": "string"}],
            "name": "getRewardBalance",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]

# Initialize contract
try:
    rewards_contract = w3.eth.contract(
        address=to_checksum_address(REWARDS_CONTRACT_ADDRESS),
        abi=contract_abi
    )
    logger.info("Rewards contract initialized")
except Exception as e:
    logger.error(f"Failed to initialize rewards contract: {str(e)}")
    rewards_contract = None


def issue_reward(user_id: str, data_type: str, data_points: int) -> Dict[str, Any]:
    """
    Issue rewards to a user for sharing health data.
    
    Args:
        user_id: User ID to issue rewards to
        data_type: Type of data shared (hospital, pharmacy, wearable)
        data_points: Number of data points shared
    
    Returns:
        Dictionary containing transaction details or error message
    """
    if rewards_contract is None:
        logger.error("Rewards contract not initialized")
        return {"success": False, "error": "Contract not initialized"}
    
    if not user_id:
        return {"success": False, "error": "User ID cannot be empty"}
    
    if data_points <= 0:
        return {"success": False, "error": "Data points must be greater than zero"}
    
    # Input validation for data_type
    valid_data_types = ["hospital", "pharmacy", "wearable"]
    if data_type not in valid_data_types:
        return {"success": False, "error": f"Invalid data type. Must be one of: {', '.join(valid_data_types)}"}
    
    try:
        # For development/testing, we'll simulate blockchain interaction
        # This would be a real blockchain transaction in production
        if ADMIN_PRIVATE_KEY and w3.is_connected():
            # Get admin account
            admin_account = Account.from_key(ADMIN_PRIVATE_KEY)
            admin_address = admin_account.address
            
            # Build transaction
            tx = rewards_contract.functions.issueReward(
                user_id,
                data_type,
                data_points
            ).build_transaction({
                'from': admin_address,
                'nonce': w3.eth.get_transaction_count(admin_address),
                'gas': 200000,
                'gasPrice': w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = w3.eth.account.sign_transaction(tx, ADMIN_PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            result = {
                "success": tx_receipt.status == 1,
                "transaction_hash": HexBytes(tx_hash).hex(),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "reward_points": data_points
            }
            
            logger.info(f"Reward issued to {user_id} for {data_points} {data_type} data points - TX: {result['transaction_hash']}")
            return result
        else:
            # For development/testing without blockchain
            logger.info(f"Simulating reward issuance to {user_id} for {data_points} {data_type} data points")
            return {
                "success": True,
                "simulated": True,
                "transaction_hash": "0x" + "0" * 64,  # Dummy transaction hash
                "reward_points": data_points
            }
    
    except ContractLogicError as e:
        # Contract logic error (e.g., user not registered)
        logger.error(f"Contract logic error issuing reward: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        # Other errors
        logger.error(f"Error issuing reward: {str(e)}")
        return {"success": False, "error": str(e)}


def get_reward_balance(user_id: str) -> Dict[str, Any]:
    """
    Get the reward balance for a specific user.
    
    Args:
        user_id: User ID to check balance for
    
    Returns:
        Dictionary containing balance information or error message
    """
    if rewards_contract is None:
        logger.error("Rewards contract not initialized")
        return {"success": False, "error": "Contract not initialized"}
    
    if not user_id:
        return {"success": False, "error": "User ID cannot be empty"}
    
    try:
        # For development/testing, we'll simulate blockchain interaction
        # This would be a real blockchain query in production
        if w3.is_connected():
            # Call the contract
            balance = rewards_contract.functions.getRewardBalance(user_id).call()
            
            result = {
                "success": True,
                "user_id": user_id,
                "balance": balance
            }
            
            logger.info(f"Reward balance retrieved for {user_id}: {balance} tokens")
            return result
        else:
            # For development/testing without blockchain
            logger.info(f"Simulating reward balance retrieval for {user_id}")
            # Generate a deterministic balance based on user_id to ensure consistent results
            import hashlib
            # Using SHA-256 instead of MD5 for stronger cryptographic security
            hash_val = int(hashlib.sha256(user_id.encode()).hexdigest(), 16) % 1000
            return {
                "success": True,
                "simulated": True,
                "user_id": user_id,
                "balance": hash_val
            }
    
    except ContractLogicError as e:
        # Contract logic error
        logger.error(f"Contract logic error getting balance: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        # Other errors
        logger.error(f"Error getting balance: {str(e)}")
        return {"success": False, "error": str(e)}


def validate_rewards_contract() -> bool:
    """
    Validate that the rewards contract is properly configured and accessible.
    
    Returns:
        True if contract is valid and accessible, False otherwise
    """
    if rewards_contract is None:
        return False
    
    try:
        # Try a simple call to verify contract
        # This depends on what functions are available on your contract
        method_list = [fn for fn in rewards_contract.functions]
        if 'issueReward' in method_list or 'getRewardBalance' in method_list:
            logger.info("Rewards contract validated successfully")
            return True
        else:
            logger.warning("Rewards contract does not have expected methods")
            return False
    except Exception as e:
        logger.error(f"Error validating rewards contract: {str(e)}")
        return False
