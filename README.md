# HealthData Gateway

HealthData Gateway is a standalone service that provides secure, standardized access to health data from multiple sources including hospitals, pharmacies, and wearable devices.

## Features

- **Data Standardization**: Converts various health data formats into FHIR standard
- **Blockchain-based Consent**: Secure, transparent patient consent management
- **Multi-source Integration**: Connect to hospitals, pharmacies, and wearable devices
- **AI-powered Anonymization**: Preserve privacy while maintaining data utility
- **Reward System**: Tokenized incentives for data sharing

## Project Structure

```
HealthDataGateway/
│── src/
│   ├── api/               # API endpoints for different data sources
│   │   ├── hospitals.py   # Hospital system integrations
│   │   ├── pharmacies.py  # Pharmacy system integrations
│   │   ├── wearables.py   # Wearable device integrations
│   ├── blockchain/        # Blockchain components
│   │   ├── consent.sol    # Smart contract for consent management
│   │   ├── rewards.sol    # Smart contract for reward tokens
│   │   ├── consent.py     # Python interface to consent contract
│   ├── ai/                # AI components
│   │   ├── standardizer.py # FHIR data standardization
│   │   ├── anonymizer.py   # Data anonymization
│   ├── main.py            # Main FastAPI application
│── tests/                 # Test directory
│── .env                   # Environment configuration
│── requirements.txt       # Python dependencies
│── README.md              # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+ (for blockchain development)
- Ethereum development environment (for blockchain features)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd HealthDataGateway
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Application

Start the API server:

```
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Hospital Data
- `GET /api/hospitals/` - List supported hospital systems
- `GET /api/hospitals/{hospital_id}/patient/{patient_id}` - Get patient data from hospital

### Pharmacy Data
- `GET /api/pharmacies/` - List supported pharmacy systems
- `GET /api/pharmacies/{pharmacy_id}/patient/{patient_id}` - Get patient medication data

### Wearable Data
- `GET /api/wearables/` - List supported wearable systems
- `GET /api/wearables/{wearable_id}/user/{user_id}` - Get user health data from wearable
- `GET /api/wearables/{wearable_id}/user/{user_id}/metrics/{metric_type}` - Get specific health metric

### Consent Management
- `POST /consent/{patient_id}/grant` - Grant consent for data access
- `POST /consent/{patient_id}/revoke` - Revoke previously granted consent

### Data Processing
- `POST /anonymize` - Anonymize FHIR data

## Integration with HealthData Rewards

This project is designed to be integrated with HealthData Rewards as a microservice. After development and testing, the following integration steps will be required:

1. Deploy HealthData Gateway as a standalone service
2. Set up API Gateway for HealthData Rewards to communicate with HealthData Gateway
3. Configure shared authentication between services
4. Link the blockchain-based rewards and consent systems

## Development

### Testing

Run tests:

```
pytest
```

### Deploying

For production deployment, consider using:
- Docker containers
- AWS Lambda + API Gateway
- Kubernetes

## License

[Specify license here]

## Contact

[Your contact information]
