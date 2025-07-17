#!/usr/bin/env python3
"""
📚 Liberation System Documentation Generator
===========================================

Automatically generates comprehensive documentation from code,
API endpoints, and configuration files.
"""

import ast
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import inspect
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel

console = Console()

class DocumentationGenerator:
    """Enterprise documentation generation system"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs" / "auto-generated"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_all_docs(self):
        """Generate all documentation"""
        console.print("📚 Generating Liberation System Documentation", style="bold cyan")
        console.print("=" * 50)
        
        with Progress() as progress:
            task = progress.add_task("Generating docs...", total=6)
            
            # API Documentation
            console.print("📡 Generating API documentation...")
            self.generate_api_docs()
            progress.advance(task)
            
            # Code Documentation
            console.print("💻 Generating code documentation...")
            self.generate_code_docs()
            progress.advance(task)
            
            # Configuration Documentation
            console.print("⚙️  Generating configuration documentation...")
            self.generate_config_docs()
            progress.advance(task)
            
            # Architecture Documentation
            console.print("🏗️  Generating architecture documentation...")
            self.generate_architecture_docs()
            progress.advance(task)
            
            # Deployment Documentation
            console.print("🚀 Generating deployment documentation...")
            self.generate_deployment_docs()
            progress.advance(task)
            
            # Index Documentation
            console.print("📋 Generating index documentation...")
            self.generate_index_docs()
            progress.advance(task)
        
        console.print("✅ Documentation generation complete!", style="bold green")
        console.print(f"📁 Documentation saved to: {self.docs_dir}")
    
    def generate_api_docs(self):
        """Generate API documentation"""
        api_docs = {
            "title": "Liberation System API Reference",
            "version": "1.0.0",
            "description": "Complete API reference for the Liberation System",
            "base_url": "http://localhost:8000",
            "endpoints": self.extract_api_endpoints(),
            "models": self.extract_data_models(),
            "authentication": {
                "type": "Trust-based",
                "description": "Following trust-by-default principles, most endpoints require minimal authentication"
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate markdown
        markdown = self.generate_api_markdown(api_docs)
        
        # Save API docs
        with open(self.docs_dir / "api-reference.md", "w") as f:
            f.write(markdown)
    
    def extract_api_endpoints(self) -> List[Dict]:
        """Extract API endpoints from code"""
        endpoints = []
        
        # Look for FastAPI route definitions
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Parse AST
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for route decorators
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Call):
                                if hasattr(decorator.func, 'attr') and decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                    endpoint = self.extract_endpoint_info(node, decorator)
                                    if endpoint:
                                        endpoints.append(endpoint)
            except Exception as e:
                console.print(f"⚠️  Error parsing {py_file}: {e}")
        
        return endpoints
    
    def extract_endpoint_info(self, func_node: ast.FunctionDef, decorator: ast.Call) -> Optional[Dict]:
        """Extract endpoint information from AST nodes"""
        try:
            # Get HTTP method
            method = decorator.func.attr.upper()
            
            # Get path
            path = "/"
            if decorator.args:
                if isinstance(decorator.args[0], ast.Str):
                    path = decorator.args[0].s
                elif isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value
            
            # Get docstring
            docstring = ast.get_docstring(func_node) or "No description available"
            
            # Get parameters
            parameters = []
            for arg in func_node.args.args:
                if arg.arg not in ['self', 'request']:
                    parameters.append({
                        "name": arg.arg,
                        "type": "string",  # Default type
                        "description": f"Parameter {arg.arg}"
                    })
            
            return {
                "method": method,
                "path": path,
                "function": func_node.name,
                "description": docstring,
                "parameters": parameters
            }
        except Exception:
            return None
    
    def extract_data_models(self) -> List[Dict]:
        """Extract data models from code"""
        models = []
        
        # Look for Pydantic models or dataclasses
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Look for class definitions
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's a data model
                        if any(base.id in ['BaseModel', 'dataclass'] for base in node.bases if isinstance(base, ast.Name)):
                            model = {
                                "name": node.name,
                                "description": ast.get_docstring(node) or f"Data model for {node.name}",
                                "fields": self.extract_model_fields(node)
                            }
                            models.append(model)
            except Exception as e:
                console.print(f"⚠️  Error parsing models in {py_file}: {e}")
        
        return models
    
    def extract_model_fields(self, class_node: ast.ClassDef) -> List[Dict]:
        """Extract fields from data model class"""
        fields = []
        
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                field = {
                    "name": node.target.id,
                    "type": self.get_type_string(node.annotation),
                    "description": f"Field {node.target.id}"
                }
                fields.append(field)
        
        return fields
    
    def get_type_string(self, annotation) -> str:
        """Convert AST annotation to string"""
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Constant):
                return str(annotation.value)
            else:
                return "Any"
        except Exception:
            return "Any"
    
    def generate_api_markdown(self, api_docs: Dict) -> str:
        """Generate API documentation markdown"""
        markdown = f"""# {api_docs['title']}

