# core/config_manager.py
"""
Centralized configuration management system for the Liberation System.
Handles environment-specific settings, validation, and configuration loading.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class EnvironmentType(Enum):
    """Environment types for configuration management"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    LOCAL = "local"


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 5432
    database: str = "liberation_system"
    username: str = "liberation_user"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    sqlite_fallback: bool = True
    sqlite_path: str = "data/liberation_system.db"


@dataclass
class APIConfig:
    """API configuration settings"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = field(default_factory=lambda: ["*"])
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds


@dataclass
class SystemConfig:
    """Core system configuration"""
    trust_level: str = "maximum"
    verification_required: bool = False
    auth_bypass: bool = True
    resource_pool: int = 19_000_000_000_000  # $19T
    mesh_network_enabled: bool = True
    auto_discovery: bool = True
    sync_interval: int = 1000  # milliseconds
    task_cycle_delay: int = 60  # seconds


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    trust_default: bool = True
    audit_logging: bool = True
    security_headers: bool = True
    max_login_attempts: int = 5
    session_timeout: int = 3600  # seconds
    encryption_enabled: bool = False  # Trust by default


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/liberation_system.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_logging: bool = True


@dataclass
class LiberationSystemConfig:
    """Main configuration class containing all subsystem configurations"""
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigurationManager:
    """
    Centralized configuration management for the Liberation System.
    
    Handles loading configuration from multiple sources:
    1. Environment variables
    2. Configuration files (.env, .json, .yaml)
    3. Default values
    
    Provides validation and environment-specific overrides.
    """
    
    def __init__(self, config_dir: str = "config", env_file: str = ".env"):
        self.config_dir = Path(config_dir)
        self.env_file = env_file
        self.logger = logging.getLogger(__name__)
        self._config: Optional[LiberationSystemConfig] = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self, environment: Optional[str] = None) -> LiberationSystemConfig:
        """
        Load configuration from all sources with proper precedence.
        
        Args:
            environment: Environment name (development, testing, production)
            
        Returns:
            LiberationSystemConfig: Complete system configuration
        """
        # Determine environment
        env_type = self._determine_environment(environment)
        
        # Start with default configuration
        config = LiberationSystemConfig(environment=env_type)
        
        # Load from environment variables
        config = self._load_from_environment_variables(config)
        
        # Load from configuration files
        config = self._load_from_config_files(config, env_type)
        
        # Load from .env file
        config = self._load_from_env_file(config)
        
        # Validate configuration
        self._validate_configuration(config)
        
        # Apply environment-specific overrides
        config = self._apply_environment_overrides(config, env_type)
        
        self._config = config
        self.logger.info(f"Configuration loaded for environment: {env_type.value}")
        
        return config
    
    def get_config(self) -> LiberationSystemConfig:
        """
        Get the current configuration.
        
        Returns:
            LiberationSystemConfig: Current system configuration
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def _determine_environment(self, environment: Optional[str] = None) -> EnvironmentType:
        """Determine the current environment"""
        if environment:
            return EnvironmentType(environment.lower())
        
        # Check environment variable
        env_var = os.getenv("LIBERATION_ENV", "development")
        
        try:
            return EnvironmentType(env_var.lower())
        except ValueError:
            self.logger.warning(f"Unknown environment '{env_var}', defaulting to development")
            return EnvironmentType.DEVELOPMENT
    
    def _load_from_environment_variables(self, config: LiberationSystemConfig) -> LiberationSystemConfig:
        """Load configuration from environment variables"""
        
        # Database configuration
        if os.getenv("DATABASE_HOST"):
            config.database.host = os.getenv("DATABASE_HOST")
        if os.getenv("DATABASE_PORT"):
            config.database.port = int(os.getenv("DATABASE_PORT"))
        if os.getenv("DATABASE_NAME"):
            config.database.database = os.getenv("DATABASE_NAME")
        if os.getenv("DATABASE_USER"):
            config.database.username = os.getenv("DATABASE_USER")
        if os.getenv("DATABASE_PASSWORD"):
            config.database.password = os.getenv("DATABASE_PASSWORD")
        
        # API configuration
        if os.getenv("API_HOST"):
            config.api.host = os.getenv("API_HOST")
        if os.getenv("API_PORT"):
            config.api.port = int(os.getenv("API_PORT"))
        if os.getenv("API_DEBUG"):
            config.api.debug = os.getenv("API_DEBUG").lower() == "true"
        
        # System configuration
        if os.getenv("TRUST_LEVEL"):
            config.system.trust_level = os.getenv("TRUST_LEVEL")
        if os.getenv("VERIFICATION_REQUIRED"):
            config.system.verification_required = os.getenv("VERIFICATION_REQUIRED").lower() == "true"
        if os.getenv("AUTH_BYPASS"):
            config.system.auth_bypass = os.getenv("AUTH_BYPASS").lower() == "true"
        if os.getenv("RESOURCE_POOL"):
            config.system.resource_pool = int(os.getenv("RESOURCE_POOL"))
        if os.getenv("MESH_NETWORK_ENABLED"):
            config.system.mesh_network_enabled = os.getenv("MESH_NETWORK_ENABLED").lower() == "true"
        if os.getenv("AUTO_DISCOVERY"):
            config.system.auto_discovery = os.getenv("AUTO_DISCOVERY").lower() == "true"
        if os.getenv("SYNC_INTERVAL"):
            config.system.sync_interval = int(os.getenv("SYNC_INTERVAL"))
        
        # Security configuration
        if os.getenv("TRUST_DEFAULT"):
            config.security.trust_default = os.getenv("TRUST_DEFAULT").lower() == "true"
        if os.getenv("AUDIT_LOGGING"):
            config.security.audit_logging = os.getenv("AUDIT_LOGGING").lower() == "true"
        if os.getenv("SECURITY_HEADERS"):
            config.security.security_headers = os.getenv("SECURITY_HEADERS").lower() == "true"
        
        # Logging configuration
        if os.getenv("LOG_LEVEL"):
            config.logging.level = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            config.logging.file_path = os.getenv("LOG_FILE")
        
        return config
    
    def _load_from_config_files(self, config: LiberationSystemConfig, env_type: EnvironmentType) -> LiberationSystemConfig:
        """Load configuration from JSON/YAML files"""
        
        # Load base configuration
        base_config_path = self.config_dir / "config.json"
        if base_config_path.exists():
            config = self._merge_json_config(config, base_config_path)
        
        # Load environment-specific configuration
        env_config_path = self.config_dir / f"config.{env_type.value}.json"
        if env_config_path.exists():
            config = self._merge_json_config(config, env_config_path)
        
        return config
    
    def _load_from_env_file(self, config: LiberationSystemConfig) -> LiberationSystemConfig:
        """Load configuration from .env file"""
        env_path = Path(self.env_file)
        
        if not env_path.exists():
            return config
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            
            # Reload from environment variables to pick up .env values
            config = self._load_from_environment_variables(config)
            
        except Exception as e:
            self.logger.warning(f"Failed to load .env file: {e}")
        
        return config
    
    def _merge_json_config(self, config: LiberationSystemConfig, config_path: Path) -> LiberationSystemConfig:
        """Merge JSON configuration file into config object"""
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            
            # Merge configuration sections
            for section, values in file_config.items():
                if hasattr(config, section):
                    section_config = getattr(config, section)
                    for key, value in values.items():
                        if hasattr(section_config, key):
                            setattr(section_config, key, value)
            
        except Exception as e:
            self.logger.warning(f"Failed to load config file {config_path}: {e}")
        
        return config
    
    def _validate_configuration(self, config: LiberationSystemConfig) -> None:
        """Validate configuration settings"""
        
        # Database validation
        if not config.database.host:
            raise ValueError("Database host is required")
        if not (1 <= config.database.port <= 65535):
            raise ValueError("Database port must be between 1 and 65535")
        
        # API validation
        if not (1 <= config.api.port <= 65535):
            raise ValueError("API port must be between 1 and 65535")
        if config.api.max_request_size < 1024:
            raise ValueError("API max_request_size must be at least 1024 bytes")
        
        # System validation
        if config.system.trust_level not in ["minimum", "medium", "maximum"]:
            raise ValueError("Trust level must be 'minimum', 'medium', or 'maximum'")
        if config.system.resource_pool < 0:
            raise ValueError("Resource pool must be non-negative")
        if config.system.sync_interval < 100:
            raise ValueError("Sync interval must be at least 100ms")
        
        # Logging validation
        if config.logging.level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("Log level must be a valid logging level")
        
        self.logger.info("Configuration validation passed")
    
    def _apply_environment_overrides(self, config: LiberationSystemConfig, env_type: EnvironmentType) -> LiberationSystemConfig:
        """Apply environment-specific configuration overrides"""
        
        if env_type == EnvironmentType.DEVELOPMENT:
            # Development-specific settings
            config.api.debug = True
            config.logging.level = "DEBUG"
            config.logging.console_logging = True
            config.database.sqlite_fallback = True
            
        elif env_type == EnvironmentType.TESTING:
            # Testing-specific settings
            config.api.debug = False
            config.logging.level = "INFO"
            config.database.sqlite_fallback = True
            config.database.sqlite_path = "data/test_liberation_system.db"
            
        elif env_type == EnvironmentType.PRODUCTION:
            # Production-specific settings
            config.api.debug = False
            config.logging.level = "WARNING"
            config.logging.console_logging = False
            config.database.sqlite_fallback = False
            config.security.audit_logging = True
            config.security.security_headers = True
            
        return config
    
    def save_config_template(self, output_path: str = "config/config.template.json") -> None:
        """Save a configuration template file"""
        template_config = LiberationSystemConfig()
        
        # Convert to dictionary for JSON serialization
        config_dict = {
            "database": {
                "host": template_config.database.host,
                "port": template_config.database.port,
                "database": template_config.database.database,
                "username": template_config.database.username,
                "password": "YOUR_DATABASE_PASSWORD",
                "pool_size": template_config.database.pool_size,
                "max_overflow": template_config.database.max_overflow,
                "sqlite_fallback": template_config.database.sqlite_fallback,
                "sqlite_path": template_config.database.sqlite_path
            },
            "api": {
                "host": template_config.api.host,
                "port": template_config.api.port,
                "debug": template_config.api.debug,
                "cors_origins": template_config.api.cors_origins,
                "max_request_size": template_config.api.max_request_size,
                "rate_limit_requests": template_config.api.rate_limit_requests,
                "rate_limit_window": template_config.api.rate_limit_window
            },
            "system": {
                "trust_level": template_config.system.trust_level,
                "verification_required": template_config.system.verification_required,
                "auth_bypass": template_config.system.auth_bypass,
                "resource_pool": template_config.system.resource_pool,
                "mesh_network_enabled": template_config.system.mesh_network_enabled,
                "auto_discovery": template_config.system.auto_discovery,
                "sync_interval": template_config.system.sync_interval,
                "task_cycle_delay": template_config.system.task_cycle_delay
            },
            "security": {
                "trust_default": template_config.security.trust_default,
                "audit_logging": template_config.security.audit_logging,
                "security_headers": template_config.security.security_headers,
                "max_login_attempts": template_config.security.max_login_attempts,
                "session_timeout": template_config.security.session_timeout,
                "encryption_enabled": template_config.security.encryption_enabled
            },
            "logging": {
                "level": template_config.logging.level,
                "format": template_config.logging.format,
                "file_path": template_config.logging.file_path,
                "max_file_size": template_config.logging.max_file_size,
                "backup_count": template_config.logging.backup_count,
                "console_logging": template_config.logging.console_logging
            }
        }
        
        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write template file
        with open(output_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        self.logger.info(f"Configuration template saved to {output_path}")


# Global configuration instance
_config_manager = ConfigurationManager()


def get_config() -> LiberationSystemConfig:
    """Get the global configuration instance"""
    return _config_manager.get_config()


def load_config(environment: Optional[str] = None) -> LiberationSystemConfig:
    """Load configuration for a specific environment"""
    return _config_manager.load_config(environment)


def save_config_template(output_path: str = "config/config.template.json") -> None:
    """Save a configuration template file"""
    _config_manager.save_config_template(output_path)


# Example usage
if __name__ == "__main__":
    # Create configuration manager
    config_manager = ConfigurationManager()
    
    # Load configuration
    config = config_manager.load_config()
    
    # Print configuration summary
    print(f"Environment: {config.environment.value}")
    print(f"Database: {config.database.host}:{config.database.port}/{config.database.database}")
    print(f"API: {config.api.host}:{config.api.port}")
    print(f"Trust Level: {config.system.trust_level}")
    print(f"Log Level: {config.logging.level}")
    
    # Save configuration template
    config_manager.save_config_template()
