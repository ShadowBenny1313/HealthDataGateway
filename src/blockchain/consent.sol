// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
 * @title DataConsent
 * @dev Smart contract for managing patient consent for data access
 */
contract DataConsent {
    address public owner;
    
    // Mapping from patient ID to array of authorized data requesters
    mapping(string => mapping(address => bool)) private patientConsent;
    
    // Mapping to track consent expiration times
    mapping(string => mapping(address => uint256)) private consentExpiration;
    
    // Consent events
    event ConsentGranted(string patientId, address requester, uint256 expirationTime);
    event ConsentRevoked(string patientId, address requester);
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Modifier to verify the caller is the contract owner
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    /**
     * @dev Grant consent for a requester to access patient data
     * @param patientId The patient identifier
     * @param requester The address of the authorized data requester
     * @param durationDays The duration for which consent is valid (in days)
     */
    function grantConsent(string memory patientId, address requester, uint256 durationDays) public {
        // In production, this would include verification of patient identity
        // For simplicity, we're allowing any transaction to grant consent
        require(bytes(patientId).length > 0, "Patient ID cannot be empty");
        require(requester != address(0), "Requester address cannot be zero");
        require(durationDays > 0, "Duration must be greater than zero");
        
        patientConsent[patientId][requester] = true;
        
        // Set expiration time based on duration days
        uint256 expirationTime = block.timestamp + (durationDays * 1 days);
        consentExpiration[patientId][requester] = expirationTime;
        
        emit ConsentGranted(patientId, requester, expirationTime);
    }
    
    /**
     * @dev Revoke previously granted consent
     * @param patientId The patient identifier
     * @param requester The address of the data requester to revoke
     */
    function revokeConsent(string memory patientId, address requester) public {
        // In production, this would include verification of patient identity
        require(bytes(patientId).length > 0, "Patient ID cannot be empty");
        require(requester != address(0), "Requester address cannot be zero");
        
        patientConsent[patientId][requester] = false;
        consentExpiration[patientId][requester] = 0;
        
        emit ConsentRevoked(patientId, requester);
    }
    
    /**
     * @dev Check if a requester has consent to access patient data
     * @param patientId The patient identifier
     * @param requester The address of the data requester
     * @return bool True if requester has valid consent, false otherwise
     */
    function hasValidConsent(string memory patientId, address requester) public view returns (bool) {
        // Check if consent exists and hasn't expired
        bool hasConsent = patientConsent[patientId][requester];
        uint256 expiration = consentExpiration[patientId][requester];
        
        return hasConsent && (expiration > block.timestamp);
    }
    
    /**
     * @dev Get consent expiration time
     * @param patientId The patient identifier
     * @param requester The address of the data requester
     * @return uint256 The timestamp when consent expires (0 if no consent)
     */
    function getConsentExpiration(string memory patientId, address requester) public view returns (uint256) {
        return consentExpiration[patientId][requester];
    }
}