**Version:** {api_docs['version']}  
**Base URL:** {api_docs['base_url']}  
**Generated:** {api_docs['generated_at']}

## Overview

{api_docs['description']}

## Authentication

**Type:** {api_docs['authentication']['type']}  
**Description:** {api_docs['authentication']['description']}

## Endpoints

"""
        
        # Group endpoints by category
        categories = {}
        for endpoint in api_docs['endpoints']:
            category = endpoint['path'].split('/')[1] if '/' in endpoint['path'] else 'root'
            if category not in categories:
                categories[category] = []
            categories[category].append(endpoint)
        
        for category, endpoints in categories.items():
            markdown += f"### {category.title()}\n\n"
            
            for endpoint in endpoints:
                markdown += f"#### `{endpoint['method']} {endpoint['path']}`\n\n"
                markdown += f"**Description:** {endpoint['description']}\n\n"
                
                if endpoint['parameters']:
                    markdown += "**Parameters:**\n\n"
                    for param in endpoint['parameters']:
                        markdown += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
                    markdown += "\n"
                
                markdown += "---\n\n"
        
        # Add data models
        if api_docs['models']:
            markdown += "## Data Models\n\n"
            
            for model in api_docs['models']:
                markdown += f"### {model['name']}\n\n"
                markdown += f"{model['description']}\n\n"
                
                if model['fields']:
                    markdown += "**Fields:**\n\n"
                    for field in model['fields']:
                        markdown += f"- `{field['name']}` ({field['type']}): {field['description']}\n"
                    markdown += "\n"
                
                markdown += "---\n\n"
        
        return markdown
    
    def generate_code_docs(self):
        """Generate code documentation"""
        code_docs = {
            "title": "Liberation System Code Reference",
            "modules": self.extract_module_docs(),
            "classes": self.extract_class_docs(),
            "functions": self.extract_function_docs(),
            "generated_at": datetime.now().isoformat()
        }
        
        markdown = self.generate_code_markdown(code_docs)
        
        with open(self.docs_dir / "code-reference.md", "w") as f:
            f.write(markdown)
    
    def extract_module_docs(self) -> List[Dict]:
        """Extract module documentation"""
        modules = []
        
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                module_doc = ast.get_docstring(tree)
                
                if module_doc:
                    modules.append({
                        "name": py_file.stem,
                        "path": str(py_file.relative_to(self.project_root)),
                        "description": module_doc
                    })
            except Exception as e:
                console.print(f"⚠️  Error parsing module {py_file}: {e}")
        
        return modules
    
    def extract_class_docs(self) -> List[Dict]:
        """Extract class documentation"""
        classes = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_doc = {
                            "name": node.name,
                            "file": str(py_file.relative_to(self.project_root)),
                            "description": ast.get_docstring(node) or f"Class {node.name}",
                            "methods": []
                        }
                        
                        # Extract methods
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                method_doc = ast.get_docstring(item)
                                class_doc["methods"].append({
                                    "name": item.name,
                                    "description": method_doc or f"Method {item.name}"
                                })
                        
                        classes.append(class_doc)
            except Exception as e:
                console.print(f"⚠️  Error parsing classes in {py_file}: {e}")
        
        return classes
    
    def extract_function_docs(self) -> List[Dict]:
        """Extract function documentation"""
        functions = []
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                        # Skip methods (functions inside classes)
                        if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body):
                            function_doc = {
                                "name": node.name,
                                "file": str(py_file.relative_to(self.project_root)),
                                "description": ast.get_docstring(node) or f"Function {node.name}",
                                "parameters": [arg.arg for arg in node.args.args if arg.arg != 'self']
                            }
                            functions.append(function_doc)
            except Exception as e:
                console.print(f"⚠️  Error parsing functions in {py_file}: {e}")
        
        return functions
    
    def generate_code_markdown(self, code_docs: Dict) -> str:
        """Generate code documentation markdown"""
        markdown = f"""# {code_docs['title']}

**Generated:** {code_docs['generated_at']}

## Modules

