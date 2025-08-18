"""
Enterprise System Configuration Management
Centralized configuration for all database and system settings
Zero hardcoding, environment-aware, production-ready
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration with validation"""
    civil_db_path: str
    quranic_db_path: str
    islamic_db_path: str
    
    def __post_init__(self):
        """Validate database paths exist"""
        for path_name, path_value in [
            ("civil_db", self.civil_db_path),
            ("quranic_db", self.quranic_db_path),
            ("islamic_db", self.islamic_db_path)
        ]:
            path_obj = Path(path_value)
            if not path_obj.parent.exists():
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created database directory: {path_obj.parent}")


@dataclass
class SystemConfig:
    """Complete system configuration"""
    database: DatabaseConfig
    
    # Performance settings
    max_civil_results: int = 15
    max_quranic_results: int = 10
    parallel_search_enabled: bool = True
    cache_enabled: bool = True
    
    # Integration settings
    quranic_integration_enabled: bool = True
    concept_extraction_enabled: bool = True
    fallback_strategies_enabled: bool = True
    
    # Logging and monitoring
    log_level: str = "INFO"
    performance_tracking_enabled: bool = True
    
    def validate(self) -> bool:
        """Validate system configuration"""
        try:
            # Check database paths
            for path in [
                self.database.civil_db_path,
                self.database.quranic_db_path,
                self.database.islamic_db_path
            ]:
                if not Path(path).parent.exists():
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False


class ConfigManager:
    """Centralized configuration manager"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_config()
    
    def _load_config(self) -> SystemConfig:
        """Load configuration from environment variables with sensible defaults"""
        
        # Get base directory (works in any environment)
        # Since we're running from backend/, we need to go up one level to access data/
        base_dir = os.getenv("ARABIC_LEGAL_AI_BASE_DIR", ".")
        data_dir = os.path.join(base_dir, "data")
        
        # Database paths (environment-aware with defaults)
        civil_db_path = os.getenv("CIVIL_DB_PATH", os.path.join(data_dir, "vectors.db"))
        quranic_db_path = os.getenv("QURANIC_DB_PATH", os.path.join(data_dir, "quranic_foundation.db"))
        islamic_db_path = os.getenv("ISLAMIC_DB_PATH", os.path.join(data_dir, "islamic_vectors.db"))
        
        database_config = DatabaseConfig(
            civil_db_path=civil_db_path,
            quranic_db_path=quranic_db_path,
            islamic_db_path=islamic_db_path
        )
        
        # System settings (environment-aware)
        config = SystemConfig(
            database=database_config,
            max_civil_results=int(os.getenv("MAX_CIVIL_RESULTS", "15")),
            max_quranic_results=int(os.getenv("MAX_QURANIC_RESULTS", "10")),
            parallel_search_enabled=os.getenv("PARALLEL_SEARCH", "true").lower() == "true",
            cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            quranic_integration_enabled=os.getenv("QURANIC_INTEGRATION", "true").lower() == "true",
            concept_extraction_enabled=os.getenv("CONCEPT_EXTRACTION", "true").lower() == "true",
            fallback_strategies_enabled=os.getenv("FALLBACK_STRATEGIES", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            performance_tracking_enabled=os.getenv("PERFORMANCE_TRACKING", "true").lower() == "true"
        )
        
        # Validate configuration
        if not config.validate():
            raise ValueError("Invalid system configuration")
        
        logger.info(f"System configuration loaded successfully")
        logger.info(f"Civil DB: {config.database.civil_db_path}")
        logger.info(f"Quranic DB: {config.database.quranic_db_path}")
        logger.info(f"Islamic DB: {config.database.islamic_db_path}")
        
        return config
    
    @property
    def config(self) -> SystemConfig:
        """Get current system configuration"""
        return self._config
    
    def reload_config(self) -> SystemConfig:
        """Reload configuration (useful for testing)"""
        self._config = self._load_config()
        return self._config
    
    def get_database_paths(self) -> Dict[str, str]:
        """Get all database paths"""
        return {
            "civil": self.config.database.civil_db_path,
            "quranic": self.config.database.quranic_db_path,
            "islamic": self.config.database.islamic_db_path
        }
    
    def is_production_mode(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    def get_performance_settings(self) -> Dict[str, Any]:
        """Get performance-related settings"""
        return {
            "max_civil_results": self.config.max_civil_results,
            "max_quranic_results": self.config.max_quranic_results,
            "parallel_search_enabled": self.config.parallel_search_enabled,
            "cache_enabled": self.config.cache_enabled
        }


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> SystemConfig:
    """Get system configuration (convenience function)"""
    return config_manager.config


def get_database_paths() -> Dict[str, str]:
    """Get database paths (convenience function)"""
    return config_manager.get_database_paths()


def validate_system_health() -> Dict[str, Any]:
    """Validate system health and configuration"""
    config = get_config()
    health_status = {
        "configuration_valid": config.validate(),
        "database_paths_exist": True,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "issues": []
    }
    
    # Check database directories
    for db_name, db_path in get_database_paths().items():
        if not Path(db_path).parent.exists():
            health_status["database_paths_exist"] = False
            health_status["issues"].append(f"{db_name} database directory missing: {db_path}")
        elif not Path(db_path).exists():
            health_status["issues"].append(f"{db_name} database file not found: {db_path}")
    
    return health_status