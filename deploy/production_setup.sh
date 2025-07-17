#!/bin/bash

# Liberation System Production Deployment Script
# No Docker/Kubernetes - Direct server deployment

set -e

# Configuration
DEPLOY_USER="liberation"
DEPLOY_DIR="/opt/liberation-system"
SERVICE_NAME="liberation-system"
PYTHON_VERSION="3.9"
VENV_PATH="$DEPLOY_DIR/venv"
LOG_DIR="/var/log/liberation-system"
DATA_DIR="/var/lib/liberation-system"
CONFIG_DIR="/etc/liberation-system"

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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    # Detect OS
    if [[ -f /etc/debian_version ]]; then
        # Debian/Ubuntu
        apt-get update
        apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            python3-dev \
            build-essential \
            nginx \
            supervisor \
            git \
            curl \
            sqlite3 \
            htop \
            certbot \
            python3-certbot-nginx \
            fail2ban \
            ufw
    elif [[ -f /etc/redhat-release ]]; then
        # RHEL/CentOS/Fedora
        yum update -y
        yum install -y \
            python3 \
            python3-pip \
            python3-devel \
            gcc \
            gcc-c++ \
            make \
            nginx \
            supervisor \
            git \
            curl \
            sqlite \
            htop \
            certbot \
            python3-certbot-nginx \
            fail2ban \
            firewalld
    else
        error "Unsupported operating system"
    fi
    
    success "System dependencies installed"
}

# Create system user
create_system_user() {
    log "Creating system user: $DEPLOY_USER"
    
    if ! id "$DEPLOY_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$DEPLOY_DIR" "$DEPLOY_USER"
        success "User $DEPLOY_USER created"
    else
        log "User $DEPLOY_USER already exists"
    fi
}

# Create directories
create_directories() {
    log "Creating directories..."
    
    mkdir -p "$DEPLOY_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$CONFIG_DIR"
    
    # Set ownership
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$LOG_DIR"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DATA_DIR"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$CONFIG_DIR"
    
    success "Directories created and configured"
}

# Setup Python virtual environment
setup_python_environment() {
    log "Setting up Python virtual environment..."
    
    # Create virtual environment
    sudo -u "$DEPLOY_USER" python3 -m venv "$VENV_PATH"
    
    # Upgrade pip
    sudo -u "$DEPLOY_USER" "$VENV_PATH/bin/pip" install --upgrade pip
    
    success "Python virtual environment created"
}

# Deploy application
deploy_application() {
    log "Deploying Liberation System..."
    
    # Copy application files
    cp -r . "$DEPLOY_DIR/app"
    
    # Install Python dependencies
    sudo -u "$DEPLOY_USER" "$VENV_PATH/bin/pip" install -r "$DEPLOY_DIR/app/requirements.txt"
    
    # Set ownership
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR/app"
    
    success "Application deployed"
}

