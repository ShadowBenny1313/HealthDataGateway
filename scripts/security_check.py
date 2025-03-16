#!/usr/bin/env python3
"""
security_check.py - Security analysis tool for HealthData Gateway

This script performs basic security checks on the HealthData Gateway system,
including testing for common vulnerabilities, reviewing configuration settings,
and verifying security best practices.
"""

import os
import sys
import json
import requests
import logging
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("security_check")

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Constants
PROJECT_ROOT = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_FILE = REPORTS_DIR / f"security_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

# Ensure reports directory exists
REPORTS_DIR.mkdir(exist_ok=True)

def check_env_file():
    """Check .env file for security issues"""
    logger.info("Checking .env file...")
    
    env_file = PROJECT_ROOT / ".env"
    results = {
        "test_name": "Environment File Check",
        "issues": [],
        "passed": True
    }
    
    if not env_file.exists():
        results["issues"].append("ERROR: .env file not found")
        results["passed"] = False
        return results
    
    # Check for hardcoded secrets
    sensitive_patterns = [
        (r'SECRET_KEY\s*=\s*.{0,10}(development|test)', "Development/test secret key in .env file"),
        (r'PASSWORD\s*=\s*[\'"]?(password|admin|123)', "Simple password pattern found in .env file"),
        (r'JWT_SECRET_KEY\s*=\s*[\'"]?.{0,10}(secret|key|test)', "Simple JWT secret pattern in .env file"),
        (r'PRIVATE_KEY\s*=\s*.{1,100}', "Private key may be exposed in .env file")
    ]
    
    try:
        with open(env_file, 'r') as f:
            env_content = f.read()
            
            # Check for sensitive patterns
            for pattern, message in sensitive_patterns:
                if re.search(pattern, env_content, re.IGNORECASE):
                    results["issues"].append(f"WARNING: {message}")
                    results["passed"] = False
            
            # Check if .env in gitignore
            gitignore_file = PROJECT_ROOT / ".gitignore"
            if gitignore_file.exists():
                with open(gitignore_file, 'r') as gf:
                    gitignore_content = gf.read()
                    if ".env" not in gitignore_content:
                        results["issues"].append("WARNING: .env file not listed in .gitignore")
                        results["passed"] = False
            else:
                results["issues"].append("WARNING: No .gitignore file found")
                results["passed"] = False
    
    except Exception as e:
        results["issues"].append(f"ERROR checking .env file: {str(e)}")
        results["passed"] = False
    
    if results["passed"]:
        results["issues"].append("No issues found in .env file")
    
    return results

def check_dependency_vulnerabilities():
    """Check dependencies for known security vulnerabilities"""
    logger.info("Checking dependencies for vulnerabilities...")
    
    results = {
        "test_name": "Dependency Vulnerability Check",
        "issues": [],
        "passed": True
    }
    
    requirements_file = PROJECT_ROOT / "requirements.txt"
    if not requirements_file.exists():
        results["issues"].append("ERROR: requirements.txt file not found")
        results["passed"] = False
        return results
    
    # This would use a tool like safety in a real scenario
    # For this simulation, we'll check for some known problematic versions
    problematic_deps = {
        "django": ["<3.0.14", "<2.2.24"],  # Example versions with known issues
        "flask": ["<1.0"],
        "requests": ["<2.20.0"],
        "pyjwt": ["<1.7.1"],
        "cryptography": ["<3.3.2"],
    }
    
    try:
        with open(requirements_file, 'r') as f:
            requirements = f.readlines()
            
            for req in requirements:
                req = req.strip()
                if not req or req.startswith('#'):
                    continue
                
                # Extract package name and version
                if '==' in req:
                    package, version = req.split('==', 1)
                elif '>=' in req:
                    package, version = req.split('>=', 1)
                else:
                    results["issues"].append(f"WARNING: Unpinned dependency: {req}")
                    results["passed"] = False
                    continue
                
                package = package.lower()
                
                # Check against problematic versions
                if package in problematic_deps:
                    for bad_version in problematic_deps[package]:
                        if bad_version.startswith('<') and version < bad_version[1:]:
                            results["issues"].append(f"CRITICAL: {package} version {version} has known vulnerabilities, update to newer version")
                            results["passed"] = False
    
    except Exception as e:
        results["issues"].append(f"ERROR checking dependencies: {str(e)}")
        results["passed"] = False
    
    if results["passed"]:
        results["issues"].append("No immediate dependency vulnerabilities found")
        
    results["issues"].append("NOTE: For production, run a full dependency scanner like Safety or Snyk")
    
    return results

