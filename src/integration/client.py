"""
client.py - Integration client for HealthData Gateway

This module provides a client library that can be used by other services (like HealthData Rewards)
to interact with HealthData Gateway's APIs in a clean and abstracted way.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger("healthdata_client")

class HealthDataGatewayClient:
    """
    Client for interacting with the HealthData Gateway API.
    
    This client abstracts the HTTP requests and authentication flow,
    providing a simple interface for other services to use.
    """
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize the client with connection details
        
        Args:
            base_url: The base URL of the HealthData Gateway API
            api_key: API key for authentication (if using key-based auth)
        """
        self.base_url = base_url or os.environ.get('HEALTHDATA_GATEWAY_URL', 'http://localhost:8000')
        self.api_key = api_key or os.environ.get('HEALTHDATA_GATEWAY_API_KEY')
        self.token = None
        
    def authenticate(self, username: str = None, password: str = None) -> bool:
        """
        Authenticate with the API using OAuth2 password flow
        
        Args:
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            bool: True if authentication was successful
        """
        # Use environment variables if not provided
        username = username or os.environ.get('HEALTHDATA_GATEWAY_USERNAME', 'demo')
        password = password or os.environ.get('HEALTHDATA_GATEWAY_PASSWORD', 'password')
        
        try:
            response = requests.post(
                f"{self.base_url}/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests, including authentication"""
        headers = {"Content-Type": "application/json"}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
            
        return headers
    
    # Hospital data methods
    def list_hospitals(self) -> Dict[str, Any]:
        """List all supported hospital systems"""
        try:
            response = requests.get(
                f"{self.base_url}/api/hospitals/",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error listing hospitals: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error listing hospitals: {str(e)}")
            return {"error": str(e)}
    
    def get_hospital_patient_data(self, hospital_id: str, patient_id: str) -> Dict[str, Any]:
        """
        Get patient data from a specific hospital
        
        Args:
            hospital_id: The hospital system identifier
            patient_id: The patient's ID in that hospital system
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/hospitals/{hospital_id}/patient/{patient_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting hospital patient data: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error getting hospital patient data: {str(e)}")
            return {"error": str(e)}
    
    # Pharmacy data methods
    def list_pharmacies(self) -> Dict[str, Any]:
        """List all supported pharmacy systems"""
        try:
            response = requests.get(
                f"{self.base_url}/api/pharmacies/",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error listing pharmacies: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error listing pharmacies: {str(e)}")
            return {"error": str(e)}
    
    def get_pharmacy_patient_data(self, pharmacy_id: str, patient_id: str) -> Dict[str, Any]:
        """
        Get patient medication data from a specific pharmacy
        
        Args:
            pharmacy_id: The pharmacy system identifier
            patient_id: The patient's ID in that pharmacy system
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/pharmacies/{pharmacy_id}/patient/{patient_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting pharmacy patient data: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error getting pharmacy patient data: {str(e)}")
            return {"error": str(e)}
    
    # Wearable data methods
    def list_wearables(self) -> Dict[str, Any]:
        """List all supported wearable systems"""
        try:
            response = requests.get(
                f"{self.base_url}/api/wearables/",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error listing wearables: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error listing wearables: {str(e)}")
            return {"error": str(e)}
    
    def get_wearable_user_data(self, wearable_id: str, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get user health data from a specific wearable device
        
        Args:
            wearable_id: The wearable platform identifier
            user_id: The user's ID in the wearable platform
            days: Number of days of historical data to retrieve
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/wearables/{wearable_id}/user/{user_id}",
                params={"days": days},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting wearable user data: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error getting wearable user data: {str(e)}")
            return {"error": str(e)}
    
    def get_wearable_metric(self, wearable_id: str, user_id: str, metric_type: str, days: int = 30) -> Dict[str, Any]:
        """
        Get specific health metric data from wearable device
        
        Args:
            wearable_id: The wearable platform identifier
            user_id: The user's ID in the wearable platform
            metric_type: The specific metric to retrieve (heart_rate, steps, etc.)
            days: Number of days of historical data to retrieve
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/wearables/{wearable_id}/user/{user_id}/metrics/{metric_type}",
                params={"days": days},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting wearable metric: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error getting wearable metric: {str(e)}")
            return {"error": str(e)}
    
    # Consent management methods
    def grant_consent(self, patient_id: str, requester: str, duration_days: int = 30) -> Dict[str, Any]:
        """
        Grant consent for a requester to access patient data
        
        Args:
            patient_id: The patient's unique identifier
            requester: The requester's address/identifier
            duration_days: Number of days the consent remains valid
        """
        try:
            response = requests.post(
                f"{self.base_url}/consent/{patient_id}/grant",
                json={"requester": requester, "duration_days": duration_days},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error granting consent: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error granting consent: {str(e)}")
            return {"error": str(e)}
    
    def revoke_consent(self, patient_id: str, requester: str) -> Dict[str, Any]:
        """
        Revoke previously granted consent
        
        Args:
            patient_id: The patient's unique identifier
            requester: The requester's address/identifier
        """
        try:
            response = requests.post(
                f"{self.base_url}/consent/{patient_id}/revoke",
                json={"requester": requester},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error revoking consent: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error revoking consent: {str(e)}")
            return {"error": str(e)}
    
    # Data processing methods
    def anonymize_data(self, data: Dict[str, Any], preserve_age: bool = True, preserve_gender: bool = True) -> Dict[str, Any]:
        """
        Anonymize FHIR data
        
        Args:
            data: FHIR bundle to anonymize
            preserve_age: Whether to preserve patient age (range) in anonymized data
            preserve_gender: Whether to preserve patient gender in anonymized data
        """
        try:
            response = requests.post(
                f"{self.base_url}/anonymize",
                json={
                    "data": data,
                    "preserve_age": preserve_age,
                    "preserve_gender": preserve_gender
                },
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error anonymizing data: {response.status_code} - {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            logger.error(f"Error anonymizing data: {str(e)}")
            return {"error": str(e)}
