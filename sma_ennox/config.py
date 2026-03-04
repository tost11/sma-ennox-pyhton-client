"""Configuration management for SMA Ennox library."""

import json
import logging
from typing import Dict
from .exceptions import SMAConfigError

logger = logging.getLogger(__name__)


class Config:
    """Configuration container for SMA API credentials and settings."""

    def __init__(self, username: str, password: str, component_id: str):
        """
        Initialize configuration.

        Args:
            username: SMA account username
            password: SMA account password
            component_id: Plant/component ID

        Raises:
            SMAConfigError: If any required field is missing
        """
        self.username = username
        self.password = password
        self.component_id = component_id
        self.validate()

    @classmethod
    def from_dict(cls, config_dict: Dict[str, str]) -> 'Config':
        """
        Create configuration from dictionary.

        Args:
            config_dict: Dictionary containing configuration keys

        Returns:
            Config instance

        Raises:
            SMAConfigError: If required fields are missing
        """
        logger.debug("Creating configuration from dictionary")
        try:
            config = cls(
                username=config_dict['username'],
                password=config_dict['password'],
                component_id=config_dict['component_id']
            )
            logger.debug("Configuration created successfully")
            return config
        except KeyError as e:
            logger.error(f"Validation failed: {e} is missing")
            raise SMAConfigError(f"Missing required configuration field: {e}")

    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """
        Create configuration from JSON file.

        Args:
            config_path: Path to JSON configuration file

        Returns:
            Config instance

        Raises:
            SMAConfigError: If file not found, invalid JSON, or missing fields
        """
        logger.debug(f"Loading configuration from file: {config_path}")
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            logger.debug("Configuration file loaded successfully")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise SMAConfigError(f"Configuration file '{config_path}' not found")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {config_path}")
            raise SMAConfigError(f"Invalid JSON in configuration file '{config_path}'")

        return cls.from_dict(config_dict)

    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create configuration from environment variables.

        Reads from:
            - SMA_USERNAME
            - SMA_PASSWORD
            - SMA_COMPONENT_ID

        Returns:
            Config instance

        Raises:
            SMAConfigError: If required environment variables are missing

        Example:
            >>> import os
            >>> os.environ['SMA_USERNAME'] = 'user@example.com'
            >>> os.environ['SMA_PASSWORD'] = 'secret'
            >>> os.environ['SMA_COMPONENT_ID'] = '12345'
            >>> client = SMASolarClient.from_env()
        """
        import os

        logger.debug("Loading configuration from environment variables")

        username = os.getenv('SMA_USERNAME')
        password = os.getenv('SMA_PASSWORD')
        component_id = os.getenv('SMA_COMPONENT_ID')

        # Check for missing variables
        missing = []
        if not username:
            missing.append('SMA_USERNAME')
        if not password:
            missing.append('SMA_PASSWORD')
        if not component_id:
            missing.append('SMA_COMPONENT_ID')

        if missing:
            logger.error(f"Missing environment variables: {', '.join(missing)}")
            raise SMAConfigError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        logger.debug("Environment variables loaded successfully")
        return cls(username=username, password=password, component_id=component_id)

    def validate(self) -> None:
        """
        Validate that all required fields are present and non-empty.

        Raises:
            SMAConfigError: If validation fails
        """
        logger.debug("Validating configuration")
        if not self.username:
            logger.error("Validation failed: username is missing")
            raise SMAConfigError("Username is required")
        if not self.password:
            logger.error("Validation failed: password is missing")
            raise SMAConfigError("Password is required")
        if not self.component_id:
            logger.error("Validation failed: component_id is missing")
            raise SMAConfigError("Component ID is required")
        logger.debug("Configuration validation passed")