def check_api_security():
    """Check API endpoints for basic security issues"""
    logger.info("Checking API security...")
    
    results = {
        "test_name": "API Security Check",
        "issues": [],
        "passed": True
    }
    
    # Check if the API is running
    try:
        response = requests.get("http://localhost:8000/docs", timeout=3)
        if response.status_code != 200:
            results["issues"].append("WARNING: API not running, skipping live API checks")
            results["passed"] = False
            return results
    except requests.exceptions.RequestException:
        results["issues"].append("WARNING: API not running, skipping live API checks")
        results["passed"] = False
        return results
    
    # Basic security checks on the API
    checks = [
        {
            "name": "API exposes OpenAPI docs",
            "endpoint": "/docs",
            "expected_code": 200,
            "message": "API documentation is exposed. This is fine for development but should be restricted in production."
        },
        {
            "name": "Authentication required",
            "endpoint": "/api/hospitals/",
            "expected_code": 401,
            "message": "Endpoints should require authentication"
        },
        {
            "name": "CORS verification",
            "endpoint": "/api/hospitals/",
            "expected_code": 401,
            "headers": {"Origin": "https://malicious-site.com"},
            "check_headers": {"access-control-allow-origin": "https://malicious-site.com"},
            "message": "CORS headers should not allow arbitrary origins"
        }
    ]
    
    for check in checks:
        try:
            headers = check.get("headers", {})
            response = requests.get(f"http://localhost:8000{check['endpoint']}", headers=headers, timeout=3)
            
            if response.status_code != check["expected_code"]:
                results["issues"].append(f"WARNING: {check['name']} - Got status {response.status_code}, expected {check['expected_code']}")
                results["passed"] = False
            
            if "check_headers" in check:
                for header, value in check["check_headers"].items():
                    if header in response.headers and response.headers[header] == value:
                        results["issues"].append(f"WARNING: {check['name']} - {check['message']}")
                        results["passed"] = False
        
        except requests.exceptions.RequestException as e:
            results["issues"].append(f"ERROR checking {check['name']}: {str(e)}")
            results["passed"] = False
    
    return results

def check_code_security():
    """Perform static code analysis for security issues"""
    logger.info("Performing static code analysis...")
    
    results = {
        "test_name": "Static Code Analysis",
        "issues": [],
        "passed": True
    }
    
    # In a real scenario, this would use a tool like Bandit
    # For this simulation, we'll check for common security code patterns
    security_patterns = [
        (r'os\.system\(', "Potential command injection vulnerability"),
        (r'subprocess\.call\(.+, shell=True', "Potential command injection vulnerability"),
        (r'eval\(', "Potential code execution vulnerability"),
        (r'exec\(', "Potential code execution vulnerability"),
        (r'pickle\.loads?\(', "Potential deserialization vulnerability"),
        (r'return\s+User\.objects\.filter\(.+request\.(GET|POST)', "Potential ORM injection vulnerability"),
        (r'\.execute\([\'"]SELECT.+\+', "Potential SQL injection vulnerability"),
        (r'md5\(', "Weak cryptographic hash function")
    ]
    
    # Directories to scan
    scan_dirs = ["src"]
    
    for scan_dir in scan_dirs:
        dir_path = PROJECT_ROOT / scan_dir
        for path in dir_path.glob('**/*.py'):
            try:
                with open(path, 'r') as f:
                    code = f.read()
                    rel_path = path.relative_to(PROJECT_ROOT)
                    
                    for pattern, message in security_patterns:
                        for match in re.finditer(pattern, code):
                            line_num = code[:match.start()].count('\n') + 1
                            results["issues"].append(f"WARNING: {message} in {rel_path}:{line_num}")
                            results["passed"] = False
            
            except Exception as e:
                results["issues"].append(f"ERROR scanning {path}: {str(e)}")
                results["passed"] = False
    
    if results["passed"]:
        results["issues"].append("No immediate code security issues found")
    
    results["issues"].append("NOTE: For production, run a full code security scanner like Bandit")
    
    return results

