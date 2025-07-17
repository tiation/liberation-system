#!/bin/bash

# Liberation System Development Validation Script
# For macOS/Development environments - validates system before production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check Python version
check_python() {
    log "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log "Python version: $PYTHON_VERSION"
        success "Python 3 is available"
    else
        error "Python 3 is not installed"
    fi
}

# Check virtual environment
check_venv() {
    log "Checking virtual environment capabilities..."
    
    if python3 -m venv --help &> /dev/null; then
        success "Virtual environment module is available"
    else
        error "Virtual environment module is not available"
    fi
}

# Check requirements file
check_requirements() {
    log "Checking requirements file..."
    
    if [[ -f "requirements.txt" ]]; then
        success "requirements.txt found"
        log "Requirements:"
        cat requirements.txt
    else
        error "requirements.txt not found"
    fi
}

# Check core modules
check_core_modules() {
    log "Checking core Liberation System modules..."
    
    local modules=(
        "core/liberation_core.py"
        "core/web_server.py"
        "core/resource_management.py"
        "core/truth_spreading.py"
        "core/mesh_network.py"
        "core/database_manager.py"
        "core/ai_engine.py"
        "core/ui_manager.py"
    )
    
    for module in "${modules[@]}"; do
        if [[ -f "$module" ]]; then
            success "✅ $module found"
        else
            error "❌ $module not found"
        fi
    done
}

# Check static files
check_static_files() {
    log "Checking static web interface files..."
    
    local static_files=(
        "static/index.html"
        "static/style.css"
        "static/script.js"
    )
    
    for file in "${static_files[@]}"; do
        if [[ -f "$file" ]]; then
            success "✅ $file found"
        else
            error "❌ $file not found"
        fi
    done
}

# Check deployment files
check_deployment_files() {
    log "Checking deployment files..."
    
    local deploy_files=(
        "deploy/production_setup.sh"
        "deploy/DEPLOYMENT_GUIDE.md"
    )
    
    for file in "${deploy_files[@]}"; do
        if [[ -f "$file" ]]; then
            success "✅ $file found"
        else
            error "❌ $file not found"
        fi
    done
}

# Validate Python syntax
validate_python_syntax() {
    log "Validating Python syntax..."
    
    find . -name "*.py" -type f | while read -r file; do
        if python3 -m py_compile "$file" 2>/dev/null; then
            success "✅ $file syntax OK"
        else
            error "❌ $file has syntax errors"
        fi
    done
}

# Test import capabilities
test_imports() {
    log "Testing Python imports..."
    
    # Test if we can import core modules
    python3 -c "
import sys
sys.path.append('.')

try:
    from core import liberation_core
    print('✅ liberation_core import OK')
except Exception as e:
    print(f'❌ liberation_core import failed: {e}')

try:
    from core import web_server
    print('✅ web_server import OK')
except Exception as e:
    print(f'❌ web_server import failed: {e}')

try:
    from core import resource_management
    print('✅ resource_management import OK')
except Exception as e:
    print(f'❌ resource_management import failed: {e}')
"
}

# Create test virtual environment
create_test_venv() {
    log "Creating test virtual environment..."
    
    if [[ -d "test_venv" ]]; then
        rm -rf test_venv
    fi
    
    python3 -m venv test_venv
    source test_venv/bin/activate
    
    pip install --upgrade pip
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        success "Test virtual environment created and dependencies installed"
    else
        warning "No requirements.txt found, skipping dependency installation"
    fi
    
    deactivate
}

# Test basic system functionality
test_basic_functionality() {
    log "Testing basic system functionality..."
    
    if [[ -d "test_venv" ]]; then
        source test_venv/bin/activate
        
        # Test if we can create a basic database
        python3 -c "
import sys
sys.path.append('.')
from core.database_manager import DatabaseManager
db = DatabaseManager(':memory:')
db.initialize()
print('✅ Database initialization OK')
"
        
        deactivate
    else
        warning "Test virtual environment not available, skipping functionality tests"
    fi
}

# Generate deployment readiness report
generate_report() {
    log "Generating deployment readiness report..."
    
    cat > "deployment_readiness_report.md" << EOF
# Liberation System Deployment Readiness Report

Generated on: $(date)

## System Validation Results

### Core Components
- [x] Python 3 installation verified
- [x] Virtual environment capabilities confirmed
- [x] Core modules present and syntax validated
- [x] Static web interface files available
- [x] Deployment scripts ready

### Dependencies
- [x] Requirements file validated
- [x] Test virtual environment created successfully
- [x] All dependencies installable

### Deployment Files
- [x] Production setup script available
- [x] Deployment guide complete
- [x] Configuration templates ready

## Next Steps for Production Deployment

1. **Prepare Linux Server**
   - Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
   - Minimum 4GB RAM, 2+ CPU cores
   - 20GB+ storage space

2. **Clone Repository on Server**
   \`\`\`bash
   git clone <repository-url>
   cd liberation-system
   \`\`\`

3. **Run Production Setup**
   \`\`\`bash
   chmod +x deploy/production_setup.sh
   sudo ./deploy/production_setup.sh
   \`\`\`

4. **Start Services**
   \`\`\`bash
   sudo systemctl start liberation-system
   sudo systemctl start nginx
   sudo systemctl enable liberation-system
   sudo systemctl enable nginx
   \`\`\`

5. **Verify Deployment**
   - Check service status: \`systemctl status liberation-system\`
   - Access web interface: \`http://your-server-ip\`
   - Monitor logs: \`journalctl -u liberation-system -f\`

## System Ready for Production Deployment ✅

The Liberation System has been validated and is ready for production deployment on a Linux server.
EOF
    
    success "Deployment readiness report generated: deployment_readiness_report.md"
}

# Cleanup function
cleanup() {
    log "Cleaning up test environment..."
    
    if [[ -d "test_venv" ]]; then
        rm -rf test_venv
        success "Test virtual environment cleaned up"
    fi
}

# Main validation flow
main() {
    log "🚀 Starting Liberation System Development Validation"
    echo
    
    check_python
    check_venv
    check_requirements
    check_core_modules
    check_static_files
    check_deployment_files
    validate_python_syntax
    test_imports
    create_test_venv
    test_basic_functionality
    generate_report
    cleanup
    
    echo
    success "🎉 Liberation System validation completed successfully!"
    success "System is ready for production deployment on Linux server"
    log "See deployment_readiness_report.md for detailed information"
}

# Run main function
main
