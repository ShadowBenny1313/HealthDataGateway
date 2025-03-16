"""
client_example.py - Example usage of the HealthData Gateway client

This example demonstrates how to use the HealthData Gateway client library
to interact with the Gateway API from another application.
"""

import json
import sys
import os
import logging
from typing import Dict, Any

# Add parent directory to path to allow importing the client
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the client
from src.integration.client import HealthDataGatewayClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("example_client")

def pretty_print(data: Dict[str, Any]) -> None:
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def main():
    """Main entry point for the example client"""
    # Create client instance
    client = HealthDataGatewayClient(base_url="http://localhost:8000")
    
    # Authenticate
    logger.info("Authenticating with the API...")
    if not client.authenticate(username="demo", password="password"):
        logger.error("Authentication failed")
        return
    
    logger.info("Authentication successful")
    
    # Example 1: List supported hospital systems
    logger.info("Retrieving supported hospital systems...")
    hospitals = client.list_hospitals()
    print("\nSupported Hospital Systems:")
    pretty_print(hospitals)
    
    # Example 2: Get patient data from a hospital
    hospital_id = "epic"
    patient_id = "patient123"
    logger.info(f"Retrieving patient data from {hospital_id} for {patient_id}...")
    
    patient_data = client.get_hospital_patient_data(hospital_id, patient_id)
    print(f"\nPatient Data from {hospital_id}:")
    pretty_print(patient_data)
    
    # Example 3: Get medication data for a patient
    pharmacy_id = "cvs"
    logger.info(f"Retrieving medication data from {pharmacy_id} for {patient_id}...")
    
    medication_data = client.get_pharmacy_patient_data(pharmacy_id, patient_id)
    print(f"\nMedication Data from {pharmacy_id}:")
    pretty_print(medication_data)
    
    # Example 4: Get wearable data
    wearable_id = "fitbit"
    user_id = "user123"
    logger.info(f"Retrieving health data from {wearable_id} for {user_id}...")
    
    wearable_data = client.get_wearable_user_data(wearable_id, user_id, days=14)
    print(f"\nWearable Data from {wearable_id}:")
    pretty_print(wearable_data)
    
    # Example 5: Get specific health metric
    metric = "heart_rate"
    logger.info(f"Retrieving {metric} data from {wearable_id} for {user_id}...")
    
    metric_data = client.get_wearable_metric(wearable_id, user_id, metric, days=7)
    print(f"\nHeart Rate Data from {wearable_id}:")
    pretty_print(metric_data)
    
    # Example 6: Grant consent for data access
    requester = "healthdata_rewards_app"
    logger.info(f"Granting consent for {requester} to access data for {patient_id}...")
    
    consent_result = client.grant_consent(patient_id, requester, duration_days=90)
    print("\nConsent Grant Result:")
    pretty_print(consent_result)
    
    # Example 7: Anonymize patient data for research
    logger.info("Anonymizing patient data...")
    anonymized_data = client.anonymize_data(patient_data, preserve_age=True, preserve_gender=True)
    print("\nAnonymized Patient Data:")
    pretty_print(anonymized_data)
    
    logger.info("Example client completed successfully")

if __name__ == "__main__":
    main()
