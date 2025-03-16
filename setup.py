from setuptools import setup, find_packages

setup(
    name="healthdata-gateway",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "pydantic>=1.10.7",
        "python-dotenv>=1.0.0",
        "web3>=6.0.0",
        "requests>=2.28.2",
        "python-multipart>=0.0.6",
        "PyJWT>=2.6.0",
    ],
    author="HealthData Team",
    author_email="info@healthdata.example.com",
    description="Gateway service for standardizing health data from multiple sources",
    keywords="healthcare, FHIR, blockchain, data standardization",
    python_requires=">=3.8",
)
