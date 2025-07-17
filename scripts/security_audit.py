#!/usr/bin/env python3
"""
🔒 Liberation System Security Audit
===================================

Enterprise-grade security audit script following the trust-by-default
philosophy while ensuring operational security.
"""

import asyncio
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import socket
import ssl
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.text import Text

console = Console()

class SecurityAuditor:
    """Enterprise security audit system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.audit_results: Dict[str, Any] = {}
        self.vulnerabilities: List[Dict] = []
        self.recommendations: List[Dict] = []
        
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        console.print("🔒 Starting Liberation System Security Audit", style="bold cyan")
        console.print("=" * 55)
        
        with Progress() as progress:
            task = progress.add_task("Running security audit...", total=8)
            
            # Code security audit
            console.print("🔍 Auditing code security...")
            self.audit_code_security()
            progress.advance(task)
            
            # Dependency security audit
            console.print("📦 Auditing dependencies...")
            self.audit_dependencies()
            progress.advance(task)
            
            # Configuration security audit
            console.print("⚙️  Auditing configuration...")
            self.audit_configuration()
            progress.advance(task)
            
            # Network security audit
            console.print("🌐 Auditing network security...")
            self.audit_network_security()
            progress.advance(task)
            
            # API security audit
            console.print("📡 Auditing API security...")
            asyncio.run(self.audit_api_security())
            progress.advance(task)
            
            # File permissions audit
            console.print("📁 Auditing file permissions...")
            self.audit_file_permissions()
            progress.advance(task)
            
            # Docker security audit
            console.print("🐳 Auditing Docker security...")
            self.audit_docker_security()
            progress.advance(task)
            
            # Generate report
            console.print("📊 Generating security report...")
            self.generate_security_report()
            progress.advance(task)
        
        return self.audit_results
    
    def audit_code_security(self):
        """Audit code for security vulnerabilities"""
        console.print("  Scanning Python code for security issues...")
        
        # Run bandit security scanner
        try:
            result = subprocess.run(
                ["bandit", "-r", str(self.project_root), "-f", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                bandit_results = json.loads(result.stdout)
                self.audit_results["bandit_scan"] = {
                    "status": "completed",
                    "issues_found": len(bandit_results.get("results", [])),
                    "results": bandit_results
                }
                
                # Process bandit results
                for issue in bandit_results.get("results", []):
                    self.vulnerabilities.append({
                        "type": "code",
                        "severity": issue.get("issue_severity", "MEDIUM"),
                        "confidence": issue.get("issue_confidence", "MEDIUM"),
                        "description": issue.get("issue_text", ""),
                        "file": issue.get("filename", ""),
                        "line": issue.get("line_number", 0),
                        "tool": "bandit"
                    })
                
                console.print(f"    ✅ Bandit scan completed: {len(bandit_results.get('results', []))} issues found")
            else:
                console.print("    ⚠️  Bandit scan failed")
                self.audit_results["bandit_scan"] = {"status": "failed", "error": result.stderr}
        
        except FileNotFoundError:
            console.print("    ⚠️  Bandit not installed, skipping code security scan")
            self.audit_results["bandit_scan"] = {"status": "skipped", "reason": "bandit not installed"}
        
        # Manual code security checks
        self.audit_results["manual_code_checks"] = self.manual_code_security_checks()
    
    def manual_code_security_checks(self) -> Dict[str, Any]:
        """Manual code security checks"""
        issues = []
        
        # Check for hardcoded secrets
        secret_patterns = [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"token\s*=\s*['\"][^'\"]+['\"]"
        ]
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                for pattern in secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_number = content[:match.start()].count('\\n') + 1
                        issues.append({
                            "type": "hardcoded_secret",
                            "severity": "HIGH",
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": line_number,
                            "description": f"Potential hardcoded secret: {match.group()}"
                        })
            except Exception as e:
                console.print(f"    ⚠️  Error checking {py_file}: {e}")
        
        # Check for SQL injection vulnerabilities
        sql_patterns = [
            r"execute\s*\(\s*['\"].*%.*['\"]",
            r"cursor\.execute\s*\(\s*['\"].*\+.*['\"]",
            r"query\s*=\s*['\"].*%.*['\"]"
        ]
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                for pattern in sql_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_number = content[:match.start()].count('\\n') + 1
                        issues.append({
                            "type": "sql_injection",
                            "severity": "HIGH",
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": line_number,
                            "description": f"Potential SQL injection: {match.group()}"
                        })
            except Exception as e:
                console.print(f"    ⚠️  Error checking {py_file}: {e}")
        
        return {
            "total_issues": len(issues),
            "issues": issues
        }
    
    def audit_dependencies(self):
        """Audit dependencies for security vulnerabilities"""
        console.print("  Checking Python dependencies...")
        
        # Check for known vulnerable packages
        try:
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                self.audit_results["dependencies"] = {
                    "python_packages": len(packages),
                    "packages": packages
                }
                
                # Check for outdated packages
                outdated_result = subprocess.run(
                    ["pip", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True
                )
                
                if outdated_result.returncode == 0:
                    outdated = json.loads(outdated_result.stdout)
                    self.audit_results["dependencies"]["outdated_packages"] = len(outdated)
                    
                    for package in outdated:
                        self.recommendations.append({
                            "type": "dependency_update",
                            "priority": "MEDIUM",
                            "description": f"Update {package['name']} from {package['version']} to {package['latest_version']}"
                        })
                
                console.print(f"    ✅ Found {len(packages)} Python packages")
            else:
                console.print("    ⚠️  Failed to list Python packages")
        
        except Exception as e:
            console.print(f"    ⚠️  Error checking dependencies: {e}")
        
        # Check Node.js dependencies
        console.print("  Checking Node.js dependencies...")
        
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    audit_data = json.loads(result.stdout)
                    self.audit_results["npm_audit"] = audit_data
                    
                    vulnerabilities = audit_data.get("vulnerabilities", {})
                    for vuln_name, vuln_data in vulnerabilities.items():
                        self.vulnerabilities.append({
                            "type": "npm_dependency",
                            "severity": vuln_data.get("severity", "MEDIUM").upper(),
                            "package": vuln_name,
                            "description": vuln_data.get("title", "NPM vulnerability"),
                            "tool": "npm_audit"
                        })
                    
                    console.print(f"    ✅ NPM audit completed: {len(vulnerabilities)} vulnerabilities found")
                else:
                    console.print("    ⚠️  NPM audit failed")
            
            except Exception as e:
                console.print(f"    ⚠️  Error running NPM audit: {e}")
        else:
            console.print("    ℹ️  No package.json found, skipping NPM audit")
    
    def audit_configuration(self):
        """Audit configuration files for security issues"""
        console.print("  Checking configuration security...")
        
        config_issues = []
        
        # Check Docker configuration
        docker_compose = self.project_root / "docker-compose.yml"
        if docker_compose.exists():
            try:
                with open(docker_compose, 'r') as f:
                    content = f.read()
                    
                # Check for default passwords
                if "password" in content.lower():
                    config_issues.append({
                        "type": "default_password",
                        "severity": "HIGH",
                        "file": "docker-compose.yml",
                        "description": "Default passwords detected in Docker configuration"
                    })
                
                # Check for exposed ports
                if "ports:" in content:
                    config_issues.append({
                        "type": "exposed_ports",
                        "severity": "MEDIUM",
                        "file": "docker-compose.yml",
                        "description": "Ports exposed in Docker configuration"
                    })
                
            except Exception as e:
                console.print(f"    ⚠️  Error checking Docker config: {e}")
        
        # Check environment files
        env_files = [".env", ".env.local", ".env.production"]
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                try:
                    with open(env_path, 'r') as f:
                        content = f.read()
                        
                    # Check for sensitive data
                    if any(keyword in content.lower() for keyword in ["password", "secret", "key", "token"]):
                        config_issues.append({
                            "type": "sensitive_env",
                            "severity": "HIGH",
                            "file": env_file,
                            "description": "Sensitive data in environment file"
                        })
                
                except Exception as e:
                    console.print(f"    ⚠️  Error checking {env_file}: {e}")
        
        self.audit_results["configuration_audit"] = {
            "issues_found": len(config_issues),
            "issues": config_issues
        }
        
        console.print(f"    ✅ Configuration audit completed: {len(config_issues)} issues found")
    
    def audit_network_security(self):
        """Audit network security configuration"""
        console.print("  Checking network security...")
        
        network_issues = []
        
        # Check for open ports
        common_ports = [22, 80, 443, 3000, 5432, 6379, 8000, 8080, 9090]
        open_ports = []
        
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        if open_ports:
            network_issues.append({
                "type": "open_ports",
                "severity": "MEDIUM",
                "description": f"Open ports detected: {', '.join(map(str, open_ports))}"
            })
        
        self.audit_results["network_audit"] = {
            "open_ports": open_ports,
            "issues": network_issues
        }
        
        console.print(f"    ✅ Network audit completed: {len(open_ports)} open ports found")
    
    async def audit_api_security(self):
        """Audit API security"""
        console.print("  Checking API security...")
        
        api_issues = []
        base_url = "http://localhost:8000"
        
        # Test common API endpoints
        test_endpoints = [
            "/",
            "/health",
            "/api/v1/stats",
            "/api/v1/humans",
            "/docs",
            "/admin"
        ]
        
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint in test_endpoints:
                    try:
                        async with session.get(f"{base_url}{endpoint}") as response:
                            # Check for sensitive information disclosure
                            if response.status == 200:
                                text = await response.text()
                                if any(keyword in text.lower() for keyword in ["password", "secret", "token"]):
                                    api_issues.append({
                                        "type": "information_disclosure",
                                        "severity": "HIGH",
                                        "endpoint": endpoint,
                                        "description": "Sensitive information exposed in API response"
                                    })
                            
                            # Check for missing security headers
                            security_headers = ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection"]
                            missing_headers = [h for h in security_headers if h not in response.headers]
                            
                            if missing_headers:
                                api_issues.append({
                                    "type": "missing_security_headers",
                                    "severity": "MEDIUM",
                                    "endpoint": endpoint,
                                    "description": f"Missing security headers: {', '.join(missing_headers)}"
                                })
                    
                    except Exception as e:
                        console.print(f"    ⚠️  Error testing {endpoint}: {e}")
        
        except Exception as e:
            console.print(f"    ⚠️  Error during API security audit: {e}")
        
        self.audit_results["api_security"] = {
            "issues_found": len(api_issues),
            "issues": api_issues
        }
        
        console.print(f"    ✅ API security audit completed: {len(api_issues)} issues found")
    
    def audit_file_permissions(self):
        """Audit file permissions for security issues"""
        console.print("  Checking file permissions...")
        
        permission_issues = []
        
        # Check for world-writable files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    mode = stat.st_mode
                    
                    # Check if file is world-writable
                    if mode & 0o002:
                        permission_issues.append({
                            "type": "world_writable",
                            "severity": "HIGH",
                            "file": str(file_path.relative_to(self.project_root)),
                            "description": "File is world-writable"
                        })
                    
                    # Check for executable files that shouldn't be
                    if file_path.suffix in ['.py', '.js', '.json', '.md'] and mode & 0o111:
                        permission_issues.append({
                            "type": "unexpected_executable",
                            "severity": "MEDIUM",
                            "file": str(file_path.relative_to(self.project_root)),
                            "description": "Non-executable file has execute permissions"
                        })
                
                except Exception as e:
                    console.print(f"    ⚠️  Error checking permissions for {file_path}: {e}")
        
        self.audit_results["file_permissions"] = {
            "issues_found": len(permission_issues),
            "issues": permission_issues
        }
        
        console.print(f"    ✅ File permissions audit completed: {len(permission_issues)} issues found")
    
    def audit_docker_security(self):
        """Audit Docker security configuration"""
        console.print("  Checking Docker security...")
        
        docker_issues = []
        
        # Check Dockerfile
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            try:
                with open(dockerfile, 'r') as f:
                    content = f.read()
                
                # Check for running as root
                if "USER root" in content or "USER 0" in content:
                    docker_issues.append({
                        "type": "running_as_root",
                        "severity": "HIGH",
                        "file": "Dockerfile",
                        "description": "Container runs as root user"
                    })
                
                # Check for latest tag usage
                if ":latest" in content:
                    docker_issues.append({
                        "type": "latest_tag",
                        "severity": "MEDIUM",
                        "file": "Dockerfile",
                        "description": "Using :latest tag instead of specific version"
                    })
                
                # Check for ADD instead of COPY
                if "ADD " in content:
                    docker_issues.append({
                        "type": "add_vs_copy",
                        "severity": "LOW",
                        "file": "Dockerfile",
                        "description": "Using ADD instead of COPY"
                    })
            
            except Exception as e:
                console.print(f"    ⚠️  Error checking Dockerfile: {e}")
        
        # Check docker-compose.yml
        compose_file = self.project_root / "docker-compose.yml"
        if compose_file.exists():
            try:
                with open(compose_file, 'r') as f:
                    content = f.read()
                
                # Check for privileged mode
                if "privileged: true" in content:
                    docker_issues.append({
                        "type": "privileged_mode",
                        "severity": "HIGH",
                        "file": "docker-compose.yml",
                        "description": "Container running in privileged mode"
                    })
                
                # Check for host network mode
                if "network_mode: host" in content:
                    docker_issues.append({
                        "type": "host_network",
                        "severity": "MEDIUM",
                        "file": "docker-compose.yml",
                        "description": "Container using host network mode"
                    })
            
            except Exception as e:
                console.print(f"    ⚠️  Error checking docker-compose.yml: {e}")
        
        self.audit_results["docker_security"] = {
            "issues_found": len(docker_issues),
            "issues": docker_issues
        }
        
        console.print(f"    ✅ Docker security audit completed: {len(docker_issues)} issues found")
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        
        # Count total issues by severity
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for vuln in self.vulnerabilities:
            severity = vuln.get("severity", "MEDIUM")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Generate report
        report = {
            "audit_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "severity_breakdown": severity_counts,
                "recommendations_count": len(self.recommendations)
            },
            "vulnerabilities": self.vulnerabilities,
            "recommendations": self.recommendations,
            "detailed_results": self.audit_results
        }
        
        # Save report
        os.makedirs("logs", exist_ok=True)
        with open("logs/security_audit_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        self.display_audit_summary(report)
        
        return report
    
    def display_audit_summary(self, report: Dict):
        """Display security audit summary"""
        console.print("\\n" + "=" * 55)
        console.print("🔒 Security Audit Summary", style="bold cyan")
        console.print("=" * 55)
        
        # Summary table
        table = Table(title="Security Audit Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Status", style="yellow")
        
        summary = report["summary"]
        
        # Overall status
        total_vulns = summary["total_vulnerabilities"]
        high_vulns = summary["severity_breakdown"]["HIGH"]
        
        if high_vulns > 0:
            overall_status = "🔴 Critical"
        elif total_vulns > 0:
            overall_status = "🟡 Needs Attention"
        else:
            overall_status = "🟢 Good"
        
        table.add_row("Total Vulnerabilities", str(total_vulns), overall_status)
        table.add_row("High Severity", str(high_vulns), "🔴 Critical" if high_vulns > 0 else "🟢 Good")
        table.add_row("Medium Severity", str(summary["severity_breakdown"]["MEDIUM"]), "🟡 Warning" if summary["severity_breakdown"]["MEDIUM"] > 0 else "🟢 Good")
        table.add_row("Low Severity", str(summary["severity_breakdown"]["LOW"]), "ℹ️  Info" if summary["severity_breakdown"]["LOW"] > 0 else "🟢 Good")
        table.add_row("Recommendations", str(summary["recommendations_count"]), "📋 Review")
        
        console.print(table)
        
        # Top recommendations
        if self.recommendations:
            console.print("\\n📋 Top Recommendations:", style="bold yellow")
            for i, rec in enumerate(self.recommendations[:5], 1):
                console.print(f"  {i}. {rec['description']} ({rec['priority']} priority)")
        
        # Trust-by-default note
        console.print("\\n" + "=" * 55)
        console.print("🌟 Trust-by-Default Security Model", style="bold cyan")
        console.print("=" * 55)
        
        trust_panel = Panel(
            \"\"\"The Liberation System operates on a trust-by-default model:
            
• Security exists to protect against real threats, not artificial scarcity
• Barriers are minimized to maximize accessibility
• Transparency is prioritized over obscurity
• Systems are designed to be self-healing and fault-tolerant
            
This audit identifies operational security issues while maintaining
the core philosophy of trust and accessibility.\"\"\",
            title="Security Philosophy",
            border_style="cyan"
        )
        
        console.print(trust_panel)
        
        console.print(f"\\n📊 Full report saved to: logs/security_audit_report.json")

def main():
    """Main security audit execution"""
    auditor = SecurityAuditor()
    auditor.run_comprehensive_audit()

if __name__ == "__main__":
    main()
