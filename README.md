# SMA Ennox Python Library

A Python library for accessing the SMA Sunny Portal / Ennexos API to retrieve solar system data. This library provides a clean, intuitive interface for fetching energy balance, CO2 savings, revenue, device states, and more from your SMA solar installation.

## Features

- **Simple API** - Easy-to-use methods for all SMA endpoints
- **Automatic Authentication** - OAuth2/PKCE flow handled transparently
- **Token Management** - Automatic token refresh before expiration
- **Multiple Configuration Options** - Direct parameters, config file, or environment variables
- **Comprehensive Data Access** - Energy balance, CO2 savings, revenue, weather, sensors, and more
- **Error Handling** - Clear exception hierarchy for different error types
- **Type Hints** - Full type annotations for better IDE support

## Installation

### Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd sma-crawler
```

2. Create and activate virtual environment:
```bash
python -m venv pyenv
source pyenv/bin/activate  # On Windows: pyenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

```python
from sma_ennox import SMASolarClient

# Initialize the client
client = SMASolarClient(
    username="your-email@example.com",
    password="your-password",
    component_id="your-component-id"
)

# Get current energy data
energy = client.get_energy_balance()
print(f"PV Generation: {energy['pvGeneration']} W")
print(f"Total Consumption: {energy['totalConsumption']} W")
print(f"Autarky Rate: {energy['autarkyRate']*100:.1f}%")
```

## Configuration

The library uses environment variables for configuration. The recommended method is using a `.env` file:

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```env
SMA_USERNAME=your-email@example.com
SMA_PASSWORD=your-password
SMA_COMPONENT_ID=your-component-id
```

3. Use the library:
```python
from sma_ennox import SMASolarClient

client = SMASolarClient.from_env()
energy = client.get_energy_balance()
```

**For detailed configuration options** (system environment variables, direct parameters, JSON config, Docker/Kubernetes setup, etc.), see **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)**.

**Security:** Never commit `.env` or `config.json` to Git. The `.env` file is automatically git-ignored.

## API Reference

The library provides methods to access all SMA Sunny Portal endpoints:

- **`get_energy_balance()`** - Get current energy flow (PV generation, consumption, battery status)
- **`get_battery()`** - Get dedicated battery data (SoC and power)
- **`get_co2_savings(today_date)`** - Get CO2 savings in kg (today and total)
- **`get_revenue(today_date)`** - Get revenue/earnings by currency
- **`get_device_states()`** - Get status of all devices in the plant
- **`get_plant_info(plant_id)`** - Get plant details (location, peak power, configuration)
- **`get_weather_forecast(component_id, start_date_utc)`** - Get weather forecast for plant location
- **`get_sensor_data(sensor_type)`** - Get sensor readings (irradiation, wind, temperatures)
- **`is_authenticated()`** - Check if client has valid authentication token
- **`refresh_token()`** - Manually refresh the authentication token

For complete API documentation with parameters, return types, response structures, and examples, see **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)**.

**Quick Example:**
```python
from sma_ennox import SMASolarClient

client = SMASolarClient.from_env()
energy = client.get_energy_balance()
print(f"PV: {energy['pvGeneration']} W")
```

## Error Handling

The library uses a clear exception hierarchy:

```python
from sma_ennox import SMASolarClient, SMAError, SMAAuthenticationError

try:
    client = SMASolarClient.from_env()
    energy = client.get_energy_balance()
except SMAAuthenticationError as e:
    print(f"Authentication failed: {e}")
except SMAError as e:
    print(f"Error: {e}")
```

**Exception types:**
- `SMAError` - Base exception for all SMA-related errors
- `SMAAuthenticationError` - Authentication failures
- `SMAAPIError` - API request failures
- `SMAConfigError` - Configuration issues
- `SMANetworkError` - Network request failures

For detailed error handling guide and troubleshooting, see **[docs/ERROR_HANDLING.md](docs/ERROR_HANDLING.md)**.

## Logging

The library uses Python's standard `logging` module. By default, logging is disabled.

