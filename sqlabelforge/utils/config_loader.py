"""Configuration loader for SQLabelForge."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Load and manage configuration from YAML files and environment variables.

    Features:
    - Load from multiple config files
    - Environment variable override
    - Secure credential management
    - Query template management
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        env_path: Optional[str] = None,
    ):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to main config YAML file
            env_path: Path to .env file
        """
        self.config_path = config_path or self._find_config_file()
        self.env_path = env_path or self._find_env_file()

        # Load environment variables
        if self.env_path and os.path.exists(self.env_path):
            load_dotenv(self.env_path)
            logger.info(f"Loaded environment from {self.env_path}")

        self.config: Dict[str, Any] = {}
        self.queries: Dict[str, str] = {}

    def _find_config_file(self) -> str:
        """Find config.yaml in standard locations."""
        search_paths = [
            "config/config.yaml",
            "config.yaml",
            "../config/config.yaml",
        ]

        for path in search_paths:
            if os.path.exists(path):
                logger.info(f"Found config file at {path}")
                return path

        logger.warning("No config file found, using defaults")
        return "config/config.yaml"

    def _find_env_file(self) -> str:
        """Find .env file in standard locations."""
        search_paths = [
            ".env",
            "../.env",
        ]

        for path in search_paths:
            if os.path.exists(path):
                logger.info(f"Found .env file at {path}")
                return path

        logger.warning("No .env file found")
        return ".env"

    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Optional path to config file

        Returns:
            Configuration dictionary
        """
        path = config_path or self.config_path

        if not os.path.exists(path):
            logger.warning(f"Config file not found: {path}, using defaults")
            return self._get_default_config()

        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)

            # Override with environment variables
            config = self._apply_env_overrides(config)

            self.config = config
            logger.info(f"Configuration loaded from {path}")
            return config

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "database": {
                "server": os.getenv("SQL_SERVER", "localhost"),
                "database": os.getenv("SQL_DATABASE", "master"),
                "username": os.getenv("SQL_USERNAME"),
                "password": os.getenv("SQL_PASSWORD"),
                "trusted_connection": os.getenv("SQL_TRUSTED_CONNECTION", "false").lower() == "true",
            },
            "processor": {
                "use_gpu": os.getenv("USE_GPU", "false").lower() == "true",
                "chunk_size": int(os.getenv("CHUNK_SIZE", "10000")),
            },
            "labeling": {
                "default_strategy": os.getenv("LABELING_STRATEGY", "manual"),
            },
        }

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to config.

        Args:
            config: Base configuration

        Returns:
            Configuration with environment overrides
        """
        # Database overrides
        if "database" in config:
            config["database"]["server"] = os.getenv(
                "SQL_SERVER", config["database"].get("server")
            )
            config["database"]["database"] = os.getenv(
                "SQL_DATABASE", config["database"].get("database")
            )
            config["database"]["username"] = os.getenv(
                "SQL_USERNAME", config["database"].get("username")
            )
            config["database"]["password"] = os.getenv(
                "SQL_PASSWORD", config["database"].get("password")
            )

        # Processor overrides
        if "processor" in config:
            if os.getenv("USE_GPU"):
                config["processor"]["use_gpu"] = os.getenv("USE_GPU").lower() == "true"

            if os.getenv("CHUNK_SIZE"):
                config["processor"]["chunk_size"] = int(os.getenv("CHUNK_SIZE"))

        return config

    def load_queries(self, queries_path: Optional[str] = None) -> Dict[str, str]:
        """
        Load SQL queries from YAML file.

        Args:
            queries_path: Path to queries YAML file

        Returns:
            Dictionary mapping query names to SQL strings
        """
        if queries_path is None:
            # Try to find queries file
            search_paths = [
                "config/queries.yaml",
                "queries.yaml",
                "../config/queries.yaml",
            ]

            queries_path = None
            for path in search_paths:
                if os.path.exists(path):
                    queries_path = path
                    break

            if not queries_path:
                logger.warning("No queries file found")
                return {}

        try:
            with open(queries_path, 'r') as f:
                queries = yaml.safe_load(f)

            self.queries = queries.get("queries", {})
            logger.info(f"Loaded {len(self.queries)} queries from {queries_path}")
            return self.queries

        except Exception as e:
            logger.error(f"Failed to load queries: {e}")
            return {}

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        if not self.config:
            self.load_config()
        return self.config

    def get_queries(self) -> Dict[str, str]:
        """Get loaded queries."""
        if not self.queries:
            self.load_queries()
        return self.queries

    def get_query(self, name: str) -> Optional[str]:
        """
        Get a specific query by name.

        Args:
            name: Query name

        Returns:
            SQL query string or None if not found
        """
        if not self.queries:
            self.load_queries()

        return self.queries.get(name)

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate configuration and return validation results.

        Returns:
            Dictionary with validation results
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        config = self.get_config()

        # Check database config
        db_config = config.get("database", {})
        if not db_config.get("server"):
            validation["errors"].append("Database server not configured")
            validation["valid"] = False

        if not db_config.get("database"):
            validation["errors"].append("Database name not configured")
            validation["valid"] = False

        if not db_config.get("trusted_connection"):
            if not db_config.get("username"):
                validation["warnings"].append("Database username not configured")

            if not db_config.get("password"):
                validation["warnings"].append("Database password not configured")

        return validation
