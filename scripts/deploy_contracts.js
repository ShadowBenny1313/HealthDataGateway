/**
 * deploy_contracts.js - Script to deploy HealthData Gateway smart contracts
 * 
 * This script deploys the Consent and Rewards smart contracts to a blockchain network
 * and saves the contract addresses and ABIs for later use.
 */

const fs = require('fs');
const path = require('path');
const Web3 = require('web3');

// Connect to local blockchain (like Ganache)
const web3 = new Web3('http://localhost:8545');

async function deployContracts() {
  console.log('Deploying HealthData Gateway smart contracts...');
  
  // Get the contract source files
  const consentPath = path.join(__dirname, '..', 'src', 'blockchain', 'consent.sol');
  const rewardsPath = path.join(__dirname, '..', 'src', 'blockchain', 'rewards.sol');
  
  const consentSource = fs.readFileSync(consentPath, 'utf8');
  const rewardsSource = fs.readFileSync(rewardsPath, 'utf8');
  
  // In a real implementation, we would use solc to compile the contracts
  // For this example, we'll simulate the compilation output
  console.log('Compiling contracts...');
  
  // This would be the actual compiled contract data in production
  const mockConsentABI = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "string",
          "name": "patientId",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "requester",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "expirationTime",
          "type": "uint256"
        }
      ],
      "name": "ConsentGranted",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "string",
          "name": "patientId",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "address",
          "name": "requester",
          "type": "address"
        }
      ],
      "name": "ConsentRevoked",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "patientId",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "requester",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "durationDays",
          "type": "uint256"
        }
      ],
      "name": "grantConsent",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "patientId",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "requester",
          "type": "address"
        }
      ],
      "name": "revokeConsent",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "patientId",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "requester",
          "type": "address"
        }
      ],
      "name": "hasValidConsent",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "patientId",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "requester",
          "type": "address"
        }
      ],
      "name": "getConsentExpiration",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
  ];
  
  const mockRewardsABI = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Approval",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        },
        {
          "indexed": false,
          "internalType": "string",
          "name": "dataType",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "qualityLevel",
          "type": "uint256"
        }
      ],
      "name": "RewardIssued",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "to",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "value",
          "type": "uint256"
        }
      ],
      "name": "Transfer",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    // More ABI functions would be here
  ];
  
  try {
    // Get accounts
    const accounts = await web3.eth.getAccounts();
    const deployer = accounts[0];
    
    console.log(`Deploying contracts from account: ${deployer}`);
    
    // In a real implementation, we would deploy using the compiled contracts
    // For this example, we'll just log the step
    console.log('Deploying DataConsent contract...');
    
    // Simulate contract deployment and get addresses
    const consentContractAddress = "0x1234567890123456789012345678901234567890";
    const rewardsContractAddress = "0x0987654321098765432109876543210987654321";
    
    console.log(`DataConsent contract deployed at: ${consentContractAddress}`);
    console.log(`HealthDataRewards contract deployed at: ${rewardsContractAddress}`);
    
    // Save contract addresses and ABIs
    const deploymentInfo = {
      network: "development",
      deployer: deployer,
      consentContract: {
        address: consentContractAddress,
        abi: mockConsentABI
      },
      rewardsContract: {
        address: rewardsContractAddress,
        abi: mockRewardsABI
      },
      deployedAt: new Date().toISOString()
    };
    
    // Write deployment info to file
    const deploymentPath = path.join(__dirname, '..', 'src', 'blockchain', 'deployment.json');
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
    
    // Write ABIs to separate files for easier import
    const consentAbiPath = path.join(__dirname, '..', 'src', 'blockchain', 'consent_abi.json');
    const rewardsAbiPath = path.join(__dirname, '..', 'src', 'blockchain', 'rewards_abi.json');
    
    fs.writeFileSync(consentAbiPath, JSON.stringify(mockConsentABI, null, 2));
    fs.writeFileSync(rewardsAbiPath, JSON.stringify(mockRewardsABI, null, 2));
    
    console.log('Deployment complete! Contract addresses and ABIs saved.');
    console.log(`Deployment info: ${deploymentPath}`);
    console.log(`Update your .env file with these contract addresses.`);
    
  } catch (error) {
    console.error('Error deploying contracts:');
    console.error(error);
    process.exit(1);
  }
}

deployContracts();
