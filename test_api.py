#!/usr/bin/env python3
"""
Liberation System API Test Suite
Comprehensive API endpoint testing
"""

import asyncio
import aiohttp
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.tests_passed = 0
        self.tests_failed = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method, endpoint, data=None, expected_status=200, test_name=None):
        """Test a single API endpoint"""
        if test_name is None:
            test_name = f"{method.upper()} {endpoint}"
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    result = await response.json()
                    status = response.status
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
                    status = response.status
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    result = await response.json()
                    status = response.status
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if status == expected_status:
                self.tests_passed += 1
                console.print(f"✅ {test_name}: {status}", style="green")
                return result
            else:
                self.tests_failed += 1
                console.print(f"❌ {test_name}: Expected {expected_status}, got {status}", style="red")
                return None
                
        except Exception as e:
            self.tests_failed += 1
            console.print(f"❌ {test_name}: Error - {str(e)}", style="red")
            return None
    
    async def run_all_tests(self):
        """Run comprehensive API tests"""
        console.print(Panel.fit("🧪 Liberation System API Tests", style="bold blue"))
        
        # Test 1: Root endpoint
        await self.test_endpoint("GET", "/", test_name="Root Endpoint")
        
        # Test 2: Health check
        await self.test_endpoint("GET", "/health", test_name="Health Check")
        
        # Test 3: System stats
        await self.test_endpoint("GET", "/api/v1/stats", test_name="System Stats")
        
        # Test 4: Get all humans
        humans = await self.test_endpoint("GET", "/api/v1/humans", test_name="Get All Humans")
        
        # Test 5: Create a new human
        new_human = {
            "id": "human_api_test_001",
            "weekly_flow": 800.0,
            "housing_credit": 104000.0,
            "investment_pool": 104000.0,
            "status": "active"
        }
        await self.test_endpoint("POST", "/api/v1/humans", data=new_human, test_name="Create Human")
        
        # Test 6: Get specific human
        await self.test_endpoint("GET", "/api/v1/humans/human_api_test_001", test_name="Get Specific Human")
        
        # Test 7: Security check
        security_request = {
            "human_id": "human_api_test_001",
            "resource_id": "test_resource",
            "action": "access"
        }
        await self.test_endpoint("POST", "/api/v1/security/check", data=security_request, test_name="Security Check")
        
        # Test 8: Run distribution
        distribution_request = {
            "human_ids": ["human_api_test_001"],
            "amount_override": 1000.0
        }
        await self.test_endpoint("POST", "/api/v1/distribute", data=distribution_request, test_name="Resource Distribution")
        
        # Test 9: Get automation stats
        await self.test_endpoint("GET", "/api/v1/automation/stats", test_name="Automation Stats")
        
        # Test 10: Run automation task
        await self.test_endpoint("POST", "/api/v1/automation/run-task/monitor_system", test_name="Run Automation Task")
        
        # Test 11: Resource health check
        await self.test_endpoint("GET", "/api/v1/health", test_name="Resource Health Check")
        
        # Test 12: Deactivate human
        await self.test_endpoint("DELETE", "/api/v1/humans/human_api_test_001", test_name="Deactivate Human")
        
        # Display results
        self.display_results()
    
    def display_results(self):
        """Display test results"""
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Summary table
        table = Table(title="API Test Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Tests", str(total_tests))
        table.add_row("Passed", str(self.tests_passed))
        table.add_row("Failed", str(self.tests_failed))
        table.add_row("Success Rate", f"{success_rate:.1f}%")
        
        console.print(table)
        
        # Final status
        if self.tests_failed == 0:
            console.print(Panel("🎉 ALL API TESTS PASSED! REST API is fully operational.", style="bold green"))
        else:
            console.print(Panel(f"⚠️  {self.tests_failed} API tests failed. Check server logs.", style="bold red"))

async def main():
    """Run API tests"""
    console.print("🌟 Liberation System API Test Suite", style="bold cyan")
    console.print("📡 Testing all endpoints...", style="yellow")
    
    try:
        async with APITester() as tester:
            await tester.run_all_tests()
    except Exception as e:
        console.print(f"❌ Test suite failed: {e}", style="red")

if __name__ == "__main__":
    asyncio.run(main())
