# HealthData Gateway - Integration Guide

This guide outlines the steps required to integrate the HealthData Gateway service with the HealthData Rewards platform, following the microservices architecture approach.

## Integration Overview

HealthData Gateway is designed as a standalone service that can be integrated with HealthData Rewards through a well-defined API. This approach ensures:

- **Modularity**: Each service has a clear, distinct responsibility
- **Scalability**: Services can be scaled independently based on demand
- **Maintainability**: Changes to one service don't require changes to the other
- **Testability**: Each service can be tested independently

## Integration Architecture

```
┌───────────────────┐      ┌───────────────────┐
│                   │      │                   │
│  HealthData       │      │  HealthData       │
│  Rewards          │◄─────►  Gateway          │
│                   │      │                   │
└───────────────────┘      └───────────────────┘
        │                          │
        │                          │
        ▼                          ▼
┌───────────────────┐      ┌───────────────────┐
│                   │      │  External Data    │
│  Rewards          │      │  Sources          │
│  Blockchain       │      │  (Hospitals,      │
│                   │      │   Pharmacies,     │
└───────────────────┘      │   Wearables)      │
                           └───────────────────┘
```

## Prerequisites

Before integration, ensure:

1. HealthData Gateway is deployed and accessible
2. HealthData Rewards is ready for integration
3. Authentication mechanisms are aligned
4. Network connectivity between services is established

## Integration Steps

### 1. Configure HealthData Rewards to Use the Gateway

Add the following configuration to HealthData Rewards:

```python
# In HealthData Rewards configuration
HEALTHDATA_GATEWAY_URL = "http://gateway-service:8000"  # Or the appropriate URL
HEALTHDATA_GATEWAY_USERNAME = "rewards_service"
HEALTHDATA_GATEWAY_PASSWORD = "your_secure_password"
```

### 2. Import the Client Library

The easiest way to integrate is to use the provided client library:

1. Copy the `src/integration/client.py` file to the HealthData Rewards project
2. Import and use the client in your code:

```python
from integration.client import HealthDataGatewayClient

# Initialize the client
gateway_client = HealthDataGatewayClient()

# Authenticate
gateway_client.authenticate()

# Retrieve data
hospital_data = gateway_client.get_hospital_patient_data("hospital_id", "patient_id")
```

### 3. Set Up Shared Authentication

For production, implement a more secure authentication mechanism:

1. Create service accounts in both systems
2. Use JWT tokens with appropriate scopes
3. Consider implementing OAuth2 for service-to-service communication

Example JWT implementation:

```python
# In HealthData Rewards
import jwt
import time

def get_gateway_token():
    payload = {
        "iss": "health_rewards",
        "sub": "service_account",
        "aud": "health_gateway",
        "exp": int(time.time()) + 3600,  # 1 hour expiration
        "scopes": ["read:hospital", "read:pharmacy", "read:wearable"]
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
```

### 4. Implement Data Synchronization

Determine the data flow between services:

1. **Event-Based**: Use a message queue (RabbitMQ, Kafka) for async communication
2. **API-Based**: Direct API calls for immediate data needs
3. **Hybrid**: Combine both approaches based on use cases

Example event-based integration:

```python
# In HealthData Rewards
import pika
import json

def publish_data_request(patient_id, data_type):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    channel.exchange_declare(exchange='healthdata', exchange_type='topic')
    
    message = {
        "patient_id": patient_id,
        "data_type": data_type,
        "requested_by": "rewards_service",
        "timestamp": time.time()
    }
    
    channel.basic_publish(
        exchange='healthdata',
        routing_key=f'data.request.{data_type}',
        body=json.dumps(message)
    )
    
    connection.close()
```

### 5. Link Blockchain Consent & Rewards

Ensure that the consent management in HealthData Gateway aligns with the rewards system:

1. Verify that user consent exists before processing rewards
2. Ensure consent is properly recorded on the blockchain
3. Link user identities across both systems

```python
# In HealthData Rewards
def process_reward(user_id, data_contribution):
    # First check if user has valid consent
    has_consent = gateway_client.verify_consent(user_id, "rewards_service")
    
    if not has_consent:
        logger.warning(f"Cannot process reward for {user_id}: No valid consent")
        return False
    
    # Process the reward if consent is valid
    reward_amount = calculate_reward(data_contribution)
    issue_tokens(user_id, reward_amount)
    
    return True
```

### 6. Handle Error Cases

Implement proper error handling for integration points:

- Service unavailability
- Authentication failures
- Consent verification failures
- Data format inconsistencies

Example error handling:

```python
try:
    data = gateway_client.get_hospital_patient_data(hospital_id, patient_id)
    if "error" in data:
        logger.error(f"Error from Gateway: {data['error']}")
        # Implement fallback or retry logic
    else:
        process_data(data)
except Exception as e:
    logger.error(f"Failed to communicate with Gateway: {str(e)}")
    # Implement circuit breaker pattern or other resilience mechanisms
```

### 7. Monitoring and Logging

Implement cross-service monitoring:

1. Use distributed tracing (e.g., OpenTelemetry)
2. Set up centralized logging
3. Create dashboards to monitor integration points

### 8. Testing the Integration

1. Create integration tests that verify the end-to-end functionality
2. Set up a staging environment where both services can be tested together
3. Test failure scenarios and recovery mechanisms

## Deployment Considerations

### Kubernetes Deployment

For containerized deployments, consider using Kubernetes:

```yaml
# Example Kubernetes service for Gateway
apiVersion: v1
kind: Service
metadata:
  name: healthdata-gateway
spec:
  selector:
    app: healthdata-gateway
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### API Gateway Pattern

Consider using an API Gateway to manage communication:

1. Route requests to appropriate services
2. Handle authentication and rate limiting
3. Provide a unified entry point for clients

## Security Considerations

1. Use HTTPS for all communication between services
2. Implement proper authentication and authorization
3. Encrypt sensitive data in transit and at rest
4. Regularly audit access patterns

## Support and Troubleshooting

If you encounter issues during integration:

1. Check logs in both services for errors
2. Verify network connectivity between services
3. Ensure authentication credentials are correct
4. Test the APIs directly using tools like Postman or cURL

For additional support, contact the HealthData team at support@healthdata.example.com.
