"""
Dynamic Embedding Configuration System
Automatically detects and manages embedding models across the system.
No hardcoding - future-proof for any embedding model.
"""

import json
import sqlite3
import numpy as np
import logging
from typing import Dict, Optional, Tuple, Any, List
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class EmbeddingModel(Enum):
    """Supported embedding models with their specifications"""
    ADA_002 = ("text-embedding-ada-002", 1536, 0.0001)
    SMALL_3 = ("text-embedding-3-small", 1536, 0.00002)  
    LARGE_3 = ("text-embedding-3-large", 3072, 0.00013)
    
    def __init__(self, model_name: str, dimension: int, cost_per_1k_tokens: float):
        self.model_name = model_name
        self.dimension = dimension
        self.cost_per_1k_tokens = cost_per_1k_tokens


@dataclass
class EmbeddingConfiguration:
    """Configuration for embedding operations"""
    model: EmbeddingModel
    database_path: str
    embedding_columns: Dict[str, str]  # column_name -> purpose
    is_consistent: bool
    detected_automatically: bool
    migration_needed: bool = False
    last_validated: Optional[str] = None


class EmbeddingConfigurationManager:
    """
    Manages embedding configuration across the entire system.
    Automatically detects existing embedding dimensions and ensures consistency.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/embedding_config.json"
        self.config: Optional[EmbeddingConfiguration] = None
        self._load_or_detect_configuration()
    
    def _load_or_detect_configuration(self):
        """Load existing configuration or auto-detect from database"""
        
        # Try to load existing configuration
        if self._load_existing_config():
            logger.info("Loaded existing embedding configuration")
            return
        
        # Auto-detect from database
        logger.info("No existing config found, auto-detecting from database...")
        self._auto_detect_configuration()
    
    def _load_existing_config(self) -> bool:
        """Load configuration from file if it exists"""
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Reconstruct configuration  
            model_name = config_data["model"]["model_name"]
            model = None
            for em in EmbeddingModel:
                if em.model_name == model_name:
                    model = em
                    break
            if not model:
                logger.warning(f"Unknown model {model_name}, using default")
                model = EmbeddingModel.SMALL_3
            
            self.config = EmbeddingConfiguration(
                model=model,
                database_path=config_data["database_path"],
                embedding_columns=config_data["embedding_columns"],
                is_consistent=config_data["is_consistent"],
                detected_automatically=config_data["detected_automatically"],
                migration_needed=config_data.get("migration_needed", False),
                last_validated=config_data.get("last_validated")
            )
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to load existing config: {e}")
            return False
    
    def _auto_detect_configuration(self):
        """Automatically detect embedding configuration from database"""
        
        # Database discovery
        database_paths = [
            "data/quranic_foundation.db",
            "data/quranic_foundations.db", 
            "data/islamic_vectors.db",
            "data/vectors.db"
        ]
        
        detected_config = None
        
        for db_path in database_paths:
            if Path(db_path).exists():
                config = self._analyze_database(db_path)
                if config:
                    detected_config = config
                    break
        
        if not detected_config:
            # Fallback to default configuration
            logger.warning("No suitable database found, using default configuration")
            detected_config = self._create_default_configuration()
        
        self.config = detected_config
        self._save_configuration()
    
    def _analyze_database(self, db_path: str) -> Optional[EmbeddingConfiguration]:
        """Analyze database to determine embedding configuration"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Find tables with embedding columns
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            embedding_info = {}
            detected_dimension = None
            
            for table in tables:
                table_name = table[0]
                
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                embedding_columns = [col[1] for col in columns if 'embedding' in col[1].lower()]
                
                if embedding_columns:
                    # Analyze embedding dimensions
                    for col in embedding_columns:
                        dimension = self._get_embedding_dimension(cursor, table_name, col)
                        if dimension:
                            embedding_info[col] = f"{table_name}.{col}"
                            if not detected_dimension:
                                detected_dimension = dimension
                            elif detected_dimension != dimension:
                                logger.warning(f"Inconsistent embedding dimensions found: {detected_dimension} vs {dimension}")
            
            conn.close()
            
            if not detected_dimension or not embedding_info:
                return None
            
            # Map dimension to model
            model = self._dimension_to_model(detected_dimension)
            
            return EmbeddingConfiguration(
                model=model,
                database_path=db_path,
                embedding_columns=embedding_info,
                is_consistent=True,
                detected_automatically=True,
                last_validated=None
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze database {db_path}: {e}")
            return None
    
    def _get_embedding_dimension(self, cursor, table_name: str, column_name: str) -> Optional[int]:
        """Get the dimension of embeddings in a specific column"""
        try:
            cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL LIMIT 1")
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return None
            
            # Handle BLOB format
            if isinstance(result[0], bytes):
                embedding_array = np.frombuffer(result[0], dtype=np.float32)
                return len(embedding_array)
            
            # Handle JSON format
            if isinstance(result[0], str):
                embedding_list = json.loads(result[0])
                return len(embedding_list)
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not determine dimension for {table_name}.{column_name}: {e}")
            return None
    
    def _dimension_to_model(self, dimension: int) -> EmbeddingModel:
        """Map embedding dimension to appropriate model"""
        if dimension == 1536:
            # Prefer newer model for 1536 dimensions
            return EmbeddingModel.SMALL_3
        elif dimension == 3072:
            return EmbeddingModel.LARGE_3
        else:
            logger.warning(f"Unknown embedding dimension {dimension}, defaulting to text-embedding-3-small")
            return EmbeddingModel.SMALL_3
    
    def _create_default_configuration(self) -> EmbeddingConfiguration:
        """Create default configuration when auto-detection fails"""
        return EmbeddingConfiguration(
            model=EmbeddingModel.SMALL_3,
            database_path="data/quranic_foundation.db",
            embedding_columns={
                "verse_embedding": "quranic_foundations.verse_embedding",
                "principle_embedding": "quranic_foundations.principle_embedding", 
                "application_embedding": "quranic_foundations.application_embedding"
            },
            is_consistent=False,
            detected_automatically=False,
            migration_needed=True
        )
    
    def _save_configuration(self):
        """Save configuration to file"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                "model": {
                    "model_name": self.config.model.model_name,
                    "dimension": self.config.model.dimension,
                    "cost_per_1k_tokens": self.config.model.cost_per_1k_tokens
                },
                "database_path": self.config.database_path,
                "embedding_columns": self.config.embedding_columns,
                "is_consistent": self.config.is_consistent,
                "detected_automatically": self.config.detected_automatically,
                "migration_needed": self.config.migration_needed,
                "last_validated": self.config.last_validated
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved embedding configuration to {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_embedding_model(self) -> EmbeddingModel:
        """Get the configured embedding model"""
        return self.config.model
    
    def get_database_path(self) -> str:
        """Get the configured database path"""
        return self.config.database_path
    
    def get_embedding_columns(self) -> Dict[str, str]:
        """Get the mapping of embedding columns"""
        return self.config.embedding_columns
    
    def is_migration_needed(self) -> bool:
        """Check if database migration is needed"""
        return self.config.migration_needed
    
    def validate_consistency(self) -> Tuple[bool, List[str]]:
        """Validate that all embedding columns have consistent dimensions"""
        issues = []
        
        try:
            conn = sqlite3.connect(self.config.database_path)
            cursor = conn.cursor()
            
            expected_dimension = self.config.model.dimension
            
            for col_name, table_col in self.config.embedding_columns.items():
                table_name, column_name = table_col.split('.')
                dimension = self._get_embedding_dimension(cursor, table_name, column_name)
                
                if dimension != expected_dimension:
                    issues.append(f"{col_name}: expected {expected_dimension}, found {dimension}")
            
            conn.close()
            
            is_consistent = len(issues) == 0
            self.config.is_consistent = is_consistent
            
            return is_consistent, issues
            
        except Exception as e:
            logger.error(f"Failed to validate consistency: {e}")
            return False, [f"Validation failed: {e}"]
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        is_consistent, issues = self.validate_consistency()
        
        return {
            "model_name": self.config.model.model_name,
            "dimension": self.config.model.dimension,
            "cost_per_1k_tokens": self.config.model.cost_per_1k_tokens,
            "database_path": self.config.database_path,
            "embedding_columns": len(self.config.embedding_columns),
            "is_consistent": is_consistent,
            "issues": issues,
            "migration_needed": self.config.migration_needed,
            "detected_automatically": self.config.detected_automatically
        }


# Global configuration manager instance
_config_manager: Optional[EmbeddingConfigurationManager] = None


def get_embedding_config() -> EmbeddingConfigurationManager:
    """Get the global embedding configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = EmbeddingConfigurationManager()
    return _config_manager


def get_embedding_model() -> EmbeddingModel:
    """Get the configured embedding model"""
    return get_embedding_config().get_embedding_model()


# Convenience functions for backward compatibility
def get_embedding_model_name() -> str:
    """Get the embedding model name"""
    return get_embedding_model().model_name


def get_embedding_dimension() -> int:
    """Get the embedding dimension"""
    return get_embedding_model().dimension