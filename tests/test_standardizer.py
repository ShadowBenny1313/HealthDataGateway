"""
Tests for the FHIR data standardization functionality
"""

import unittest
import json
from src.ai.standardizer import standardize_to_fhir

class TestStandardizer(unittest.TestCase):
    """Test cases for the data standardization module"""
    
    def test_hospital_data_standardization(self):
        """Test standardization of hospital data to FHIR format"""
        # Sample hospital data input
        hospital_data = {
            "hospital_id": "hospital123",
            "patient_id": "patient456",
            "name": "John Doe",
            "dob": "1980-01-15",
            "medical_records": [
                {"date": "2023-03-10", "type": "lab_result", "value": "normal"},
                {"date": "2023-04-05", "type": "visit", "notes": "Regular checkup"},
            ]
        }
        
        # Convert to FHIR
        fhir_data = standardize_to_fhir(hospital_data, "hospital")
        
        # Verify structure and content
        self.assertEqual(fhir_data["resourceType"], "Bundle")
        self.assertEqual(fhir_data["type"], "collection")
        
        # Should have 3 resources (1 Patient + 2 records)
        self.assertEqual(len(fhir_data["entry"]), 3)
        
        # First resource should be Patient
        patient = fhir_data["entry"][0]["resource"]
        self.assertEqual(patient["resourceType"], "Patient")
        self.assertEqual(patient["id"], "patient456")
        
    def test_pharmacy_data_standardization(self):
        """Test standardization of pharmacy data to FHIR format"""
        # Sample pharmacy data input
        pharmacy_data = {
            "pharmacy_id": "pharmacy789",
            "patient_id": "patient456",
            "medications": [
                {
                    "name": "Metformin",
                    "dosage": "500mg",
                    "frequency": "twice daily",
                    "prescribed_date": "2023-01-10",
                    "prescribed_by": "Dr. Smith"
                }
            ]
        }
        
        # Convert to FHIR
        fhir_data = standardize_to_fhir(pharmacy_data, "pharmacy")
        
        # Verify structure and content
        self.assertEqual(fhir_data["resourceType"], "Bundle")
        self.assertEqual(fhir_data["type"], "collection")
        
        # Should have 2 resources (1 Patient + 1 medication)
        self.assertEqual(len(fhir_data["entry"]), 2)
        
        # Second resource should be MedicationStatement
        med = fhir_data["entry"][1]["resource"]
        self.assertEqual(med["resourceType"], "MedicationStatement")
        self.assertEqual(med["subject"]["reference"], "Patient/patient456")
        
    def test_wearable_data_standardization(self):
        """Test standardization of wearable data to FHIR format"""
        # Sample wearable data input
        wearable_data = {
            "wearable_id": "fitbit",
            "user_id": "user123",
            "device_type": "Fitbit",
            "data": [
                {
                    "date": "2023-05-01",
                    "steps": 9500,
                    "heart_rate_avg": 72,
                    "sleep_hours": 7.5
                }
            ]
        }
        
        # Convert to FHIR
        fhir_data = standardize_to_fhir(wearable_data, "wearable")
        
        # Verify structure and content
        self.assertEqual(fhir_data["resourceType"], "Bundle")
        self.assertEqual(fhir_data["type"], "collection")
        
        # Should have 4 resources (1 Patient + 3 observations)
        self.assertEqual(len(fhir_data["entry"]), 4)
        
        # Verify patient ID
        patient = fhir_data["entry"][0]["resource"]
        self.assertEqual(patient["id"], "user123")

if __name__ == "__main__":
    unittest.main()
