"""
HealthData Gateway - Main Application

This is the main entry point for the HealthData Gateway service, which provides:
- AI-powered data standardization into FHIR format
- Secure blockchain-based consent management
- Integration with hospitals, pharmacies, and wearables
- Data anonymization capabilities
"""

import os
import json
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Import API routers
from src.api.hospitals import router as hospitals_router
from src.api.pharmacies import router as pharmacies_router
from src.api.wearables import router as wearables_router
from src.api.provider_registry import router as provider_registry_router
from src.api.dashboard import router as dashboard_router

# Import integrations
from src.integrations.healthdata_rewards import rewards_client

# Import AI components
from src.ai.standardizer import standardize_to_fhir
from src.ai.anonymizer import Anonymizer

# Import blockchain components
from src.blockchain.consent import verify_consent, grant_consent, revoke_consent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("healthdata_gateway")

# Initialize FastAPI app
app = FastAPI(
    title="HealthData Gateway",
    description="API for standardizing and securing health data from multiple sources",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Add routers
app.include_router(hospitals_router)
app.include_router(pharmacies_router)
app.include_router(wearables_router)
app.include_router(provider_registry_router)
app.include_router(dashboard_router)

@app.get("/")
async def root():
    """
    Root endpoint with basic service information
    """
    return {
        "service": "HealthData Gateway",
        "version": "0.2.0",
        "status": "operational",
        "features": [
            "FHIR Standardization",
            "Blockchain Consent Management",
            "Provider Registry",
            "Data Anonymization",
            "HealthData Rewards Integration"
        ],
        "docs_url": "/docs",
    }

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate and generate access token
    
    This is a simplified mock implementation. In production, this would:
    1. Validate credentials against a user database
    2. Generate proper JWT tokens with appropriate scopes
    """
    # Mock user authentication - in production, check against real database
    if form_data.username == "demo" and form_data.password == "password":
        # Return a mock token - in production, use proper JWT
        return {
            "access_token": "demo_token_with_full_access",
            "token_type": "bearer",
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    Get information about the currently authenticated user
    """
    # In production, validate and decode the JWT token
    # For now, return mock user data
    return {
        "user_id": "demo_user",
        "permissions": ["read:hospital", "read:pharmacy", "read:wearable"],
    }

@app.post("/consent/{patient_id}/grant")
async def grant_patient_consent(
    patient_id: str, 
    requester: str,
    duration_days: int = 30,
    token: str = Depends(oauth2_scheme)
):
    """
    Grant consent for a requester to access patient data
    """
    try:
        success = grant_consent(patient_id, requester, duration_days)
        if success:
            return {"status": "success", "message": "Consent granted successfully"}
        return {"status": "error", "message": "Failed to grant consent"}
    except Exception as e:
        logger.error(f"Error granting consent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error granting consent: {str(e)}")

@app.post("/consent/{patient_id}/revoke")
async def revoke_patient_consent(
    patient_id: str, 
    requester: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Revoke previously granted consent
    """
    try:
        success = revoke_consent(patient_id, requester)
        if success:
            return {"status": "success", "message": "Consent revoked successfully"}
        return {"status": "error", "message": "Failed to revoke consent"}
    except Exception as e:
        logger.error(f"Error revoking consent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error revoking consent: {str(e)}")

@app.post("/anonymize")
async def anonymize_data(
    data: Dict[str, Any],
    preserve_age: bool = True,
    preserve_gender: bool = True,
    token: str = Depends(oauth2_scheme)
):
    """
    Anonymize FHIR data
    
    The data should be a FHIR bundle that has already been standardized.
    """
    try:
        # Create anonymizer with specified preservation settings
        anonymizer = Anonymizer(
            preserve_age=preserve_age,
            preserve_gender=preserve_gender
        )
        
        # Process the data
        anonymized_data = anonymizer.anonymize_fhir(data)
        
        return anonymized_data
    except Exception as e:
        logger.error(f"Error anonymizing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error anonymizing data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
