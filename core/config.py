# core/config.py

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import logging
from decimal import Decimal

@dataclass
class ResourceConfig:
    """Configuration for resource distribution"""
    total_wealth: Decimal = Decimal('19000000000000.00')  # $19T
    weekly_flow: Decimal = Decimal('800.00')  # $800 per week
    housing_credit: Decimal = Decimal('104000.00')  # $104K housing
    investment_pool: Decimal = Decimal('104000.00')  # $104K investment
    distribution_interval: int = 60  # seconds (for testing)
    production_interval: int = 7 * 24 * 60 * 60  # 1 week in seconds

@dataclass
class TruthConfig:
    """Configuration for truth spreading"""
    spread_interval: int = 30  # seconds
    max_channels: int = 50
    message_priority_levels: int = 5
    effectiveness_threshold: float = 0.7

@dataclass
class MeshConfig:
    """Configuration for mesh network"""
    max_nodes: int = 1000
    discovery_interval: int = 60
    health_check_interval: int = 30
    auto_healing: bool = True
    learning_rate: float = 0.01

@dataclass
class SecurityConfig:
    """Configuration for trust-based security"""
    trust_by_default: bool = True
    verification_required: bool = False
    auth_bypass: bool = True
    log_all_access: bool = True

@dataclass
class DatabaseConfig:
    """Database configuration for production"""
    database_url: str = "postgresql://liberation_user:liberation_password@localhost:5432/liberation_system"
    database_type: str = "postgresql"  # postgresql, sqlite
    pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False  # Set to True for SQL query logging
    
    # Connection retry settings
    retry_attempts: int = 3
    retry_delay: int = 1
    
    # SSL settings for production
    ssl_mode: str = "prefer"  # disable, allow, prefer, require
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    ssl_ca_path: Optional[str] = None

@dataclass
class LoggingConfig:
    """Logging configuration for production"""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = "logs/liberation_system.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    json_format: bool = True
    
    # Structured logging
    include_extra_fields: bool = True
    correlation_id: bool = True
    request_id: bool = True
    
    # External logging services
    elasticsearch_url: Optional[str] = None
    elasticsearch_index: str = "liberation-system"
    
@dataclass
class SecurityConfig:
    """Enhanced security configuration"""
    trust_by_default: bool = True
    verification_required: bool = False
    auth_bypass: bool = True
    log_all_access: bool = True
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # CORS settings
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    cors_methods: List[str] = field(default_factory=lambda: ["*"])
    cors_headers: List[str] = field(default_factory=lambda: ["*"])
    
    # Security headers
    security_headers: bool = True
    
    # API Keys for external services
    api_key_header: str = "X-API-Key"
    admin_api_key: Optional[str] = None
    