"""
        
        for module in code_docs['modules']:
            markdown += f"### {module['name']}\n\n"
            markdown += f"**File:** `{module['path']}`\n\n"
            markdown += f"{module['description']}\n\n"
            markdown += "---\n\n"
        
        markdown += "## Classes\n\n"
        
        for cls in code_docs['classes']:
            markdown += f"### {cls['name']}\n\n"
            markdown += f"**File:** `{cls['file']}`\n\n"
            markdown += f"{cls['description']}\n\n"
            
            if cls['methods']:
                markdown += "**Methods:**\n\n"
                for method in cls['methods']:
                    markdown += f"- `{method['name']}`: {method['description']}\n"
                markdown += "\n"
            
            markdown += "---\n\n"
        
        markdown += "## Functions\n\n"
        
        for func in code_docs['functions']:
            markdown += f"### {func['name']}\n\n"
            markdown += f"**File:** `{func['file']}`\n\n"
            markdown += f"{func['description']}\n\n"
            
            if func['parameters']:
                markdown += f"**Parameters:** {', '.join(func['parameters'])}\n\n"
            
            markdown += "---\n\n"
        
        return markdown
    
    def generate_config_docs(self):
        """Generate configuration documentation"""
        config_files = []
        
        # Find configuration files
        for config_file in self.project_root.rglob("*.json"):
            if "config" in config_file.name.lower() or "settings" in config_file.name.lower():
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    
                    config_files.append({
                        "name": config_file.name,
                        "path": str(config_file.relative_to(self.project_root)),
                        "data": config_data
                    })
                except Exception as e:
                    console.print(f"⚠️  Error parsing config {config_file}: {e}")
        
        # Generate markdown
        markdown = f"""# Configuration Reference

**Generated:** {datetime.now().isoformat()}

## Configuration Files

This document describes all configuration files used by the Liberation System.

"""
        
        for config in config_files:
            markdown += f"### {config['name']}\n\n"
            markdown += f"**Path:** `{config['path']}`\n\n"
            markdown += "**Configuration Options:**\n\n"
            markdown += self.generate_config_table(config['data'])
            markdown += "\n---\n\n"
        
        with open(self.docs_dir / "configuration.md", "w") as f:
            f.write(markdown)
    
    def generate_config_table(self, config_data: Dict, prefix: str = "") -> str:
        """Generate configuration table"""
        table = ""
        
        for key, value in config_data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                table += f"- **{full_key}**: Configuration section\n"
                table += self.generate_config_table(value, full_key)
            else:
                table += f"- **{full_key}**: `{value}` ({type(value).__name__})\n"
        
        return table
    
    def generate_architecture_docs(self):
        """Generate architecture documentation"""
        markdown = f"""# System Architecture

**Generated:** {datetime.now().isoformat()}

## Overview

The Liberation System follows a modular architecture designed for scalability, maintainability, and trust-by-default principles.

## Core Components

