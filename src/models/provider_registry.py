"""
Provider Registry Models for HealthData Gateway

This module contains data models for managing healthcare provider registration and requests
in the HealthData Gateway platform.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl


class ProviderType(str, Enum):
    """Type of healthcare provider"""
    HOSPITAL = "hospital"
    PHARMACY = "pharmacy"
    WEARABLE = "wearable"
    LAB = "lab"
    CLINIC = "clinic"
    OTHER = "other"


class ProviderStatus(str, Enum):
    """Status of provider registration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    INACTIVE = "inactive"


class ContactInfo(BaseModel):
    """Contact information for a provider"""
    name: str = Field(..., description="Contact person's name")
    title: Optional[str] = Field(None, description="Contact person's title")
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")


class IntegrationInfo(BaseModel):
    """Technical integration information for a provider"""
    api_documentation: Optional[HttpUrl] = Field(None, description="Link to API documentation")
    requires_oauth: bool = Field(False, description="Whether the provider requires OAuth")
    supports_fhir: bool = Field(False, description="Whether the provider supports FHIR natively")
    api_specifications: Optional[dict] = Field(None, description="Additional API specifications")
    testing_credentials: Optional[dict] = Field(None, description="Testing credentials (not stored in plaintext)")


class ProviderBase(BaseModel):
    """Base class for provider information"""
    name: str = Field(..., description="Provider name")
    type: ProviderType = Field(..., description="Type of provider")
    description: Optional[str] = Field(None, description="Provider description")
    website: Optional[HttpUrl] = Field(None, description="Provider website")
    logo_url: Optional[HttpUrl] = Field(None, description="URL to provider logo")
    contact: ContactInfo = Field(..., description="Provider contact information")


class ProviderRegistrationRequest(ProviderBase):
    """Request from a provider to be added to the platform"""
    integration_info: Optional[IntegrationInfo] = Field(None, description="Technical integration information")
    submitted_by: str = Field(..., description="User ID or email of submitter")
    submitted_at: datetime = Field(default_factory=datetime.now, description="Request submission timestamp")
    status: ProviderStatus = Field(default=ProviderStatus.PENDING, description="Request status")
    notes: Optional[str] = Field(None, description="Additional notes or information")


class PatientProviderRequest(BaseModel):
    """Request from a patient to add a provider to the platform"""
    provider_name: str = Field(..., description="Name of the provider")
    provider_type: ProviderType = Field(..., description="Type of provider")
    provider_website: Optional[HttpUrl] = Field(None, description="Provider website if known")
    provider_location: Optional[str] = Field(None, description="Provider location/address")
    requested_by: str = Field(..., description="User ID or email of requesting patient")
    requested_at: datetime = Field(default_factory=datetime.now, description="Request submission timestamp")
    reason: Optional[str] = Field(None, description="Reason for requesting this provider")
    status: ProviderStatus = Field(default=ProviderStatus.PENDING, description="Request status")
    

class RegisteredProvider(ProviderBase):
    """A provider that has been registered and approved on the platform"""
    provider_id: str = Field(..., description="Unique provider identifier")
    integration_status: str = Field(default="pending", description="Integration status")
    integration_info: Optional[IntegrationInfo] = Field(None, description="Technical integration information")
    supported_data_types: List[str] = Field(default_factory=list, description="Supported data types")
    registered_at: datetime = Field(default_factory=datetime.now, description="Registration timestamp")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    status: ProviderStatus = Field(default=ProviderStatus.ACTIVE, description="Provider status")
    available_to_patients: bool = Field(default=True, description="Whether available to patients for selection")
