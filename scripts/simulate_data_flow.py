#!/usr/bin/env python3
"""
simulate_data_flow.py - Test data flows through the HealthData Gateway

This script simulates the complete data flow through the system,
from data ingestion from various sources to standardization, anonymization,
and consent management. Useful for testing and demonstrations.
"""

import os
import sys
import json
import time
import random
import requests
import logging
from datetime import datetime, timedelta

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import HealthData Gateway modules
from src.integration.client import HealthDataGatewayClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("data_flow_simulator")

# Sample data for simulation
SAMPLE_PATIENT_DATA = {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {
            "resource": {
                "resourceType": "Patient",
                "id": "patient123",
                "name": [{"given": ["John"], "family": "Doe"}],
                "gender": "male",
                "birthDate": "1970-01-01",
                "address": [
                    {
                        "line": ["123 Main St"],
                        "city": "Anytown",
                        "state": "CA",
                        "postalCode": "12345"
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": "555-123-4567",
                        "use": "home"
                    },
                    {
                        "system": "email",
                        "value": "john.doe@example.com"
                    }
                ]
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "id": "obs1",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8867-4",
                            "display": "Heart rate"
                        }
                    ]
                },
                "subject": {
                    "reference": "Patient/patient123"
                },
                "effectiveDateTime": (datetime.now() - timedelta(days=1)).isoformat(),
                "valueQuantity": {
                    "value": 80,
                    "unit": "beats/minute",
                    "system": "http://unitsofmeasure.org",
                    "code": "/min"
                }
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "id": "obs2",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic blood pressure"
                        }
                    ]
                },
                "subject": {
                    "reference": "Patient/patient123"
                },
                "effectiveDateTime": (datetime.now() - timedelta(days=1)).isoformat(),
                "valueQuantity": {
                    "value": 120,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mmHg"
                }
            }
        }
    ]
}

SAMPLE_PHARMACY_DATA = {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {
            "resource": {
                "resourceType": "MedicationDispense",
                "id": "med1",
                "medicationCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://www.nlm.nih.gov/rxnorm",
                            "code": "211307",
                            "display": "Lisinopril 10 MG Oral Tablet"
                        }
                    ]
                },
                "subject": {
                    "reference": "Patient/patient123"
                },
                "whenHandedOver": (datetime.now() - timedelta(days=14)).isoformat(),
                "daysSupply": {
                    "value": 30,
                    "unit": "days"
                },
                "quantity": {
                    "value": 30,
                    "unit": "tablets"
                }
            }
        }
    ]
}

SAMPLE_WEARABLE_DATA = {
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {
            "resource": {
                "resourceType": "Observation",
                "id": "steps1",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "41950-7",
                            "display": "Steps"
                        }
                    ]
                },
                "subject": {
                    "reference": "Patient/patient123"
                },
                "effectiveDateTime": (datetime.now() - timedelta(days=1)).isoformat(),
                "valueQuantity": {
                    "value": 8547,
                    "unit": "steps",
                    "system": "http://unitsofmeasure.org",
                    "code": "steps"
                }
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "id": "sleep1",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "93832-4",
                            "display": "Sleep duration"
                        }
                    ]
                },
                "subject": {
                    "reference": "Patient/patient123"
                },
                "effectiveDateTime": (datetime.now() - timedelta(days=1)).isoformat(),
                "valueQuantity": {
                    "value": 7.5,
                    "unit": "h",
                    "system": "http://unitsofmeasure.org",
                    "code": "h"
                }
            }
        }
    ]
}

def pretty_print(data):
    """Pretty print data as JSON"""
    print(json.dumps(data, indent=2))

