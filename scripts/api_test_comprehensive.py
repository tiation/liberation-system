#!/usr/bin/env python3
"""
🧪 Comprehensive API Testing Script
=====================================

Enterprise-grade API testing for the Liberation System REST API.
Tests all endpoints, validates responses, and generates reports.
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiohttp
import logging
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.panel import Panel
from rich.text import Text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

@dataclass
class TestResult:
    """Test result data structure"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None

@dataclass
class TestReport:
    """Comprehensive test report"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    average_response_time: float
    total_test_time: float
    test_results: List[TestResult]
    timestamp: str

class LiberationAPITester:
    """Enterprise-grade API testing framework"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: List[TestResult] = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, 
                          endpoint: str, 
                          method: str = "GET", 
                          data: Optional[Dict] = None,
                          expected_status: int = 200) -> TestResult:
        """Test a single API endpoint"""
        
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method, 
                url, 
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                response_data = await response.json() if response.content_type == 'application/json' else None
                
                success = response.status == expected_status
                error_message = None if success else f"Expected {expected_status}, got {response.status}"
                
                result = TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status,
                    response_time=response_time,
                    success=success,
                    error_message=error_message,
                    response_data=response_data
                )
                
                self.results.append(result)
                return result
                
        except Exception as e:
            response_time = time.time() - start_time
            result = TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
            self.results.append(result)
            return result
    
    async def run_comprehensive_tests(self) -> TestReport:
        """Run comprehensive API test suite"""
        
        console.print("🚀 Starting Liberation System API Tests", style="bold cyan")
        console.print("="*60, style="cyan")
        
        start_time = time.time()
        
        with Progress() as progress:
            test_task = progress.add_task("Running API tests...", total=15)
            
            # Test cases
            test_cases = [
                # Basic system endpoints
                {"endpoint": "/", "method": "GET", "expected": 200},
                {"endpoint": "/health", "method": "GET", "expected": 200},
                
                # Human management
                {"endpoint": "/api/v1/humans", "method": "GET", "expected": 200},
                {"endpoint": "/api/v1/humans", "method": "POST", "expected": 200, 
                 "data": {"id": "test_human_001", "weekly_flow": 800}},
                {"endpoint": "/api/v1/humans/test_human_001", "method": "GET", "expected": 200},
                
                # Resource distribution
                {"endpoint": "/api/v1/distribute", "method": "POST", "expected": 200},
                {"endpoint": "/api/v1/stats", "method": "GET", "expected": 200},
                
                # Security
                {"endpoint": "/api/v1/security/check", "method": "POST", "expected": 200,
                 "data": {"human_id": "test_human_001", "resource_id": "test_resource", "action": "access"}},
                
                # Automation
                {"endpoint": "/api/v1/automation/stats", "method": "GET", "expected": 200},
                {"endpoint": "/api/v1/automation/run-task/test_task", "method": "POST", "expected": 200},
                
                # Documentation endpoints
                {"endpoint": "/docs", "method": "GET", "expected": 200},
                {"endpoint": "/redoc", "method": "GET", "expected": 200},
                {"endpoint": "/openapi.json", "method": "GET", "expected": 200},
                
                # Edge cases
                {"endpoint": "/api/v1/humans/nonexistent", "method": "GET", "expected": 404},
                {"endpoint": "/api/v1/humans/test_human_001", "method": "DELETE", "expected": 200},
            ]
            
            # Run tests
            for test_case in test_cases:
                result = await self.test_endpoint(
                    test_case["endpoint"],
                    test_case["method"],
                    test_case.get("data"),
                    test_case["expected"]
                )
                
                # Display result
                status_emoji = "✅" if result.success else "❌"
                console.print(f"{status_emoji} {result.method} {result.endpoint} - {result.status_code} ({result.response_time:.3f}s)")
                
                progress.advance(test_task)
                await asyncio.sleep(0.1)  # Small delay for readability
        
        total_time = time.time() - start_time
        
        # Generate report
        report = TestReport(
            total_tests=len(self.results),
            passed_tests=sum(1 for r in self.results if r.success),
            failed_tests=sum(1 for r in self.results if not r.success),
            average_response_time=sum(r.response_time for r in self.results) / len(self.results) if self.results else 0,
            total_test_time=total_time,
            test_results=self.results,
            timestamp=datetime.now().isoformat()
        )
        
        return report
    
    def display_report(self, report: TestReport):
        """Display comprehensive test report"""
        
        # Summary table
        table = Table(title="🧪 Liberation System API Test Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Tests", str(report.total_tests))
        table.add_row("Passed", str(report.passed_tests))
        table.add_row("Failed", str(report.failed_tests))
        table.add_row("Success Rate", f"{(report.passed_tests / report.total_tests * 100):.1f}%")
        table.add_row("Average Response Time", f"{report.average_response_time:.3f}s")
        table.add_row("Total Test Time", f"{report.total_test_time:.3f}s")
        
        console.print(table)
        
        # Failed tests details
        if report.failed_tests > 0:
            console.print("\n❌ Failed Tests:", style="bold red")
            for result in report.test_results:
                if not result.success:
                    console.print(f"  • {result.method} {result.endpoint}: {result.error_message}")
        
        # Performance insights
        if report.average_response_time > 1.0:
            console.print("\n⚠️  Performance Warning: Average response time > 1s", style="yellow")
        else:
            console.print("\n⚡ Performance: Excellent response times", style="green")
    
    def save_report(self, report: TestReport, filename: str = "api_test_report.json"):
        """Save test report to JSON file"""
        
        # Convert report to dict for JSON serialization
        report_dict = asdict(report)
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        console.print(f"📊 Test report saved to {filename}", style="green")

async def main():
    """Main test execution"""
    
    try:
        async with LiberationAPITester() as tester:
            # Run comprehensive tests
            report = await tester.run_comprehensive_tests()
            
            # Display results
            console.print("\n" + "="*60, style="cyan")
            tester.display_report(report)
            
            # Save report
            tester.save_report(report)
            
            # Final status
            if report.failed_tests == 0:
                console.print("\n🎉 All tests passed! Liberation System API is ready for production.", style="bold green")
            else:
                console.print(f"\n⚠️  {report.failed_tests} tests failed. Please check the API server.", style="bold yellow")
                
    except Exception as e:
        console.print(f"❌ Test execution failed: {e}", style="bold red")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
