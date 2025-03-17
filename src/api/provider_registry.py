"""
Provider Registry API for HealthData Gateway

This module provides endpoints for:
1. Providers to register themselves on the platform
2. Patients to request new providers be added
3. Admin management of provider registrations
"""

from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from fastapi.security import OAuth2PasswordBearer

from src.blockchain.consent import verify_admin_role
from src.models.provider_registry import (
    ProviderRegistrationRequest,
    PatientProviderRequest,
    RegisteredProvider,
    ProviderStatus,
    ProviderType
)

# Initialize router
router = APIRouter(
    prefix="/api/provider-registry",
    tags=["provider-registry"],
    responses={404: {"description": "Not found"}},
)

# Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage for demo purposes
# In production, these would be stored in a database
provider_registration_requests = {}
patient_provider_requests = {}
registered_providers = {}


@router.post("/provider/register", response_model=Dict[str, Any])
async def register_provider(
    request: ProviderRegistrationRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Endpoint for healthcare providers to register themselves on the platform.
    
    This allows hospitals, pharmacies, wearable companies, and other healthcare
    providers to initiate the process of integrating with HealthData Gateway.
    """
    request_id = str(uuid.uuid4())
    request.submitted_at = datetime.now()
    provider_registration_requests[request_id] = request.dict()
    
    # In a real implementation, this would:
    # 1. Store the request in a database
    # 2. Trigger notifications to admins
    # 3. Start an automated verification process
    
    # Return request data with ID
    response = request.dict()
    response["id"] = request_id
    return response


@router.post("/patient/request-provider", response_model=PatientProviderRequest)
async def request_provider(
    request: PatientProviderRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Endpoint for patients to request a new healthcare provider be added to the platform.
    
    This allows patients to request their hospital, pharmacy, or wearable device
    be supported by HealthData Gateway if it's not already available.
    """
    request_id = str(uuid.uuid4())
    request.requested_at = datetime.now()
    patient_provider_requests[request_id] = request.dict()
    
    # In a real implementation, this would:
    # 1. Store the request in a database
    # 2. Check if similar requests already exist
    # 3. Notify admins and potentially the provider
    
    return {**request.dict(), "id": request_id}


@router.get("/providers", response_model=List[RegisteredProvider])
async def get_providers(
    provider_type: Optional[ProviderType] = Query(None, description="Filter by provider type"),
    token: str = Depends(oauth2_scheme)
):
    """
    Get a list of registered providers, optionally filtered by type.
    
    This endpoint is used by patient applications to display available
    provider options for connecting their health data.
    """
    providers = list(registered_providers.values())
    
    # Filter by type if specified
    if provider_type:
        providers = [p for p in providers if p["type"] == provider_type]
    
    # Only return providers that are available to patients
    providers = [p for p in providers if p["available_to_patients"]]
    
    return providers


@router.get("/provider/{provider_id}", response_model=RegisteredProvider)
async def get_provider(
    provider_id: str = Path(..., description="Provider ID"),
    token: str = Depends(oauth2_scheme)
):
    """
    Get details for a specific registered provider.
    """
    if provider_id not in registered_providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return registered_providers[provider_id]


# Admin endpoints - these would typically require additional authorization

# The approve_provider alias will be defined after the approve_provider_request function

@router.get("/admin/pending-requests", response_model=dict)
async def get_pending_requests(token: str = Depends(oauth2_scheme)):
    """
    Admin endpoint to get all pending requests (both provider and patient).
    
    This consolidated view helps administrators manage both provider-initiated
    and patient-initiated requests in one place.
    """
    # Verify admin role using blockchain
    if not verify_admin_role(token):
        raise HTTPException(
            status_code=403,
            detail="Admin role required for this operation"
        )
    
    # Filter provider requests that are pending
    pending_provider_requests = []
    for request_id, request in provider_registration_requests.items():
        # Handle both Pydantic models and dictionaries
        if isinstance(request, dict) and request.get("status") == ProviderStatus.PENDING:
            pending_provider_requests.append(request)
        elif hasattr(request, "status") and request.status == ProviderStatus.PENDING:
            pending_provider_requests.append(request)
    
    # Filter patient requests that are pending
    pending_patient_requests = []
    for request_id, request in patient_provider_requests.items():
        # Handle both Pydantic models and dictionaries
        if isinstance(request, dict) and request.get("status") == ProviderStatus.PENDING:
            pending_patient_requests.append(request)
        elif hasattr(request, "status") and request.status == ProviderStatus.PENDING:
            pending_patient_requests.append(request)
    
    return {
        "provider_requests": pending_provider_requests,
        "patient_requests": pending_patient_requests,
        "total_pending": len(pending_provider_requests) + len(pending_patient_requests)
    }

@router.get("/admin/provider-requests", response_model=List[ProviderRegistrationRequest])
async def get_provider_requests(
    status: Optional[ProviderStatus] = Query(None, description="Filter by status"),
    token: str = Depends(oauth2_scheme)
):
    """
    Admin endpoint to get provider registration requests.
    """
    # Verify admin role
    if not verify_admin_role(token):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for this operation"
        )
    
    requests = list(provider_registration_requests.values())
    
    # Filter by status if specified
    if status:
        filtered_requests = []
        for r in requests:
            # Handle both Pydantic models and dictionaries
            if isinstance(r, dict) and r.get("status") == status:
                filtered_requests.append(r)
            elif hasattr(r, "status") and r.status == status:
                filtered_requests.append(r)
        requests = filtered_requests
    
    return requests