def simulate_data_flow():
    """Simulate the complete data flow through HealthData Gateway"""
    
    logger.info("Starting HealthData Gateway data flow simulation")
    
    # Initialize the client
    client = HealthDataGatewayClient(base_url="http://localhost:8000")
    
    # Step 1: Authenticate
    logger.info("Authenticating with the API...")
    if not client.authenticate(username="demo", password="password"):
        logger.error("Authentication failed. Make sure the HealthData Gateway service is running.")
        return False
    
    # Step 2: Register patient consent
    patient_id = "patient123"
    requester = "healthdata_rewards_app"
    
    logger.info(f"Registering consent for {patient_id} to share data with {requester}")
    consent_result = client.grant_consent(patient_id, requester, duration_days=90)
    
    if "error" in consent_result:
        logger.error(f"Failed to register consent: {consent_result.get('error')}")
        logger.warning("Continuing simulation without consent (this would fail in production)")
    else:
        logger.info("Consent successfully registered")
        pretty_print(consent_result)
    
    # Step 3: Simulate hospital data ingestion
    logger.info("Simulating hospital data ingestion...")
    hospital_id = "epic"
    
    # In a real scenario, this would come from the actual hospital API
    # For this simulation, we use the sample data
    logger.info(f"Ingesting data for patient {patient_id} from hospital {hospital_id}")
    
    # Standardize the data
    logger.info("Standardizing hospital data to FHIR format...")
    # In production, this would call the standardization API
    standardized_hospital_data = SAMPLE_PATIENT_DATA
    
    logger.info("Hospital data standardized successfully")
    
    # Step 4: Simulate pharmacy data ingestion
    logger.info("Simulating pharmacy data ingestion...")
    pharmacy_id = "cvs"
    
    logger.info(f"Ingesting data for patient {patient_id} from pharmacy {pharmacy_id}")
    
    # Standardize the data
    logger.info("Standardizing pharmacy data to FHIR format...")
    # In production, this would call the standardization API
    standardized_pharmacy_data = SAMPLE_PHARMACY_DATA
    
    logger.info("Pharmacy data standardized successfully")
    
    # Step 5: Simulate wearable data ingestion
    logger.info("Simulating wearable data ingestion...")
    wearable_id = "fitbit"
    user_id = "user123"
    
    logger.info(f"Ingesting data for user {user_id} from wearable {wearable_id}")
    
    # Standardize the data
    logger.info("Standardizing wearable data to FHIR format...")
    # In production, this would call the standardization API
    standardized_wearable_data = SAMPLE_WEARABLE_DATA
    
    logger.info("Wearable data standardized successfully")
    
    # Step 6: Anonymize data for research purposes
    logger.info("Anonymizing patient data for research...")
    
    anonymized_data = client.anonymize_data(
        standardized_hospital_data, 
        preserve_age=True, 
        preserve_gender=True
    )
    
    if "error" in anonymized_data:
        logger.error(f"Failed to anonymize data: {anonymized_data.get('error')}")
    else:
        logger.info("Data anonymized successfully")
        logger.info("Sample of anonymized data:")
        pretty_print(anonymized_data)
    
    # Step 7: Aggregate data from multiple sources
    logger.info("Aggregating data from multiple sources...")
    
    # In production, this would call a data aggregation API
    # For this simulation, we just combine the samples
    
    # Create a timestamp for the aggregation
    aggregation_timestamp = datetime.now().isoformat()
    
    # Create an aggregated bundle with all the data
    aggregated_data = {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": aggregation_timestamp,
        "entry": (
            SAMPLE_PATIENT_DATA.get("entry", []) + 
            SAMPLE_PHARMACY_DATA.get("entry", []) + 
            SAMPLE_WEARABLE_DATA.get("entry", [])
        )
    }
    
    logger.info("Data aggregation complete")
    
    # Step 8: Calculate health metrics based on aggregated data
    logger.info("Calculating health metrics...")
    
    # In production, this would use a more sophisticated algorithm
    # For this simulation, we'll create a basic health score
    
    # Extract some values from the simulated data
    heart_rate = 80  # From sample data
    steps = 8547     # From sample data
    sleep_hours = 7.5  # From sample data
    systolic_bp = 120  # From sample data
    
    # Very basic scoring system (0-100)
    heart_rate_score = max(0, 100 - abs(heart_rate - 70))
    step_score = min(100, steps / 100)
    sleep_score = max(0, min(100, (sleep_hours / 8) * 100))
    bp_score = max(0, 100 - abs(systolic_bp - 115) / 2)
    
    # Overall health score (simple average)
    health_score = (heart_rate_score + step_score + sleep_score + bp_score) / 4
    
    logger.info(f"Calculated health metrics:")
    logger.info(f"Heart Rate Score: {heart_rate_score:.1f}")
    logger.info(f"Physical Activity Score: {step_score:.1f}")
    logger.info(f"Sleep Quality Score: {sleep_score:.1f}")
    logger.info(f"Blood Pressure Score: {bp_score:.1f}")
    logger.info(f"Overall Health Score: {health_score:.1f}")
    
    # Step 9: Simulate reward calculation based on data contribution
    logger.info("Calculating rewards for data contribution...")
    
    # In production, this would call the rewards contract
    # For this simulation, we'll calculate a basic reward
    
    # Example factors for reward calculation:
    # - Data freshness (newer data = more rewards)
    # - Data completeness (more data points = more rewards)
    # - Data sources (multiple sources = more rewards)
    
    days_since_last_contribution = 1  # Simulated
    num_data_points = len(aggregated_data.get("entry", []))
    num_data_sources = 3  # Hospital, pharmacy, wearable
    
    # Basic reward calculation
    freshness_factor = max(0, 10 - days_since_last_contribution) / 10
    completeness_factor = min(1, num_data_points / 20)
    source_factor = num_data_sources / 5
    
    # Final reward (could be tokens, points, etc.)
    reward_amount = 10 * (freshness_factor + completeness_factor + source_factor)
    
    logger.info(f"Calculated reward for data contribution: {reward_amount:.2f} tokens")
    
    # Step 10: Record the data flow for auditing purposes
    logger.info("Recording data flow for audit trail...")
    
    audit_record = {
        "timestamp": datetime.now().isoformat(),
        "patient_id": patient_id,
        "data_sources": ["hospital", "pharmacy", "wearable"],
        "requester": requester,
        "data_points": num_data_points,
        "anonymized": True,
        "reward_issued": reward_amount
    }
    
    # In production, this would be saved to a secure audit log
    # For simulation, we just print it
    logger.info("Audit record created:")
    pretty_print(audit_record)
    
    logger.info("Data flow simulation complete!")
    return True

if __name__ == "__main__":
    # Check if the server is running before starting simulation
    try:
        requests.get("http://localhost:8000/docs")
        simulate_data_flow()
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to HealthData Gateway server at http://localhost:8000")
        logger.error("Please start the server before running this simulation:")
        logger.error("    ./start.sh")
        sys.exit(1)
