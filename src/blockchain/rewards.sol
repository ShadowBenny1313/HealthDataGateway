// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
 * @title HealthDataRewards
 * @dev Smart contract for managing rewards for health data contributions
 */
contract HealthDataRewards {
    address public owner;
    
    // Token details
    string public name = "HealthData Token";
    string public symbol = "HDT";
    uint8 public decimals = 18;
    uint256 public totalSupply = 100000000 * 10**18; // 100 million tokens
    
    // Mapping of address to token balance
    mapping(address => uint256) private balances;
    
    // Mapping of address to mapping of address to allowance
    mapping(address => mapping(address => uint256)) private allowed;
    
    // Reward tiers and rates (in tokens)
    uint256 public baseRewardRate = 10 * 10**18; // 10 tokens
    
    // Data quality multipliers (percentage)
    uint256 public highQualityMultiplier = 150; // 150% of base rate
    uint256 public mediumQualityMultiplier = 100; // 100% of base rate
    uint256 public lowQualityMultiplier = 50; // 50% of base rate
    
    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event RewardIssued(address indexed to, uint256 amount, string dataType, uint256 qualityLevel);
    
    constructor() {
        owner = msg.sender;
        balances[owner] = totalSupply;
    }
    
    /**
     * @dev Modifier to verify the caller is the contract owner
     */
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    /**
     * @dev Get the token balance of an account
     * @param _owner The address to query the balance of
     * @return uint256 The token balance
     */
    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
    }
    
    /**
     * @dev Transfer tokens to a specified address
     * @param _to The address to transfer to
     * @param _value The amount to be transferred
     * @return bool Success of the transfer
     */
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(_to != address(0), "Transfer to zero address");
        require(_value <= balances[msg.sender], "Insufficient balance");
        
        balances[msg.sender] -= _value;
        balances[_to] += _value;
        
        emit Transfer(msg.sender, _to, _value);
        return true;
    }
    
    /**
     * @dev Approve the passed address to spend the specified amount of tokens
     * @param _spender The address which will spend the funds
     * @param _value The amount of tokens to be spent
     * @return bool Success of the approval
     */
    function approve(address _spender, uint256 _value) public returns (bool) {
        require(_spender != address(0), "Approve to zero address");
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }
    
    /**
     * @dev Get the allowance granted to a spender
     * @param _owner The address which owns the tokens
     * @param _spender The address which will spend the tokens
     * @return uint256 The amount of tokens allowed to be spent
     */
    function allowance(address _owner, address _spender) public view returns (uint256) {
        return allowed[_owner][_spender];
    }
    
    /**
     * @dev Transfer tokens from one address to another
     * @param _from The address which you want to send tokens from
     * @param _to The address which you want to transfer to
     * @param _value The amount of tokens to be transferred
     * @return bool Success of the transfer
     */
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        require(_to != address(0), "Transfer to zero address");
        require(_value <= balances[_from], "Insufficient balance");
        require(_value <= allowed[_from][msg.sender], "Insufficient allowance");
        
        balances[_from] -= _value;
        balances[_to] += _value;
        allowed[_from][msg.sender] -= _value;
        
        emit Transfer(_from, _to, _value);
        return true;
    }
    
    /**
     * @dev Issue rewards to a user for contributing health data
     * @param _user The address of the user to reward
     * @param _dataType The type of data contributed (hospital, pharmacy, wearable)
     * @param _qualityLevel The quality level of the data (0=low, 1=medium, 2=high)
     * @return bool Success of the reward issuance
     */
    function issueReward(address _user, string memory _dataType, uint256 _qualityLevel) public onlyOwner returns (bool) {
        require(_user != address(0), "Reward to zero address");
        require(_qualityLevel <= 2, "Invalid quality level");
        require(bytes(_dataType).length > 0, "Data type cannot be empty");
        
        uint256 rewardAmount = calculateReward(_dataType, _qualityLevel);
        
        // Ensure the contract owner has enough tokens
        require(balances[owner] >= rewardAmount, "Insufficient rewards balance");
        
        // Transfer the reward to the user
        balances[owner] -= rewardAmount;
        balances[_user] += rewardAmount;
        
        emit Transfer(owner, _user, rewardAmount);
        emit RewardIssued(_user, rewardAmount, _dataType, _qualityLevel);
        
        return true;
    }
    
    /**
     * @dev Calculate reward amount based on data type and quality
     * @param _dataType The type of data contributed
     * @param _qualityLevel The quality level of the data (0=low, 1=medium, 2=high)
     * @return uint256 The reward amount
     */
    function calculateReward(string memory _dataType, uint256 _qualityLevel) public view returns (uint256) {
        // Base reward amount depends on data type
        uint256 baseAmount = baseRewardRate;
        
        // Apply data type multiplier if needed
        // For example, hospital data might be more valuable than wearable data
        
        // Apply quality multiplier
        uint256 qualityMultiplier;
        if (_qualityLevel == 2) {
            qualityMultiplier = highQualityMultiplier;
        } else if (_qualityLevel == 1) {
            qualityMultiplier = mediumQualityMultiplier;
        } else {
            qualityMultiplier = lowQualityMultiplier;
        }
        
        // Calculate final reward
        return (baseAmount * qualityMultiplier) / 100;
    }
    
    /**
     * @dev Update reward parameters (only owner)
     * @param _baseRate New base reward rate
     * @param _highMult New high quality multiplier
     * @param _medMult New medium quality multiplier
     * @param _lowMult New low quality multiplier
     */
    function updateRewardParameters(
        uint256 _baseRate,
        uint256 _highMult,
        uint256 _medMult,
        uint256 _lowMult
    ) public onlyOwner {
        baseRewardRate = _baseRate;
        highQualityMultiplier = _highMult;
        mediumQualityMultiplier = _medMult;
        lowQualityMultiplier = _lowMult;
    }
}