**Enable logging for debugging:**

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from sma_ennox import SMASolarClient
client = SMASolarClient.from_env()
```

**CLI script with debug logging:**

```bash
python sma_crawler.py --debug
```

For detailed logging configuration and usage, see **[docs/LOGGING.md](docs/LOGGING.md)**.

## Examples

### Continuous Monitoring

For a complete monitoring implementation with error handling and graceful shutdown, see **[examples/monitoring.py](examples/monitoring.py)**.

**Features:**
- Periodic data updates (configurable interval)
- Signal handling for clean shutdown (Ctrl+C)
- Error recovery and retry logic
- Real-time display of energy metrics

**Run it:**
```bash
python examples/monitoring.py
```

### All Endpoints Demo

For a comprehensive demonstration of all 7 API endpoints, see **[examples/all_endpoints.py](examples/all_endpoints.py)**.

**Demonstrates:**
- Energy balance (PV generation, consumption, autarky)
- CO2 savings (today and total)
- Revenue/earnings
- Device states
- Plant information
- Weather forecast
- All sensor types (irradiation, wind, temperatures)

**Run it:**
```bash
python examples/all_endpoints.py
```

### Example Files

The `examples/` directory contains working examples for common use cases:

- **[basic_usage.py](examples/basic_usage.py)** - Simple one-time data retrieval with proper None-handling
- **[monitoring.py](examples/monitoring.py)** - Continuous monitoring with signal handling and error recovery
- **[all_endpoints.py](examples/all_endpoints.py)** - Comprehensive demonstration of all 7 API endpoints and sensors
- **[configuration_methods.py](examples/configuration_methods.py)** - All 5 configuration methods with comparison table
- **[with_logging.py](examples/with_logging.py)** - Debug logging configuration for troubleshooting

Each example is a complete, runnable script with detailed comments.

## Authentication

The library uses OAuth2 with PKCE (Proof Key for Code Exchange) for secure authentication. All authentication is handled automatically:

1. On first API call, the library authenticates using your credentials
2. Access tokens are valid for 5 minutes
3. Tokens are automatically refreshed 30 seconds before expiration
4. If token refresh fails, the library re-authenticates automatically

You don't need to manage tokens or understand the authentication flow - just provide your credentials and the library handles the rest.

For detailed information about the authentication flow, see **[docs/AUTHENTICATION.md](docs/AUTHENTICATION.md)**.

## Command-Line Interface

A CLI script is available:

```bash
# One-shot mode - fetch data once
python sma_crawler.py

# Monitoring mode - continuous updates
python sma_crawler.py --monitor --interval 60
```

**CLI Options:**
- `--monitor` - Enable continuous monitoring mode
- `--interval SECONDS` - Update interval in seconds (default: 60)
- `--debug` - Enable debug logging

The CLI script uses the same library and reads credentials from `.env` file.

## Development

### Project Structure

```
sma-crawler/
├── sma_ennox/              # Main library package
│   ├── __init__.py         # Public API exports
│   ├── client.py           # SMASolarClient class
│   ├── auth.py             # OAuth2/PKCE authentication
│   ├── config.py           # Configuration handling
│   ├── endpoints.py        # API endpoint definitions
│   └── exceptions.py       # Exception classes
├── examples/               # Example scripts
├── docs/                   # Detailed documentation
├── har/                    # API endpoint documentation (HAR files)
├── sma_crawler.py          # CLI script
├── .env                    # Your credentials (not in git)
├── .env.example            # Configuration template
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Contributing

Areas for improvement:
- Add support for additional endpoints
- Improve error messages and logging
- Add retry logic for transient failures
- Add caching for frequently accessed data
- Create official PyPI package

## Requirements

- Python 3.9 or later
- `requests` - HTTP client library
- `beautifulsoup4` - HTML parsing for authentication
- `python-dotenv` - Environment variable support (optional)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and feature requests, please open an issue on the project repository.

## Acknowledgments

- SMA Solar Technology AG for the Sunny Portal platform
- The Python community for excellent libraries