@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration"""
    metrics_enabled: bool = True
    metrics_port: int = 9090
    metrics_path: str = "/metrics"
    
    # Health check settings
    health_check_enabled: bool = True
    health_check_path: str = "/health"
    health_check_interval: int = 30
    
    # Performance monitoring
    performance_monitoring: bool = True
    slow_query_threshold: float = 1.0  # seconds
    
    # External monitoring services
    prometheus_enabled: bool = True
    grafana_enabled: bool = False
    
@dataclass
class SystemConfig:
    """Main system configuration"""
    # Core settings
    liberation_mode: str = "development"  # development, production
    trust_level: str = "maximum"
    debug_mode: bool = True
    
    # Data storage
    data_dir: Path = field(default_factory=lambda: Path('data'))
    log_dir: Path = field(default_factory=lambda: Path('logs'))
    
    # Component configs
    resource: ResourceConfig = field(default_factory=ResourceConfig)
    truth: TruthConfig = field(default_factory=TruthConfig)
    mesh: MeshConfig = field(default_factory=MeshConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Ethical principles
    ethical_principles: List[str] = field(default_factory=lambda: [
        "Remove artificial scarcity - we have enough for everyone",
        "Trust by default - security exists only to protect artificial scarcity",
        "Truth over comfort - show reality, not marketing",
        "Direct action - no bureaucracy, no waiting, no bullshit",
        "Transform everything - no half measures, no compromises"
    ])
    
    # Theme configuration (dark neon)
    theme: Dict[str, Any] = field(default_factory=lambda: {
        "primary_color": "#00ffff",  # Cyan
        "secondary_color": "#ff00ff",  # Magenta
        "accent_color": "#ffff00",  # Yellow
        "background": "#000000",  # Black
        "surface": "#1a1a1a",  # Dark gray
        "text": "#ffffff",  # White
        "success": "#00ff00",  # Green
        "warning": "#ff8800",  # Orange
        "error": "#ff0000",  # Red
        "gradient": "linear-gradient(45deg, #00ffff, #ff00ff)"
    })

class ConfigManager:
    """Manage system configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path('config/liberation.json')
        self.config: SystemConfig = SystemConfig()
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> SystemConfig:
        """Load configuration from file or environment"""
        try:
            # First try to load from file
            if self.config_path.exists():
                self.config = self._load_from_file()
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.info("No config file found, using defaults")
            
            # Override with environment variables
            self._load_from_env()
            
            # Ensure directories exist
            self._ensure_directories()
            
            return self.config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.logger.info("Using default configuration")
            return SystemConfig()
    
    def _load_from_file(self) -> SystemConfig:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Convert to SystemConfig object
            config = SystemConfig()
            
            # Update fields from JSON
            for key, value in config_data.items():
                if hasattr(config, key):
                    if key == 'resource':
                        config.resource = ResourceConfig(**value)
                    elif key == 'truth':
                        config.truth = TruthConfig(**value)
                    elif key == 'mesh':
                        config.mesh = MeshConfig(**value)
                    elif key == 'security':
                        config.security = SecurityConfig(**value)
                    else:
                        setattr(config, key, value)
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load config from file: {e}")
            raise
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_mappings = {
            'LIBERATION_MODE': ('liberation_mode', str),
            'TRUST_LEVEL': ('trust_level', str),
            'DEBUG_MODE': ('debug_mode', bool),
            'RESOURCE_POOL': ('resource.total_wealth', Decimal),
            'WEEKLY_FLOW': ('resource.weekly_flow', Decimal),
            'MESH_NETWORK_ENABLED': ('mesh.auto_healing', bool),
            'VERIFICATION_REQUIRED': ('security.verification_required', bool),
            'AUTH_BYPASS': ('security.auth_bypass', bool),
            'TRUST_DEFAULT': ('security.trust_by_default', bool),
        }
        
        for env_var, (config_path, type_func) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    # Handle nested attributes
                    if '.' in config_path:
                        obj_path, attr_name = config_path.split('.')
                        obj = getattr(self.config, obj_path)
                        
                        # Convert value to appropriate type
                        if type_func == bool:
                            value = env_value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            value = type_func(env_value)
                        
                        setattr(obj, attr_name, value)
                    else:
                        if type_func == bool:
                            value = env_value.lower() in ('true', '1', 'yes', 'on')
                        else:
                            value = type_func(env_value)
                        
                        setattr(self.config, config_path, value)
                        
                    self.logger.info(f"Environment override: {env_var} = {env_value}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process environment variable {env_var}: {e}")
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.config.data_dir,
            self.config.log_dir,
            self.config_path.parent
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'liberation_mode': self.config.liberation_mode,
                'trust_level': self.config.trust_level,
                'debug_mode': self.config.debug_mode,
                'resource': {
                    'total_wealth': str(self.config.resource.total_wealth),
                    'weekly_flow': str(self.config.resource.weekly_flow),
                    'housing_credit': str(self.config.resource.housing_credit),
                    'investment_pool': str(self.config.resource.investment_pool),
                    'distribution_interval': self.config.resource.distribution_interval,
                    'production_interval': self.config.resource.production_interval
                },
                'truth': {
                    'spread_interval': self.config.truth.spread_interval,
                    'max_channels': self.config.truth.max_channels,
                    'message_priority_levels': self.config.truth.message_priority_levels,
                    'effectiveness_threshold': self.config.truth.effectiveness_threshold
                },
                'mesh': {
                    'max_nodes': self.config.mesh.max_nodes,
                    'discovery_interval': self.config.mesh.discovery_interval,
                    'health_check_interval': self.config.mesh.health_check_interval,
                    'auto_healing': self.config.mesh.auto_healing,
                    'learning_rate': self.config.mesh.learning_rate
                },
                'security': {
                    'trust_by_default': self.config.security.trust_by_default,
                    'verification_required': self.config.security.verification_required,
                    'auth_bypass': self.config.security.auth_bypass,
                    'log_all_access': self.config.security.log_all_access
                },
                'ethical_principles': self.config.ethical_principles,
                'theme': self.config.theme
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_theme_css(self) -> str:
        """Generate CSS for dark neon theme"""
        theme = self.config.theme
        return f"""
        :root {{
            --primary-color: {theme['primary_color']};
            --secondary-color: {theme['secondary_color']};
            --accent-color: {theme['accent_color']};
            --background: {theme['background']};
            --surface: {theme['surface']};
            --text: {theme['text']};
            --success: {theme['success']};
            --warning: {theme['warning']};
            --error: {theme['error']};
            --gradient: {theme['gradient']};
        }}
        
        body {{
            background-color: var(--background);
            color: var(--text);
            font-family: 'Courier New', monospace;
        }}
        
        .neon-glow {{
            box-shadow: 0 0 10px var(--primary-color);
            border: 1px solid var(--primary-color);
        }}
        
        .gradient-bg {{
            background: var(--gradient);
        }}
        """

# Global configuration instance
config_manager = ConfigManager()
config = config_manager.load_config()

def get_config() -> SystemConfig:
    """Get the current system configuration"""
    return config

def reload_config():
    """Reload configuration from file"""
    global config
    config = config_manager.load_config()
    return config
