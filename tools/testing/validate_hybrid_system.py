#!/usr/bin/env python3

import requests
import time
import json
import sys
import subprocess
import os
from pathlib import Path

class SystemValidator:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.tests_passed = 0
        self.tests_failed = 0
        
    def log(self, message, level="INFO"):
        colors = {
            "INFO": "\033[0;32m",
            "WARN": "\033[1;33m", 
            "ERROR": "\033[0;31m",
            "RESET": "\033[0m"
        }
        print(f"{colors.get(level, '')}{message}{colors['RESET']}")
        
    def test_backend_health(self):
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✓ Backend health check passed")
                self.tests_passed += 1
                return True
        except Exception as e:
            self.log(f"✗ Backend health check failed: {e}", "ERROR")
            self.tests_failed += 1
            return False
            
    def test_api_docs(self):
        """Test API documentation endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log("✓ API documentation accessible")
                self.tests_passed += 1
                return True
        except Exception as e:
            self.log(f"✗ API docs failed: {e}", "ERROR")
            self.tests_failed += 1
            return False
            
    def test_frontend_access(self):
        """Test frontend accessibility"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log("✓ Frontend accessible")
                self.tests_passed += 1
                return True
        except Exception as e:
            self.log(f"✗ Frontend access failed: {e}", "ERROR")
            self.tests_failed += 1
            return False
            
    def test_database_connection(self):
        """Test database connectivity through API"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("database") == "connected":
                    self.log("✓ Database connection verified")
                    self.tests_passed += 1
                    return True
        except Exception as e:
            self.log(f"✗ Database connection test failed: {e}", "ERROR")
            self.tests_failed += 1
            return False
            
    def test_report_generation_endpoint(self):
        """Test report generation endpoint (without full generation)"""
        try:
            # Test with invalid symbol to check endpoint exists
            response = requests.post(
                f"{self.backend_url}/api/v1/generate-report",
                json={"symbol": "INVALID_TEST"},
                timeout=5
            )
            # Should return 400 for invalid symbol, not 404 for missing endpoint
            if response.status_code in [400, 422]:
                self.log("✓ Report generation endpoint accessible")
                self.tests_passed += 1
                return True
        except Exception as e:
            self.log(f"✗ Report generation endpoint test failed: {e}", "ERROR")
            self.tests_failed += 1
            return False
            
    def test_docker_services(self):
        """Test Docker services are running"""
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "--services", "--filter", "status=running"],
                capture_output=True, text=True, timeout=10
            )
            running_services = result.stdout.strip().split('\n')
            
            required_services = ["postgres", "redis"]
            for service in required_services:
                if service in running_services:
                    self.log(f"✓ {service.capitalize()} service running")
                    self.tests_passed += 1
                else:
                    self.log(f"✗ {service.capitalize()} service not running", "ERROR")
                    self.tests_failed += 1
                    
        except Exception as e:
            self.log(f"✗ Docker services check failed: {e}", "ERROR")
            self.tests_failed += 1
            
    def test_file_structure(self):
        """Validate required files and directories exist"""
        required_paths = [
            "backend/app/main.py",
            "frontend-react/package.json",
            ".env",
            "docker-compose.yml"
        ]
        
        for path in required_paths:
            if Path(path).exists():
                self.log(f"✓ {path} exists")
                self.tests_passed += 1
            else:
                self.log(f"✗ {path} missing", "ERROR")
                self.tests_failed += 1
                
    def test_process_management(self):
        """Test that PID files exist and processes are running"""
        pid_dir = Path("pids")
        if not pid_dir.exists():
            self.log("✗ PID directory not found", "ERROR")
            self.tests_failed += 1
            return
            
        for service in ["backend", "frontend"]:
            pid_file = pid_dir / f"{service}.pid"
            if pid_file.exists():
                try:
                    pid = int(pid_file.read_text().strip())
                    # Check if process is running
                    os.kill(pid, 0)
                    self.log(f"✓ {service.capitalize()} process running (PID: {pid})")
                    self.tests_passed += 1
                except (ProcessLookupError, ValueError):
                    self.log(f"✗ {service.capitalize()} process not running", "ERROR")
                    self.tests_failed += 1
            else:
                self.log(f"✗ {service.capitalize()} PID file missing", "ERROR")
                self.tests_failed += 1
                
    def run_all_tests(self):
        """Run all validation tests"""
        self.log("Starting MarketMind Pro system validation...")
        
        # File structure test (runs first)
        self.test_file_structure()
        
        # Docker services test
        self.test_docker_services()
        
        # Process management test
        self.test_process_management()
        
        # Wait a moment for services to be fully ready
        time.sleep(2)
        
        # Backend tests
        self.test_backend_health()
        self.test_api_docs()
        self.test_database_connection()
        self.test_report_generation_endpoint()
        
        # Frontend test
        self.test_frontend_access()
        
        # Summary
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        self.log(f"\nValidation Summary:")
        self.log(f"Tests passed: {self.tests_passed}")
        self.log(f"Tests failed: {self.tests_failed}")
        self.log(f"Success rate: {success_rate:.1f}%")
        
        if self.tests_failed == 0:
            self.log("🎉 All tests passed! System is ready.", "INFO")
            return True
        else:
            self.log(f"❌ {self.tests_failed} tests failed. Check logs for details.", "ERROR")
            return False

def main():
    validator = SystemValidator()
    success = validator.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()