# HealthData Gateway - Provider API Documentation

## Overview

The HealthData Gateway Provider API enables secure integration between healthcare providers (hospitals, pharmacies, wearable manufacturers) and the HealthData Gateway platform. This documentation outlines all available endpoints, data models, and integration workflows to help providers successfully connect their systems.

## Contents

1. [Authentication](#authentication)
2. [Provider Registration](#provider-registration)
3. [Data Integration](#data-integration)
4. [Consent Management](#consent-management)
5. [FHIR Compliance](#fhir-compliance)
6. [Error Handling](#error-handling)
7. [Rate Limits](#rate-limits)
8. [Integration Checklist](#integration-checklist)

## Authentication

All API requests require OAuth2 authentication. 

### Obtaining Credentials

After your provider registration is approved, you will receive:
- Client ID
- Client Secret
- Access Token URL

### Authentication Flow

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Use this token in the Authorization header for all API requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5...
```

## Provider Registration

### Register Provider

```
POST /api/provider-registry/provider/register
```

Request Body:
```json
{
  "name": "Example Hospital System",
  "type": "hospital", 
  "description": "Leading healthcare provider in the Northeast",
  "website": "https://www.examplehospital.com",
  "logo_url": "https://www.examplehospital.com/logo.png",
  "contact": {
    "name": "Jane Smith",
    "title": "Integration Manager",
    "email": "jane.smith@examplehospital.com",
    "phone": "555-123-4567"
  },
  "integration_info": {
    "api_documentation": "https://developer.examplehospital.com/docs",
    "requires_oauth": true,
    "supports_fhir": true,
    "api_specifications": {
      "version": "2.1.0",
      "format": "JSON"
    }
  },
  "submitted_by": "jane.smith@examplehospital.com",
  "notes": "We support FHIR R4 and custom APIs"
}
```

Response:
```json
{
  "id": "f8c3de3d-1fea-4d7c-a8b0-29f63c4c3454",
  "name": "Example Hospital System",
  "type": "hospital",
  "submitted_at": "2025-03-16T05:15:30.123Z",
  "status": "pending"
}
```

## Data Integration

After your registration is approved, you'll need to implement the following data endpoints:

### Patient Data Endpoint (Hospitals)

Your system must expose a secure endpoint that the HealthData Gateway can access to retrieve patient data:

```
GET /api/v1/patients/{patient_id}
Authorization: Bearer {token}
```

Response should conform to FHIR Patient resource format:

```json
{
  "resourceType": "Patient",
  "id": "patient123",
  "name": [
    {
      "given": ["John"],
      "family": "Doe"
    }
  ],
  "gender": "male",
  "birthDate": "1970-01-01"
}
```

### Medication Data Endpoint (Pharmacies)

```
GET /api/v1/patients/{patient_id}/medications
Authorization: Bearer {token}
```

Response should conform to FHIR MedicationRequest or MedicationDispense resources.

### Health Metrics Endpoint (Wearables)

```
GET /api/v1/users/{user_id}/metrics
Authorization: Bearer {token}
```

Response should include health metrics in a structured format.

## Consent Management

HealthData Gateway manages patient consent through blockchain technology. When a patient grants consent to share their data:

1. HealthData Gateway system records consent on the blockchain
2. When requests are made to your provider API, the request will include a verified consent token
3. Your system should validate this token before returning patient data

### Consent Verification

Your API should accept and validate the consent token in the request headers:

```
X-Consent-Token: {blockchain_verified_token}
```

## FHIR Compliance

We strongly recommend implementing FHIR standards for all health data. The HealthData Gateway supports:

- FHIR R4 (preferred)
- FHIR STU3
- FHIR DSTU2 (legacy support only)

Resources that should conform to FHIR:
- Patient
- Observation
- MedicationRequest
- MedicationDispense
- AllergyIntolerance
- Condition
- Procedure
- DiagnosticReport

## Error Handling

Use standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden (e.g., no valid consent)
- 404: Resource Not Found
- 429: Too Many Requests
- 500: Server Error

Error responses should follow this format:

```json
{
  "error": "invalid_request",
  "error_description": "The patient_id parameter is required",
  "request_id": "7b411c12-44e5-4545-8bdb-a246bc35967a"
}
```

## Rate Limits

- Base rate: 100 requests per minute
- Burst allowance: 150 requests per minute for up to 2 minutes
- When rate limit is exceeded, the API will return a 429 response with a Retry-After header

## Integration Checklist

1. ✅ Register your organization through the Provider Registration API
2. ✅ Receive approval and integration credentials
3. ✅ Implement required data endpoints
4. ✅ Implement consent verification
5. ✅ Complete security assessment
6. ✅ Test with sandbox environment
7. ✅ Pass integration validation
8. ✅ Deploy to production
9. ✅ Monitor integration health

## Support

For technical assistance during integration:
- Email: integration@healthdatagateway.com
- Developer Support: +1 (555) 123-4567
- API Status Dashboard: https://status.healthdatagateway.com

---

© 2025 HealthData Gateway. All rights reserved.
