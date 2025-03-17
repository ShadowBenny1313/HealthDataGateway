"""
dashboard.py - User Dashboard API for HealthData Gateway

This module provides comprehensive API endpoints for users to view their:
- Connected data providers
- Health data summaries
- Consent records
- Reward balances
- Provider registration status
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ..blockchain.consent import verify_consent, get_user_consents
from ..api.hospitals import retrieve_from_hospital_system
from ..api.wearables import retrieve_from_wearable_system
from ..api.pharmacies import retrieve_from_pharmacy_system
from ..ai.standardizer import standardize_to_fhir
from ..integrations.healthdata_rewards import get_user_reward_balance
from ..models.provider_registry import ProviderType
from ..api.provider_registry import get_approved_providers, get_provider_by_id

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard_api")

# Create router for dashboard endpoints
router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/user/{user_id}")
async def get_user_dashboard(
    user_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Get comprehensive user dashboard including:
    - Connected providers
    - Consent status
    - Reward balance
    - Recent health data summaries
    
    This endpoint verifies the user has consent to access the requested data.
    """
    # Verify access permissions (user can only access their own data)
    # In a real implementation, this would decode the JWT token and verify user_id matches
    # For simplicity, we're assuming token auth is valid
    
    try:
        # Get user's active consents
        user_consents = get_user_consents(user_id)
        
        # Get user's reward balance
        rewards = get_user_reward_balance(user_id)
        
        # Get list of approved providers
        approved_providers = get_approved_providers()
        
        # Get user's data summaries for each provider where consent exists
        data_summaries = []
        
        # Check which hospital providers the user has consented to
        for provider in approved_providers:
            if provider["provider_type"] == ProviderType.HOSPITAL.value:
                # Check if user has consented to this provider
                if any(c["provider_id"] == provider["id"] for c in user_consents):
                    try:
                        # Get summary of hospital data
                        hospital_data = retrieve_from_hospital_system(
                            provider["id"], 
                            user_id
                        )
                        
                        # Add to summaries
                        data_summaries.append({
                            "provider_name": provider["provider_name"],
                            "provider_type": "hospital",
                            "last_updated": datetime.now().isoformat(),
                            "data_types": ["conditions", "procedures", "medications"],
                            "summary": {
                                "record_count": len(hospital_data),
                                "oldest_record": "2023-01-01T00:00:00Z",  # Example
                                "newest_record": datetime.now().isoformat()
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error retrieving hospital data: {str(e)}")
            
            elif provider["provider_type"] == ProviderType.WEARABLE.value:
                # Check if user has consented to this provider
                if any(c["provider_id"] == provider["id"] for c in user_consents):
                    try:
                        # Get summary of wearable data
                        wearable_data = retrieve_from_wearable_system(
                            provider["id"],
                            user_id,
                            7  # Last 7 days of data
                        )
                        
                        # Add to summaries
                        data_summaries.append({
                            "provider_name": provider["provider_name"],
                            "provider_type": "wearable",
                            "last_updated": datetime.now().isoformat(),
                            "data_types": ["heart_rate", "steps", "sleep"],
                            "summary": {
                                "record_count": len(wearable_data),
                                "oldest_record": (datetime.now() - timedelta(days=7)).isoformat(),
                                "newest_record": datetime.now().isoformat()
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error retrieving wearable data: {str(e)}")
        
        # Compose complete dashboard response
        dashboard = {
            "user_id": user_id,
            "rewards": {
                "total_balance": rewards.get("tokens", 0),
                "data_contributions": rewards.get("data_contributions", 0),
                "last_updated": rewards.get("last_updated")
            },
            "consents": {
                "active_count": len(user_consents),
                "consents": user_consents
            },
            "providers": {
                "connected_count": len(data_summaries),
                "available_count": len(approved_providers),
                "data_summaries": data_summaries
            }
        }
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating dashboard: {str(e)}"
        )

@router.get("/providers")
async def get_available_providers(
    token: str = Depends(oauth2_scheme),
    provider_type: Optional[str] = Query(None, description="Filter by provider type (hospital, pharmacy, wearable)")
):
    """
    Get list of all approved providers available on the platform.
    Optionally filter by provider type.
    """
    try:
        providers = get_approved_providers()
        
        # Filter by provider type if specified
        if provider_type:
            providers = [p for p in providers if p["provider_type"] == provider_type]
            
        return {
            "count": len(providers),
            "providers": providers
        }
        
    except Exception as e:
        logger.error(f"Error retrieving providers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving providers: {str(e)}"
        )

@router.get("/consents/{user_id}")
async def get_user_consent_status(
    user_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Get all active consents for a specific user
    """
    # Verify access permissions (user can only access their own data)
    # In a real implementation, this would decode the JWT token and verify user_id matches
    
    try:
        consents = get_user_consents(user_id)
        
        # Enrich consent data with provider information
        enriched_consents = []
        for consent in consents:
            try:
                provider = get_provider_by_id(consent["provider_id"])
                consent["provider_name"] = provider.get("provider_name", "Unknown Provider")
                consent["provider_type"] = provider.get("provider_type", "unknown")
                enriched_consents.append(consent)
            except Exception:
                # If provider not found, still include basic consent info
                consent["provider_name"] = "Unknown Provider"
                consent["provider_type"] = "unknown"
                enriched_consents.append(consent)
                
        return {
            "user_id": user_id,
            "consent_count": len(enriched_consents),
            "consents": enriched_consents
        }
        
    except Exception as e:
        logger.error(f"Error retrieving consent status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving consent status: {str(e)}"
        )