# Create production configuration
create_production_config() {
    log "Creating production configuration..."
    
    cat > "$CONFIG_DIR/production.env" << EOF
# Liberation System Production Configuration
LIBERATION_MODE=production
TRUST_LEVEL=maximum
DEBUG_MODE=false

# Database
DATABASE_PATH=$DATA_DIR/liberation_system.db

# Logging
LOG_LEVEL=INFO
LOG_DIR=$LOG_DIR

# Security
TRUST_DEFAULT=true
VERIFICATION_REQUIRED=false
AUTH_BYPASS=true

# Resources
RESOURCE_POOL=19000000000000
WEEKLY_FLOW=800
DISTRIBUTION_INTERVAL=604800

# Truth Spreading
TRUTH_SPREAD_INTERVAL=1800
MAX_CHANNELS=100

# Mesh Network
MESH_NETWORK_ENABLED=true
AUTO_DISCOVERY=true
MESH_MAX_NODES=1000

# Performance
WORKERS=4
MAX_CONNECTIONS=1000
KEEPALIVE_TIMEOUT=65

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
EOF
    
    chown "$DEPLOY_USER:$DEPLOY_USER" "$CONFIG_DIR/production.env"
    chmod 600 "$CONFIG_DIR/production.env"
    
    success "Production configuration created"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=Liberation System - One person, massive impact
After=network.target

[Service]
Type=simple
User=$DEPLOY_USER
Group=$DEPLOY_USER
WorkingDirectory=$DEPLOY_DIR/app
Environment=PATH=$VENV_PATH/bin
EnvironmentFile=$CONFIG_DIR/production.env
ExecStart=$VENV_PATH/bin/python core/liberation_core.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$DATA_DIR $LOG_DIR $CONFIG_DIR
CapabilityBoundingSet=CAP_NET_BIND_SERVICE

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    success "Systemd service created and enabled"
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    cat > "/etc/nginx/sites-available/$SERVICE_NAME" << EOF
server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Liberation System API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    # Metrics (restrict access)
    location /metrics {
        proxy_pass http://127.0.0.1:9090/metrics;
        allow 127.0.0.1;
        deny all;
    }
    
    # Static files
    location / {
        root $DEPLOY_DIR/app/static;
        try_files \$uri \$uri/ =404;
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOF
    
    # Enable site
    ln -sf "/etc/nginx/sites-available/$SERVICE_NAME" "/etc/nginx/sites-enabled/"
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    nginx -t
    
    success "Nginx configured"
}

# Configure monitoring
configure_monitoring() {
    log "Configuring monitoring..."
    
    # Create monitoring script
    cat > "$DEPLOY_DIR/monitor.sh" << EOF
#!/bin/bash
# Liberation System Monitoring Script

LOG_FILE="$LOG_DIR/monitor.log"
SERVICE_NAME="$SERVICE_NAME"

# Function to log messages
log_message() {
    echo "[\$(date '+%Y-%m-%d %H:%M:%S')] \$1" >> "\$LOG_FILE"
}

# Check service status
check_service() {
    if systemctl is-active --quiet "\$SERVICE_NAME"; then
        log_message "✅ Service is running"
        return 0
    else
        log_message "❌ Service is down - attempting restart"
        systemctl restart "\$SERVICE_NAME"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    DISK_USAGE=\$(df "$DATA_DIR" | awk 'NR==2 {print \$5}' | sed 's/%//')
    if [[ \$DISK_USAGE -gt 80 ]]; then
        log_message "⚠️  High disk usage: \${DISK_USAGE}%"
    fi
}

# Check memory usage
check_memory() {
    MEM_USAGE=\$(free | grep Mem | awk '{printf("%.1f", \$3/\$2 * 100.0)}')
    if [[ \$(echo "\$MEM_USAGE > 80" | bc) -eq 1 ]]; then
        log_message "⚠️  High memory usage: \${MEM_USAGE}%"
    fi
}

# Main monitoring loop
main() {
    log_message "🔍 Running system checks..."
    check_service
    check_disk_space
    check_memory
    log_message "✅ Monitoring check completed"
}

main
EOF
    
    chmod +x "$DEPLOY_DIR/monitor.sh"
    chown "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR/monitor.sh"
    
    # Create cron job for monitoring
    cat > "/etc/cron.d/$SERVICE_NAME-monitor" << EOF
# Liberation System Monitoring
*/5 * * * * root $DEPLOY_DIR/monitor.sh
EOF
    
    success "Monitoring configured"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian
        ufw --force enable
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow ssh
        ufw allow 80/tcp
        ufw allow 443/tcp
    elif command -v firewalld &> /dev/null; then
        # RHEL/CentOS/Fedora
        systemctl enable firewalld
        systemctl start firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
    fi
    
    success "Firewall configured"
}

# Configure log rotation
configure_log_rotation() {
    log "Configuring log rotation..."
    
    cat > "/etc/logrotate.d/$SERVICE_NAME" << EOF
$LOG_DIR/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $DEPLOY_USER $DEPLOY_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF
    
    success "Log rotation configured"
}

# Create deployment scripts
create_deployment_scripts() {
    log "Creating deployment scripts..."
    
    # Start script
    cat > "$DEPLOY_DIR/start.sh" << EOF
#!/bin/bash
systemctl start $SERVICE_NAME
systemctl start nginx
echo "🚀 Liberation System started"
EOF
    
    # Stop script
    cat > "$DEPLOY_DIR/stop.sh" << EOF
#!/bin/bash
systemctl stop $SERVICE_NAME
echo "🛑 Liberation System stopped"
EOF
    
    # Restart script
    cat > "$DEPLOY_DIR/restart.sh" << EOF
#!/bin/bash
systemctl restart $SERVICE_NAME
systemctl reload nginx
echo "🔄 Liberation System restarted"
EOF
    
    # Status script
    cat > "$DEPLOY_DIR/status.sh" << EOF
#!/bin/bash
echo "📊 Liberation System Status:"
echo "=========================="
systemctl status $SERVICE_NAME --no-pager
echo ""
echo "🌐 Nginx Status:"
systemctl status nginx --no-pager
echo ""
echo "💾 Disk Usage:"
df -h "$DATA_DIR"
echo ""
echo "🧠 Memory Usage:"
free -h
echo ""
echo "📈 Recent Logs:"
journalctl -u $SERVICE_NAME -n 10 --no-pager
EOF
    
    # Update script
    cat > "$DEPLOY_DIR/update.sh" << EOF
#!/bin/bash
echo "🔄 Updating Liberation System..."
systemctl stop $SERVICE_NAME
cd "$DEPLOY_DIR/app"
git pull origin main
$VENV_PATH/bin/pip install -r requirements.txt
systemctl start $SERVICE_NAME
echo "✅ Liberation System updated"
EOF
    
    chmod +x "$DEPLOY_DIR"/*.sh
    
    success "Deployment scripts created"
}

# Main deployment function
main() {
    log "Starting Liberation System Production Deployment"
    log "=============================================="
    
    check_root
    install_system_dependencies
    create_system_user
    create_directories
    setup_python_environment
    deploy_application
    create_production_config
    create_systemd_service
    configure_nginx
    configure_monitoring
    configure_firewall
    configure_log_rotation
    create_deployment_scripts
    
    success "Liberation System deployed successfully!"
    
    echo ""
    echo "🌟 Liberation System Production Deployment Complete!"
    echo "===================================================="
    echo ""
    echo "📁 Installation Directory: $DEPLOY_DIR"
    echo "📊 Data Directory: $DATA_DIR"
    echo "📝 Log Directory: $LOG_DIR"
    echo "⚙️  Configuration: $CONFIG_DIR"
    echo ""
    echo "🚀 To start the system:"
    echo "   systemctl start $SERVICE_NAME"
    echo "   systemctl start nginx"
    echo ""
    echo "📈 Monitor the system:"
    echo "   journalctl -u $SERVICE_NAME -f"
    echo "   tail -f $LOG_DIR/liberation_system.log"
    echo ""
    echo "🔧 Management scripts:"
    echo "   $DEPLOY_DIR/start.sh"
    echo "   $DEPLOY_DIR/stop.sh"
    echo "   $DEPLOY_DIR/restart.sh"
    echo "   $DEPLOY_DIR/status.sh"
    echo "   $DEPLOY_DIR/update.sh"
    echo ""
    echo "🌍 Access the system at: http://your-server-ip"
    echo ""
    echo "Trust by default. Maximum automation. Zero bullshit."
    echo "One person, massive impact. Liberation is live."
}

# Run main function
main "$@"
