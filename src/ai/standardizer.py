"""
standardizer.py - AI-powered data standardization to FHIR format

This module contains functions to standardize health data from various sources
into FHIR (Fast Healthcare Interoperability Resources) format, using AI
to handle varying data structures and formats from different providers.
"""

import json
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ai.standardizer")

# FHIR resource types we support
SUPPORTED_FHIR_RESOURCES = [
    "Patient", 
    "Observation", 
    "MedicationStatement", 
    "MedicationRequest",
    "Condition",
    "AllergyIntolerance",
    "Procedure", 
    "Immunization",
    "DiagnosticReport"
]

class DataStandardizationError(Exception):
    """Exception raised for errors during data standardization process."""
    pass

def standardize_to_fhir(input_data: Dict[str, Any], source_type: str) -> Dict[str, Any]:
    """
    Convert input data from various sources to FHIR format
    
    Args:
        input_data: Raw data from the source system
        source_type: Type of source system (hospital, pharmacy, wearable)
        
    Returns:
        Dict containing data standardized to FHIR format
    """
    logger.info(f"Standardizing data from {source_type} source")
    
    # Select appropriate standardization method based on source type
    if source_type == "hospital":
        return _standardize_hospital_data(input_data)
    elif source_type == "pharmacy":
        return _standardize_pharmacy_data(input_data)
    elif source_type == "wearable":
        return _standardize_wearable_data(input_data)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")

def _standardize_hospital_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize hospital data to FHIR format
    
    In a real implementation, this would use more sophisticated mapping techniques,
    possibly including ML models to handle varied data formats.
    """
    try:
        # Create Patient resource
        patient = {
            "resourceType": "Patient",
            "id": data.get("patient_id", "unknown"),
            "meta": {
                "source": f"hospital/{data.get('hospital_id')}"
            },
            "name": [{
                "use": "official",
                "text": data.get("name", "Unknown Patient")
            }],
            "birthDate": data.get("dob"),
            "identifier": [{
                "system": "http://healthdatagateway.org/hospitals",
                "value": data.get("patient_id")
            }]
        }
        
        # Create resources for medical records
        resources = [patient]
        
        # Process medical records from the input data
        for record in data.get("medical_records", []):
            record_type = record.get("type")
            
            if record_type == "lab_result":
                observation = {
                    "resourceType": "Observation",
                    "id": f"{data.get('patient_id')}-lab-{len(resources)}",
                    "status": "final",
                    "code": {
                        "text": "Laboratory Result"
                    },
                    "subject": {
                        "reference": f"Patient/{data.get('patient_id')}"
                    },
                    "effectiveDateTime": record.get("date"),
                    "valueString": record.get("value")
                }
                resources.append(observation)
                
            elif record_type == "visit":
                encounter = {
                    "resourceType": "Encounter",
                    "id": f"{data.get('patient_id')}-visit-{len(resources)}",
                    "status": "finished",
                    "class": {
                        "code": "AMB",
                        "display": "ambulatory"
                    },
                    "subject": {
                        "reference": f"Patient/{data.get('patient_id')}"
                    },
                    "period": {
                        "start": record.get("date")
                    },
                    "reasonCode": [{
                        "text": record.get("notes")
                    }]
                }
                resources.append(encounter)
        
        # Create bundle containing all resources
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [{"resource": resource} for resource in resources]
        }
        
        return bundle
        
    except Exception as e:
        logger.error(f"Error standardizing hospital data: {str(e)}")
        raise DataStandardizationError(f"Failed to standardize hospital data: {str(e)}")

def _standardize_pharmacy_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize pharmacy data to FHIR format
    """
    try:
        # Create Patient resource
        patient = {
            "resourceType": "Patient",
            "id": data.get("patient_id", "unknown"),
            "meta": {
                "source": f"pharmacy/{data.get('pharmacy_id')}"
            },
            "identifier": [{
                "system": "http://healthdatagateway.org/pharmacies",
                "value": data.get("patient_id")
            }]
        }
        
        # Create resources for medications
        resources = [patient]
        
        # Process medications from the input data
        for medication in data.get("medications", []):
            med_statement = {
                "resourceType": "MedicationStatement",
                "id": f"{data.get('patient_id')}-med-{len(resources)}",
                "status": "active",
                "medication": {
                    "concept": {
                        "text": medication.get("name")
                    }
                },
                "subject": {
                    "reference": f"Patient/{data.get('patient_id')}"
                },
                "effectiveDateTime": medication.get("prescribed_date"),
                "dosage": [{
                    "text": f"{medication.get('dosage')} {medication.get('frequency')}",
                    "timing": {
                        "code": {
                            "text": medication.get("frequency")
                        }
                    },
                    "doseAndRate": [{
                        "doseQuantity": {
                            "value": medication.get("dosage").replace("mg", ""),
                            "unit": "mg"
                        }
                    }]
                }],
                "informationSource": {
                    "display": medication.get("prescribed_by")
                }
            }
            resources.append(med_statement)
        
        # Create bundle containing all resources
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [{"resource": resource} for resource in resources]
        }
        
        return bundle
        
    except Exception as e:
        logger.error(f"Error standardizing pharmacy data: {str(e)}")
        raise DataStandardizationError(f"Failed to standardize pharmacy data: {str(e)}")