def check_blockchain_security():
    """Check blockchain contracts for security issues"""
    logger.info("Checking blockchain contracts...")
    
    results = {
        "test_name": "Blockchain Security Check",
        "issues": [],
        "passed": True
    }
    
    # Check if contract files exist
    contract_files = [
        PROJECT_ROOT / "src" / "blockchain" / "consent.sol",
        PROJECT_ROOT / "src" / "blockchain" / "rewards.sol"
    ]
    
    for contract_file in contract_files:
        if not contract_file.exists():
            results["issues"].append(f"ERROR: Contract file {contract_file.name} not found")
            results["passed"] = False
            continue
        
        try:
            with open(contract_file, 'r') as f:
                code = f.read()
                
                # Check for common smart contract vulnerabilities
                vulnerabilities = [
                    (r'selfdestruct\(', "Contract can be self-destructed"),
                    (r'block\.(timestamp|blockhash|difficulty|number)', "Using block properties for randomness is vulnerable"),
                    (r'.*\.transfer\(', "Using transfer() instead of call() may fail silently"),
                    (r'require\(.*\)', "Missing message in require statement")
                ]
                
                for pattern, message in vulnerabilities:
                    if re.search(pattern, code):
                        results["issues"].append(f"WARNING: {message} in {contract_file.name}")
                        results["passed"] = False
        
        except Exception as e:
            results["issues"].append(f"ERROR scanning {contract_file.name}: {str(e)}")
            results["passed"] = False
    
    return results

def generate_report(all_results):
    """Generate comprehensive security report"""
    logger.info("Generating security report...")
    
    # Count issues by severity
    issue_counts = {
        "CRITICAL": 0,
        "ERROR": 0,
        "WARNING": 0
    }
    
    for result in all_results:
        for issue in result["issues"]:
            for severity in issue_counts.keys():
                if issue.startswith(severity):
                    issue_counts[severity] += 1
    
    # Calculate overall score (0-100)
    # Weighted by severity
    total_issues = sum(issue_counts.values())
    
    if total_issues == 0:
        score = 100
    else:
        weighted_score = 100 - (
            issue_counts["CRITICAL"] * 25 + 
            issue_counts["ERROR"] * 10 + 
            issue_counts["WARNING"] * 3
        )
        score = max(0, weighted_score)
    
    # Build the report
    report = {
        "project": "HealthData Gateway",
        "timestamp": datetime.now().isoformat(),
        "overall_score": score,
        "passed_all": all(result["passed"] for result in all_results),
        "issue_counts": issue_counts,
        "test_results": all_results
    }
    
    # Add recommendations based on issues
    recommendations = []
    if issue_counts["CRITICAL"] > 0:
        recommendations.append("Address all critical issues immediately before deployment")
    if issue_counts["ERROR"] > 0:
        recommendations.append("Fix all errors to ensure system reliability and security")
    if issue_counts["WARNING"] > 0:
        recommendations.append("Review warnings and address them according to your risk tolerance")
    
    if score < 50:
        recommendations.append("Consider a professional security audit before going to production")
    elif score < 80:
        recommendations.append("Perform additional security testing to improve security posture")
    
    report["recommendations"] = recommendations
    
    # Save the report
    with open(REPORT_FILE, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Security report saved to {REPORT_FILE}")
    
    return report

def print_summary(report):
    """Print a summary of the security report"""
    print("\n" + "="*80)
    print(f" HEALTH DATA GATEWAY SECURITY REPORT - {datetime.now().strftime('%Y-%m-%d')}")
    print("="*80)
    
    print(f"\nOverall Security Score: {report['overall_score']:.1f}/100")
    print(f"Status: {'PASSED' if report['passed_all'] else 'FAILED'}")
    
    print("\nIssue Summary:")
    for severity, count in report["issue_counts"].items():
        print(f"  {severity}: {count}")
    
    print("\nTest Results:")
    for result in report["test_results"]:
        status = "PASSED" if result["passed"] else "FAILED"
        print(f"  {result['test_name']}: {status}")
    
    print("\nRecommendations:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print(f"\nDetailed report saved to: {REPORT_FILE}")
    print("="*80 + "\n")

def main():
    """Main function to run security checks"""
    logger.info("Starting HealthData Gateway security check...")
    
    # Run all checks
    results = [
        check_env_file(),
        check_dependency_vulnerabilities(),
        check_api_security(),
        check_code_security(),
        check_blockchain_security()
    ]
    
    # Generate and save report
    report = generate_report(results)
    
    # Print summary
    print_summary(report)
    
    # Return exit code based on results
    return 0 if report["passed_all"] else 1

if __name__ == "__main__":
    sys.exit(main())