@router.get("/admin/patient-requests", response_model=List[PatientProviderRequest])
async def get_patient_requests(
    status: Optional[ProviderStatus] = Query(None, description="Filter by status"),
    token: str = Depends(oauth2_scheme)
):
    """
    Admin endpoint to get patient provider requests.
    """
    # Verify admin role
    if not verify_admin_role(token):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for this operation"
        )
    
    requests = list(patient_provider_requests.values())
    
    # Filter by status if specified
    if status:
        requests = [r for r in requests if r["status"] == status]
    
    return requests


@router.put("/admin/provider-request/{request_id}/approve")
async def approve_provider_request(
    request_id: str = Path(..., description="Request ID"),
    token: str = Depends(oauth2_scheme)
):
    """
    Admin endpoint to approve a provider registration request.
    """
    # Verify admin role
    if not verify_admin_role(token):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for this operation"
        )
    
    if request_id not in provider_registration_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Update request status
    provider_registration_requests[request_id]["status"] = ProviderStatus.APPROVED
    
    # Create a new registered provider
    request_data = provider_registration_requests[request_id]
    provider_id = str(uuid.uuid4())
    
    # Create registered provider from request data
    provider = {
        **request_data,
        "provider_id": provider_id,
        "registered_at": datetime.now(),
        "last_updated": datetime.now(),
        "status": ProviderStatus.ACTIVE,
        "integration_status": "pending",
        "available_to_patients": False,  # Initially false until integration is complete
        "supported_data_types": []
    }
    
    registered_providers[provider_id] = provider
    
    return {"message": "Provider request approved", "provider_id": provider_id}


# Simple alias for approve_provider_request to fix the import in test_core_functions.py
approve_provider = approve_provider_request


@router.get("/admin/approved-providers", response_model=List[Dict[str, Any]])
async def get_approved_providers(token: str = Depends(oauth2_scheme)):
    """
    Admin endpoint to get all approved providers.
    
    This returns a list of all registered and approved healthcare providers.
    """
    # Verify admin role
    if not verify_admin_role(token):
        raise HTTPException(
            status_code=403,
            detail="Admin role required for this operation"
        )
    
    # Filter providers with status APPROVED
    approved_providers = []
    for provider_id, provider in registered_providers.items():
        # Handle both Pydantic models and dictionaries
        if isinstance(provider, dict) and provider.get("status") == ProviderStatus.APPROVED:
            approved_providers.append(provider)
        elif hasattr(provider, "status") and provider.status == ProviderStatus.APPROVED:
            approved_providers.append(provider)
    
    return approved_providers


@router.get("/providers/{provider_id}", response_model=Dict[str, Any])
async def get_provider_by_id(
    provider_id: str = Path(..., description="Provider ID"),
    token: str = Depends(oauth2_scheme)
):
    """
    Get details for a specific provider by ID.
    
    This endpoint retrieves all details for a specific healthcare provider.
    """
    if provider_id not in registered_providers:
        raise HTTPException(
            status_code=404,
            detail=f"Provider with ID {provider_id} not found"
        )
    
    return registered_providers[provider_id]


@router.put("/admin/provider/{provider_id}/update-status")
async def update_provider_status(
    provider_id: str = Path(..., description="Provider ID"),
    status: ProviderStatus = Body(..., embed=True),
    token: str = Depends(oauth2_scheme)
):
    """
    Admin endpoint to update a provider's status.
    """
    # Verify admin role
    if not verify_admin_role(token):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions for this operation"
        )
    
    if provider_id not in registered_providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    registered_providers[provider_id]["status"] = status
    registered_providers[provider_id]["last_updated"] = datetime.now()
    
    return {"message": f"Provider status updated to {status}"}