def _standardize_wearable_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize wearable device data to FHIR format
    """
    try:
        # Create Patient resource
        patient = {
            "resourceType": "Patient",
            "id": data.get("user_id", "unknown"),
            "meta": {
                "source": f"wearable/{data.get('wearable_id')}"
            },
            "identifier": [{
                "system": "http://healthdatagateway.org/wearables",
                "value": data.get("user_id")
            }]
        }
        
        # Create resources for wearable data
        resources = [patient]
        
        # Process daily data from the input data
        for day_data in data.get("data", []):
            date = day_data.get("date")
            
            # Steps observation
            if "steps" in day_data:
                steps_obs = {
                    "resourceType": "Observation",
                    "id": f"{data.get('user_id')}-steps-{date}",
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "41950-7",
                            "display": "Number of steps in 24 hour Measured"
                        }]
                    },
                    "subject": {
                        "reference": f"Patient/{data.get('user_id')}"
                    },
                    "effectiveDateTime": date,
                    "valueQuantity": {
                        "value": day_data.get("steps"),
                        "unit": "steps",
                        "system": "http://unitsofmeasure.org",
                        "code": "steps"
                    },
                    "device": {
                        "display": data.get("device_type")
                    }
                }
                resources.append(steps_obs)
            
            # Heart rate observation
            if "heart_rate_avg" in day_data:
                hr_obs = {
                    "resourceType": "Observation",
                    "id": f"{data.get('user_id')}-heartrate-{date}",
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8867-4",
                            "display": "Heart rate"
                        }]
                    },
                    "subject": {
                        "reference": f"Patient/{data.get('user_id')}"
                    },
                    "effectiveDateTime": date,
                    "valueQuantity": {
                        "value": day_data.get("heart_rate_avg"),
                        "unit": "beats/minute",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min"
                    },
                    "device": {
                        "display": data.get("device_type")
                    }
                }
                resources.append(hr_obs)
                
            # Sleep observation
            if "sleep_hours" in day_data:
                sleep_obs = {
                    "resourceType": "Observation",
                    "id": f"{data.get('user_id')}-sleep-{date}",
                    "status": "final",
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "93832-4",
                            "display": "Sleep duration"
                        }]
                    },
                    "subject": {
                        "reference": f"Patient/{data.get('user_id')}"
                    },
                    "effectiveDateTime": date,
                    "valueQuantity": {
                        "value": day_data.get("sleep_hours"),
                        "unit": "h",
                        "system": "http://unitsofmeasure.org",
                        "code": "h"
                    },
                    "device": {
                        "display": data.get("device_type")
                    }
                }
                resources.append(sleep_obs)
        
        # Create bundle containing all resources
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [{"resource": resource} for resource in resources]
        }
        
        return bundle
        
    except Exception as e:
        logger.error(f"Error standardizing wearable data: {str(e)}")
        raise DataStandardizationError(f"Failed to standardize wearable data: {str(e)}")
