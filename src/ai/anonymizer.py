"""
anonymizer.py - AI-powered health data anonymization

This module contains functions to anonymize health data while preserving
its analytical value, using advanced AI techniques to identify and replace
personally identifiable information (PII) with synthetic equivalents.
"""

import json
import hashlib
import re
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ai.anonymizer")

# Types of PII that we can anonymize
PII_TYPES = [
    "NAME", 
    "ID", 
    "DOB", 
    "ADDRESS", 
    "PHONE", 
    "EMAIL", 
    "SSN"
]

class AnonymizationError(Exception):
    """Exception raised for errors during data anonymization process."""
    pass

class Anonymizer:
    """
    Class for anonymizing health data while preserving its utility for analysis.
    Uses deterministic methods to ensure consistent anonymization across datasets.
    """
    
    def __init__(self, salt: str = None, preserve_age: bool = True, preserve_gender: bool = True):
        """
        Initialize the anonymizer with optional settings
        
        Args:
            salt: A salt string to use for hashing. If None, a random one will be generated.
            preserve_age: Whether to preserve patient age (range) in anonymized data
            preserve_gender: Whether to preserve patient gender in anonymized data
        """
        self.salt = salt or str(uuid.uuid4())
        self.preserve_age = preserve_age
        self.preserve_gender = preserve_gender
        
        # PII lookup stores the mapping of original values to anonymized values
        # for consistent anonymization across multiple calls
        self.pii_lookup = {}
        
    def anonymize_fhir(self, fhir_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize a FHIR bundle while preserving its structure and clinical value
        
        Args:
            fhir_bundle: A FHIR bundle containing patient data
            
        Returns:
            Anonymized FHIR bundle
        """
        logger.info("Anonymizing FHIR bundle")
        
        try:
            # Create a deep copy to avoid modifying the original
            anonymized_bundle = json.loads(json.dumps(fhir_bundle))
            
            # Process each entry in the bundle
            for entry in anonymized_bundle.get("entry", []):
                resource = entry.get("resource", {})
                resource_type = resource.get("resourceType")
                
                # Anonymize based on resource type
                if resource_type == "Patient":
                    self._anonymize_patient(resource)
                elif resource_type == "Observation":
                    self._anonymize_observation(resource)
                elif resource_type == "MedicationStatement":
                    self._anonymize_medication_statement(resource)
                elif resource_type == "Encounter":
                    self._anonymize_encounter(resource)
                # Add more resource types as needed
            
            return anonymized_bundle
            
        except Exception as e:
            logger.error(f"Error anonymizing FHIR bundle: {str(e)}")
            raise AnonymizationError(f"Failed to anonymize FHIR bundle: {str(e)}")
    
    def _anonymize_patient(self, patient: Dict[str, Any]) -> None:
        """
        Anonymize a Patient resource in-place
        """
        # Anonymize patient ID
        original_id = patient.get("id")
        if original_id:
            patient["id"] = self._anonymize_identifier(original_id, "ID")
            
            # Update all references to this patient in the lookup table
            self.pii_lookup[f"Patient/{original_id}"] = f"Patient/{patient['id']}"
        
        # Anonymize identifiers
        if "identifier" in patient:
            for identifier in patient["identifier"]:
                if "value" in identifier:
                    identifier["value"] = self._anonymize_identifier(
                        identifier["value"], 
                        "ID"
                    )
        
        # Anonymize names
        if "name" in patient:
            for name in patient["name"]:
                if "given" in name:
                    name["given"] = [self._anonymize_identifier(given, "NAME") 
                                     for given in name.get("given", [])]
                if "family" in name:
                    name["family"] = self._anonymize_identifier(name["family"], "NAME")
                if "text" in name:
                    name["text"] = self._anonymize_identifier(name["text"], "NAME")
        
        # Anonymize contact information
        if "telecom" in patient:
            for telecom in patient["telecom"]:
                if telecom.get("system") == "phone" and "value" in telecom:
                    telecom["value"] = self._anonymize_identifier(telecom["value"], "PHONE")
                elif telecom.get("system") == "email" and "value" in telecom:
                    telecom["value"] = self._anonymize_identifier(telecom["value"], "EMAIL")
        
        # Modify DOB while preserving age if requested
        if "birthDate" in patient and self.preserve_age:
            # Parse original date
            original_date = datetime.strptime(patient["birthDate"], "%Y-%m-%d")
            
            # Add a small random offset (up to ±30 days) but keep year the same
            # to preserve age while obscuring exact birthdate
            day_offset = random.randint(-30, 30)
            new_date = original_date + timedelta(days=day_offset)
            
            # Make sure we keep the original year to preserve age
            if new_date.year != original_date.year:
                new_date = new_date.replace(year=original_date.year)
                
            patient["birthDate"] = new_date.strftime("%Y-%m-%d")
        elif "birthDate" in patient and not self.preserve_age:
            # Remove birthDate entirely if not preserving age
            del patient["birthDate"]
        
        # Anonymize address
        if "address" in patient:
            for address in patient["address"]:
                if "line" in address:
                    address["line"] = [self._anonymize_identifier(line, "ADDRESS") 
                                       for line in address.get("line", [])]
                if "city" in address:
                    address["city"] = self._anonymize_identifier(address["city"], "ADDRESS")
                if "postalCode" in address:
                    address["postalCode"] = self._anonymize_identifier(address["postalCode"], "ADDRESS")
    
    def _anonymize_observation(self, observation: Dict[str, Any]) -> None:
        """
        Anonymize an Observation resource in-place
        """
        # Anonymize ID
        if "id" in observation:
            observation["id"] = self._anonymize_identifier(observation["id"], "ID")
        
        # Update subject reference if it exists
        if "subject" in observation and "reference" in observation["subject"]:
            original_ref = observation["subject"]["reference"]
            if original_ref in self.pii_lookup:
                observation["subject"]["reference"] = self.pii_lookup[original_ref]
        
        # Any performer references would also need to be updated similarly
        if "performer" in observation:
            for performer in observation["performer"]:
                if "reference" in performer:
                    original_ref = performer["reference"]
                    if original_ref in self.pii_lookup:
                        performer["reference"] = self.pii_lookup[original_ref]
    
    def _anonymize_medication_statement(self, med_statement: Dict[str, Any]) -> None:
        """
        Anonymize a MedicationStatement resource in-place
        """
        # Anonymize ID
        if "id" in med_statement:
            med_statement["id"] = self._anonymize_identifier(med_statement["id"], "ID")
        
        # Update subject reference if it exists
        if "subject" in med_statement and "reference" in med_statement["subject"]:
            original_ref = med_statement["subject"]["reference"]
            if original_ref in self.pii_lookup:
                med_statement["subject"]["reference"] = self.pii_lookup[original_ref]
        
        # Update informationSource if it's a reference
        if "informationSource" in med_statement:
            info_source = med_statement["informationSource"]
            if "reference" in info_source:
                original_ref = info_source["reference"]
                if original_ref in self.pii_lookup:
                    info_source["reference"] = self.pii_lookup[original_ref]
            elif "display" in info_source:
                # If it's a display name (like a doctor name), anonymize it
                info_source["display"] = self._anonymize_identifier(info_source["display"], "NAME")
    
    def _anonymize_encounter(self, encounter: Dict[str, Any]) -> None:
        """
        Anonymize an Encounter resource in-place
        """
        # Anonymize ID
        if "id" in encounter:
            encounter["id"] = self._anonymize_identifier(encounter["id"], "ID")
        
        # Update subject reference if it exists
        if "subject" in encounter and "reference" in encounter["subject"]:
            original_ref = encounter["subject"]["reference"]
            if original_ref in self.pii_lookup:
                encounter["subject"]["reference"] = self.pii_lookup[original_ref]
        
        # Anonymize any participants (like practitioners)
        if "participant" in encounter:
            for participant in encounter["participant"]:
                if "individual" in participant and "reference" in participant["individual"]:
                    original_ref = participant["individual"]["reference"]
                    if original_ref in self.pii_lookup:
                        participant["individual"]["reference"] = self.pii_lookup[original_ref]
    
    def _anonymize_identifier(self, identifier: str, pii_type: str) -> str:
        """
        Anonymize an identifier based on its type
        
        Uses deterministic hashing to ensure the same identifier always maps
        to the same anonymized value, which is important for data linkage.
        
        Args:
            identifier: The original identifier to anonymize
            pii_type: The type of PII (NAME, ID, etc.)
            
        Returns:
            Anonymized identifier
        """
        # Check if we've already anonymized this value
        key = f"{pii_type}:{identifier}"
        if key in self.pii_lookup:
            return self.pii_lookup[key]
        
        # Generate a new anonymized value based on the PII type
        if pii_type == "NAME":
            # Create a hash of the original name
            hash_val = hashlib.md5(f"{self.salt}:{identifier}".encode()).hexdigest()
            # Use the hash to generate a synthetic name
            anonymized = f"Person-{hash_val[:8]}"
            
        elif pii_type == "ID":
            # Create a deterministic but anonymized ID
            hash_val = hashlib.md5(f"{self.salt}:{identifier}".encode()).hexdigest()
            anonymized = f"ID-{hash_val[:12]}"
            
        elif pii_type == "DOB":
            # Parse original date
            try:
                original_date = datetime.strptime(identifier, "%Y-%m-%d")
                # Add a small random offset but keep year the same to preserve age
                day_offset = random.randint(-30, 30)
                new_date = original_date + timedelta(days=day_offset)
                
                # Make sure we keep the original year
                if new_date.year != original_date.year:
                    new_date = new_date.replace(year=original_date.year)
                    
                anonymized = new_date.strftime("%Y-%m-%d")
            except:
                # If we can't parse the date, use a hash
                hash_val = hashlib.md5(f"{self.salt}:{identifier}".encode()).hexdigest()
                anonymized = f"Date-{hash_val[:8]}"
                
        elif pii_type == "ADDRESS":
            # Create a synthetic address
            hash_val = hashlib.md5(f"{self.salt}:{identifier}".encode()).hexdigest()
            anonymized = f"Address-{hash_val[:8]}"
            
        elif pii_type == "PHONE":
            # Create a synthetic phone number
            hash_val = hashlib.md5(f"{self.salt}:{identifier}".encode()).hexdigest()
            # Generate a random but valid-looking US phone number
            anonymized = f"555-{hash_val[:3]}-{hash_val[3:7]}"
            
        elif pii_type == "EMAIL":
            # Create a synthetic email
            hash_val = hashlib.md5(f"{self.salt}:{identifier}".encode()).hexdigest()
            anonymized = f"person.{hash_val[:8]}@example.com"
            
        elif pii_type == "SSN":
            # Create a synthetic SSN
            hash_val = hashlib.md5(f"{self.salt}:{identifier}".encode()).hexdigest()
            anonymized = f"XXX-XX-{hash_val[:4]}"
            
        else:
            # Default anonymization for other types
            hash_val = hashlib.md5(f"{self.salt}:{identifier}".encode()).hexdigest()
            anonymized = f"Anon-{hash_val[:8]}"
        
        # Store the mapping for future use
        self.pii_lookup[key] = anonymized
        return anonymized
