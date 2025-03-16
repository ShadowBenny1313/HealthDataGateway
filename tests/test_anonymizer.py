"""
Tests for the health data anonymization functionality
"""

import unittest
import json
from src.ai.anonymizer import Anonymizer

class TestAnonymizer(unittest.TestCase):
    """Test cases for the data anonymization module"""
    
    def test_fhir_anonymization(self):
        """Test anonymization of FHIR data"""
        # Sample FHIR bundle
        fhir_bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient123",
                        "name": [
                            {
                                "use": "official",
                                "text": "Jane Smith",
                                "given": ["Jane"],
                                "family": "Smith"
                            }
                        ],
                        "birthDate": "1982-05-25",
                        "telecom": [
                            {
                                "system": "phone",
                                "value": "555-123-4567"
                            },
                            {
                                "system": "email",
                                "value": "jane.smith@example.com"
                            }
                        ],
                        "address": [
                            {
                                "line": ["123 Main St"],
                                "city": "Anytown",
                                "postalCode": "12345"
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
                            "text": "Blood Pressure"
                        },
                        "subject": {
                            "reference": "Patient/patient123"
                        },
                        "effectiveDateTime": "2023-05-01",
                        "valueString": "120/80 mmHg"
                    }
                }
            ]
        }
        
        # Create anonymizer instance
        anonymizer = Anonymizer(salt="test_salt")
        
        # Anonymize the data
        anonymized_data = anonymizer.anonymize_fhir(fhir_bundle)
        
        # Verify the patient identifiers are anonymized
        patient = anonymized_data["entry"][0]["resource"]
        self.assertNotEqual(patient["id"], "patient123")
        self.assertTrue(patient["id"].startswith("ID-"))
        
        # Verify name is anonymized
        self.assertNotEqual(patient["name"][0]["text"], "Jane Smith")
        self.assertTrue(patient["name"][0]["text"].startswith("Person-"))
        
        # Verify contact info is anonymized
        self.assertNotEqual(patient["telecom"][0]["value"], "555-123-4567")
        self.assertTrue(patient["telecom"][0]["value"].startswith("555-"))
        self.assertNotEqual(patient["telecom"][1]["value"], "jane.smith@example.com")
        self.assertTrue("@example.com" in patient["telecom"][1]["value"])
        
        # Verify address is anonymized
        self.assertNotEqual(patient["address"][0]["line"][0], "123 Main St")
        self.assertTrue(patient["address"][0]["line"][0].startswith("Address-"))
        
        # Verify observation reference is updated to match the new patient ID
        observation = anonymized_data["entry"][1]["resource"]
        self.assertEqual(observation["subject"]["reference"], f"Patient/{patient['id']}")
        
    def test_deterministic_anonymization(self):
        """Test that anonymization is deterministic (same input = same output)"""
        # Create test data with duplicate identifiers
        test_data = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient123",
                        "name": [{"text": "Test Patient"}]
                    }
                },
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": "obs1",
                        "subject": {"reference": "Patient/patient123"},
                        "performer": [{"reference": "Patient/patient123"}]
                    }
                }
            ]
        }
        
        # Create anonymizer with fixed salt for deterministic output
        anonymizer = Anonymizer(salt="test_salt")
        
        # Anonymize the data
        anonymized_data = anonymizer.anonymize_fhir(test_data)
        
        # Extract anonymized patient ID
        anon_patient_id = anonymized_data["entry"][0]["resource"]["id"]
        
        # Verify both references to the patient use the same anonymized ID
        observation = anonymized_data["entry"][1]["resource"]
        self.assertEqual(observation["subject"]["reference"], f"Patient/{anon_patient_id}")
        self.assertEqual(observation["performer"][0]["reference"], f"Patient/{anon_patient_id}")
        
        # Anonymize the original data again with the same salt
        anonymized_again = anonymizer.anonymize_fhir(test_data)
        
        # Verify the anonymized IDs are the same as the first run
        self.assertEqual(
            anonymized_again["entry"][0]["resource"]["id"], 
            anonymized_data["entry"][0]["resource"]["id"]
        )

if __name__ == "__main__":
    unittest.main()