### 🎯 Core System
- **automation-system.py**: Main automation engine
- **resource_distribution.py**: Resource allocation system
- **data/**: Data management layer

### 🌐 Interface Layer
- **web/**: React/TypeScript frontend
- **mobile/**: Mobile-responsive web interface (React, not React Native)

### 🔄 Mesh Network
- **Mesh_Network/**: Decentralized communication system
- Auto-discovery and self-healing capabilities

### 🔒 Security Layer
- **trust_default.py**: Minimal security layer
- Anti-security model removing artificial barriers

### 🚀 Transformation Layer
- **truth_spreader.py**: Truth distribution engine
- Marketing channel conversion system

## Data Flow

1. **User Input** → Interface Layer
2. **Interface Layer** → Core System
3. **Core System** → Resource Distribution
4. **Resource Distribution** → Mesh Network
5. **Mesh Network** → Truth Spreading
6. **Truth Spreading** → User Output

## Scalability

The system is designed to handle:
- Theoretical $19T resource distribution
- Millions of concurrent users
- Global mesh network deployment
- Real-time truth propagation

## Security Model

Following the "trust by default" principle:
- Minimal authentication barriers
- Transparent operation
- Self-healing and fault-tolerant design
- No artificial scarcity protection

## Deployment Architecture

The system supports multiple deployment models:
- Single-node development
- Multi-node production
- Docker containerization
- Kubernetes orchestration

"""
        
        with open(self.docs_dir / "architecture.md", "w") as f:
            f.write(markdown)
    
    def generate_deployment_docs(self):
        """Generate deployment documentation"""
        markdown = f"""# Deployment Guide

**Generated:** {datetime.now().isoformat()}

## Quick Start

### Development Environment

```bash
# Clone the repository
git clone https://github.com/tiation-github/liberation-system.git
cd liberation-system

# Install dependencies
pip install -r requirements.txt
npm install

# Run the system
python core/automation-system.py
npm run dev
```

### Production Deployment

#### Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Manual Deployment

```bash
# Build application
python scripts/deploy.py

# Or use the deployment script
./scripts/deploy.py
```

## Configuration

### Environment Variables

```bash
# Core Configuration
export LIBERATION_MODE=production
export TRUST_LEVEL=maximum
export RESOURCE_POOL=19000000000000

# Database Configuration
export DATABASE_URL=postgresql://user:pass@localhost/liberation

# Theme Configuration (Dark Neon)
export THEME_PRIMARY_COLOR="#00ffff"
export THEME_SECONDARY_COLOR="#ff00ff"
```

### Docker Configuration

The system includes comprehensive Docker configuration with:
- PostgreSQL database
- Redis cache
- Prometheus monitoring
- Grafana dashboards
- PgAdmin interface

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# System stats
curl http://localhost:8000/api/v1/stats

# Automation status
curl http://localhost:8000/api/v1/automation/stats
```

### Metrics

Access monitoring dashboards:
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9091
- **PgAdmin**: http://localhost:8080

## Scaling

### Horizontal Scaling

The system supports horizontal scaling through:
- Load balancer configuration
- Database read replicas
- Redis clustering
- Mesh network expansion

### Vertical Scaling

Resource requirements:
- **Minimum**: 2GB RAM, 2 CPU cores
- **Recommended**: 8GB RAM, 4 CPU cores
- **Enterprise**: 32GB RAM, 8 CPU cores

## Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports 3000, 8000, 5432 are available
2. **Database connection**: Verify PostgreSQL is running
3. **Memory issues**: Monitor with `scripts/monitor.py`
4. **Performance**: Use automated optimization features

### Logs

```bash
# Application logs
tail -f logs/liberation.log

# Docker logs
docker-compose logs -f liberation-system

# System metrics
cat logs/metrics.json
```

## Security

### Trust-by-Default Configuration

The system operates with minimal security barriers:
- No complex authentication required
- Transparent operation
- Audit trail for all operations
- Graceful error handling

### Production Security

For production environments:
- Enable HTTPS
- Configure firewall rules
- Set up monitoring alerts
- Regular security audits

"""
        
        with open(self.docs_dir / "deployment.md", "w") as f:
            f.write(markdown)
    
    def generate_index_docs(self):
        """Generate index documentation"""
        markdown = f"""# Liberation System Documentation

**Generated:** {datetime.now().isoformat()}

Welcome to the Liberation System documentation. This documentation is automatically generated from the codebase and provides comprehensive information about the system.

## 🌟 Overview

The Liberation System is a radical transformation framework built on four core principles:

- **🔒 Trust by Default** - Maximum accessibility, minimal barriers
- **🔄 Maximum Automation** - One person can run the entire system
- **💯 Zero Bullshit** - Direct action, no bureaucracy
- **⚡ Complete Transformation** - All-at-once systematic change

## 📚 Documentation Sections

### [API Reference](api-reference.md)
Complete API documentation with endpoints, parameters, and examples.

### [Code Reference](code-reference.md)
Detailed code documentation including modules, classes, and functions.

### [Configuration Guide](configuration.md)
Configuration options and settings for all system components.

### [Architecture Overview](architecture.md)
System architecture, components, and design principles.

### [Deployment Guide](deployment.md)
Step-by-step deployment instructions for development and production.

## 🚀 Quick Links

- **Main Repository**: [tiation-github/liberation-system](https://github.com/tiation-github/liberation-system)
- **Live Demo**: [Liberation System Demo](https://tiation-github.github.io/liberation-system)
- **API Documentation**: [API Docs](http://localhost:8000/docs)
- **System Health**: [Health Check](http://localhost:8000/health)

## 🎯 Key Features

### Resource Distribution
- Automated $19T redistribution system
- $800 weekly flow per person
- $104K community pools
- Zero verification required

### Truth Spreading Network
- Marketing channel hijacking
- Viral information spread
- Media transformation
- Direct communication

### Automation Engine
- Self-organizing mesh network
- Neural learning system
- Autonomous operation
- Perfect synchronization

## 🔧 Development

### Getting Started

```bash
# Clone and setup
git clone https://github.com/tiation-github/liberation-system.git
cd liberation-system
pip install -r requirements.txt
npm install

# Run development server
python core/automation-system.py &
npm run dev
```

### Testing

```bash
# Run comprehensive tests
python scripts/api_test_comprehensive.py

# Run specific test suites
pytest tests/
npm test
```

### Monitoring

```bash
# Start monitoring dashboard
python scripts/monitor.py
```

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](../CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

*"We're not building software. We're creating transformation."*

"""
        
        with open(self.docs_dir / "index.md", "w") as f:
            f.write(markdown)

def main():
    """Main documentation generation"""
    generator = DocumentationGenerator()
    generator.generate_all_docs()

if __name__ == "__main__":
    main()
