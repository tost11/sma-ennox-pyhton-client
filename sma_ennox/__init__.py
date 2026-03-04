"""SMA Ennox Python Library

A Python library for accessing the SMA Sunny Portal / Ennexos API.

Example:
    >>> from sma_ennox import SMASolarClient
    >>> client = SMASolarClient.from_config_file("config.json")
    >>> energy = client.get_energy_balance()
    >>> print(f"PV Generation: {energy['pvGeneration']} W")

Logging:
    This library uses Python's standard logging module. To see debug logs:

    >>> import logging
    >>> logging.basicConfig(level=logging.DEBUG)
"""

import logging

from .client import SMASolarClient
from .exceptions import (
    SMAError,
    SMAAuthenticationError,
    SMAAPIError,
    SMAConfigError,
    SMANetworkError,
)

# Add NullHandler to prevent "No handlers found" warnings
# Users must configure logging in their application to see output
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "0.1.0"
__all__ = [
    "SMASolarClient",
    "SMAError",
    "SMAAuthenticationError",
    "SMAAPIError",
    "SMAConfigError",
    "SMANetworkError",
]
