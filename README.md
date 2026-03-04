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

### Package Installation (Coming Soon)

```bash
pip install sma-ennox
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

The library uses environment variables for configuration, following the 12-factor app methodology.

### Setup (Recommended Method)

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```env
SMA_USERNAME=your-email@example.com
SMA_PASSWORD=your-password
SMA_COMPONENT_ID=your-component-id
```

3. Use the library (automatically loads .env):
```python
from sma_ennox import SMASolarClient

# Automatically loads from .env file
client = SMASolarClient.from_env()
energy = client.get_energy_balance()
```

### Alternative Configuration Methods

**Option 1: System Environment Variables**

```bash
export SMA_USERNAME="your-email@example.com"
export SMA_PASSWORD="your-password"
export SMA_COMPONENT_ID="your-component-id"
```

```python
from sma_ennox import SMASolarClient

# Loads from system environment
client = SMASolarClient.from_env()
```

**Option 2: Direct Parameters (for testing)**

```python
from sma_ennox import SMASolarClient

client = SMASolarClient(
    username="your-email@example.com",
    password="your-password",
    component_id="your-component-id"
)
```

**Option 3: JSON Config File (deprecated, for backward compatibility)**

```python
from sma_ennox import SMASolarClient

# Still supported but deprecated - use .env instead
client = SMASolarClient.from_config_file("config.json")
```

**Security Note:** Never commit `.env` or `config.json` files to Git. The `.env` file is git-ignored automatically.

**For a comprehensive guide** showing all configuration methods with examples, see [`examples/configuration_methods.py`](examples/configuration_methods.py).

## Setting Up for Development

### First Time Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR-USERNAME/sma-ennox.git
cd sma-ennox
```

2. Create virtual environment:
```bash
python -m venv pyenv
source pyenv/bin/activate  # On Windows: pyenv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create local configuration:
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### Important Files

**Git-Ignored (never commit these):**
- `.env` - Your credentials
- `config.json` - (deprecated) Old config format
- `har/` - HTTP Archive files with API tokens

**In Git (safe to commit):**
- `.env.example` - Template for credentials
- Source code (`sma_ennox/*.py`)
- Documentation (README.md, CLAUDE.md)

### Security Notes

**Never commit these files:**
- `.env` or `.env.local` - Contains your credentials
- `config.json` - (deprecated) Contains credentials
- `har/` directory - Contains API tokens and session IDs

**For Contributors:**
- Test with your own credentials, never share them
- Sanitize any HAR files before sharing (replace tokens with "REDACTED")
- Never log sensitive data (passwords, tokens)
- Follow the logging security guidelines in code (see auth.py, client.py)

## API Reference

### Energy Balance

Get current energy flow data including PV generation, consumption, and battery status.

```python
energy = client.get_energy_balance()

# Returns:
{
    "time": "2026-03-04T14:20:00",
    "pvGeneration": 2653.217,              # Current PV generation (W)
    "totalConsumption": 32927.857,          # Total consumption (W)
    "autarkyRate": 0.0806,                  # Self-sufficiency rate (0-1)
    "selfConsumptionRate": 1.0,             # Self-consumption rate (0-1)
    "feedIn": 0.0,                          # Power fed to grid (W)
    "externalConsumption": 30274.64,        # Power from grid (W)
    "directConsumption": 2653.217,          # Direct PV consumption (W)
    "batteryStateOfCharge": None,           # Battery SoC (% or None)
    "batteryCharging": None,                # Battery charging power (W or None)
    "batteryDischarging": None              # Battery discharging power (W or None)
}
```

### CO2 Savings

Get CO2 savings data for today and total.

```python
from datetime import date

# Get today's CO2 savings
co2 = client.get_co2_savings()

# Or specify a date
co2 = client.get_co2_savings(today_date=date(2026, 3, 4))

# Returns:
{
    "today": 12,      # CO2 saved today (kg)
    "total": 15230    # Total CO2 saved (kg)
}
```

### Revenue

Get revenue/earnings data by currency.

```python
from datetime import date

# Get today's revenue
revenue = client.get_revenue()

# Or specify a date
revenue = client.get_revenue(today_date=date(2026, 3, 4))

# Returns:
{
    "today": [
        {"currencyCode3": "EUR", "value": 1.23}
    ],
    "total": [
        {"currencyCode3": "EUR", "value": 911.92}
    ]
}
```

### Device States

Get status information for all devices in the plant.

```python
devices = client.get_device_states()

# Returns list of devices:
[
    {
        "componentType": "Device",
        "componentId": "DEVICE-ID-1",
        "name": "SN: 1234567890",
        "state": 307,
        "additionalStateTag": None,
        "stateFunctionTag": None
    },
    # ... more devices
]
```

### Plant Information

Get detailed plant information including location, peak power, and configuration.

```python
# Get info for configured plant
plant = client.get_plant_info()

# Or specify plant ID
plant = client.get_plant_info(plant_id="12345")

# Returns:
{
    "plantId": "12345",
    "name": "My Solar Plant",
    "peakPower": 9920,                  # Peak power (W)
    "startUpUtc": "2020-01-15T00:00:00Z",
    "city": "Berlin",
    "street": "Main Street 123",
    "zipCode": "10115",
    "longitude": 13.404954,
    "latitude": 52.520008,
    "timezone": "Europe/Berlin",
    "countryName": "Germany",
    "currencyCode3": "EUR",
    "hasSelfConsumption": True,
    # ... more fields
}
```

### Weather Forecast

Get weather forecast for the plant location.

```python
weather = client.get_weather_forecast()

# Or specify component ID and start date
weather = client.get_weather_forecast(
    component_id="12345",
    start_date_utc="2026-03-04T00:00:00Z"
)

# Returns:
{
    "now": {
        "time": "2026-03-04T19:00:00Z",
        "iconId": 0,
        "temperature": 6                # Temperature (°C)
    },
    "tomorrow": {
        "date": "2026-03-04T23:00:00Z",
        "iconId": 0,
        "minTemperature": 1,
        "maxTemperature": 15
    },
    "city": "Berlin"
}
```

### Sensor Data

Get sensor readings for various sensor types.

```python
# Solar irradiation
irradiation = client.get_sensor_data("PlantInsolationSensor")

# Wind speed
wind = client.get_sensor_data("PlantWindVelocitySensor")

# Module temperature
module_temp = client.get_sensor_data("PlantModuleTemperatureSensor")

# Ambient temperature
ambient_temp = client.get_sensor_data("PlantAmbientTemperatureSensor")

# Returns:
{
    "timestampUtc": "2026-03-04T18:00:00Z",
    "value": 542.0,             # Sensor value (units depend on sensor type)
    "channelId": "measurement"
}
```

**Available sensor types:**
- `PlantInsolationSensor` - Solar irradiation (W/m²)
- `PlantWindVelocitySensor` - Wind speed (m/s)
- `PlantModuleTemperatureSensor` - Solar module temperature (°C)
- `PlantAmbientTemperatureSensor` - Ambient temperature (°C)

### Utility Methods

```python
# Check if client is authenticated
is_auth = client.is_authenticated()

# Manually refresh token (usually not needed - handled automatically)
success = client.refresh_token()
```

## Error Handling

The library uses a clear exception hierarchy for different error types:

```python
from sma_ennox import (
    SMASolarClient,
    SMAError,
    SMAAuthenticationError,
    SMAAPIError,
    SMAConfigError,
    SMANetworkError
)

try:
    client = SMASolarClient(
        username="user@example.com",
        password="secret",
        component_id="12345"
    )
    energy = client.get_energy_balance()

except SMAAuthenticationError as e:
    # Authentication failed (invalid credentials or token refresh failed)
    print(f"Authentication error: {e}")

except SMAAPIError as e:
    # API request failed
    print(f"API error (status {e.status_code}): {e}")

except SMAConfigError as e:
    # Configuration is invalid or missing
    print(f"Configuration error: {e}")

except SMANetworkError as e:
    # Network request failed
    print(f"Network error: {e}")

except SMAError as e:
    # Base exception - catches all SMA-related errors
    print(f"SMA error: {e}")
```

### Exception Hierarchy

- `SMAError` - Base exception for all SMA-related errors
  - `SMAAuthenticationError` - Authentication failures (login, token refresh)
  - `SMAAPIError` - API request failures (includes `status_code` and `response_body` attributes)
  - `SMAConfigError` - Configuration issues (missing/invalid config)
  - `SMANetworkError` - Network request failures

## Logging

The library uses Python's standard `logging` module. By default, logging is disabled (no output).

### Enable Logging for Debugging

To see debug information (authentication steps, API requests, etc.):

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from sma_ennox import SMASolarClient
client = SMASolarClient.from_env()
```

### Log Levels

- `DEBUG`: Detailed diagnostic info (authentication steps, HTTP requests, token refresh)
- `INFO`: General informational messages (successful operations)
- `WARNING`: Unusual conditions (token refresh failures, deprecated usage)
- `ERROR`: Error conditions (authentication failed, API errors)

### Control Logging Per Module

```python
import logging

# Only log authentication details
logging.getLogger('sma_ennox.auth').setLevel(logging.DEBUG)

# Only log API client details
logging.getLogger('sma_ennox.client').setLevel(logging.DEBUG)
```

### CLI Script Logging

Use the `--debug` flag to see detailed logs:

```bash
# One-shot mode with debug logging
python sma_crawler.py --debug

# Monitoring mode with debug logging
python sma_crawler.py --monitor --interval 60 --debug
```

## Examples

### Continuous Monitoring

```python
from sma_ennox import SMASolarClient
import time

client = SMASolarClient.from_env()

while True:
    try:
        energy = client.get_energy_balance()
        print(f"[{energy['time']}]")
        print(f"  PV: {energy['pvGeneration']:.1f} W")
        print(f"  Consumption: {energy['totalConsumption']:.1f} W")
        print(f"  Autarky: {energy['autarkyRate']*100:.1f}%")
        print("-" * 50)

        time.sleep(60)  # Update every minute

    except KeyboardInterrupt:
        print("Monitoring stopped")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
```

### Complete System Overview

```python
from sma_ennox import SMASolarClient

client = SMASolarClient.from_env()

# Get plant info
plant = client.get_plant_info()
print(f"Plant: {plant['name']} ({plant['peakPower']/1000:.1f} kWp)")
print(f"Location: {plant['city']}, {plant['countryName']}")

# Get energy data
energy = client.get_energy_balance()
print(f"\nCurrent Generation: {energy['pvGeneration']/1000:.2f} kW")
print(f"Current Consumption: {energy['totalConsumption']/1000:.2f} kW")

# Get environmental impact
co2 = client.get_co2_savings()
print(f"\nCO2 Saved Today: {co2['today']} kg")
print(f"Total CO2 Saved: {co2['total']/1000:.1f} tons")

# Get earnings
revenue = client.get_revenue()
total = revenue['total'][0]
print(f"\nTotal Revenue: {total['value']:.2f} {total['currencyCode3']}")

# Get weather
weather = client.get_weather_forecast()
print(f"\nCurrent Temperature: {weather['now']['temperature']}°C")

# Get sensor data
irradiation = client.get_sensor_data("PlantInsolationSensor")
print(f"Solar Irradiation: {irradiation['value']} W/m²")

# Get device states
devices = client.get_device_states()
print(f"\nDevices: {len(devices)} found")
for device in devices:
    print(f"  - {device['name']}: state {device['state']}")
```

For more examples, see the `examples/` directory:
- `configuration_methods.py` - Comprehensive guide to all configuration options
- `basic_usage.py` - Simple data retrieval
- `monitoring.py` - Continuous monitoring with auto-refresh
- `with_logging.py` - Enable debug logging for troubleshooting

## Authentication

The library uses OAuth2 with PKCE (Proof Key for Code Exchange) for secure authentication. All authentication is handled automatically:

1. On first API call, the library authenticates using your credentials
2. Access tokens are valid for 5 minutes
3. Tokens are automatically refreshed 30 seconds before expiration
4. If token refresh fails, the library re-authenticates automatically

You don't need to manage tokens or understand the authentication flow - just provide your credentials and the library handles the rest.

For detailed information about the authentication flow, see [LOGIN_README.md](LOGIN_README.md).

## Command-Line Interface

A CLI script is available for quick testing:

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
├── har/                    # API endpoint documentation (HAR files)
├── sma_crawler.py          # CLI script
├── .env                    # Your credentials (not in git)
├── .env.example            # Configuration template
├── config.json             # (deprecated) Old config format (not in git)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Running Tests

```bash
# Run unit tests (coming soon)
python -m pytest tests/

# Test authentication
python -c "from sma_ennox import SMASolarClient; client = SMASolarClient.from_env(); print(client.is_authenticated())"

# Test configuration methods
python examples/configuration_methods.py

# Test basic usage
python examples/basic_usage.py
```

### Contributing

Contributions are welcome! Areas for improvement:

- Add unit tests and integration tests
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

## Troubleshooting

### Authentication Errors

**Problem:** `SMAAuthenticationError: Authentication failed`

**Solutions:**
- Verify your username and password are correct
- Check that your SMA Sunny Portal account is active
- Ensure you can log in via the web interface

### API Errors

**Problem:** `SMAAPIError: API request failed (status 401)`

**Solutions:**
- Token may have expired - this should be handled automatically
- Check that your component_id is correct
- Verify your account has access to the component

### Configuration Errors

**Problem:** `SMAConfigError: Missing required field: component_id`

**Solutions:**
- Ensure all required fields are present in your config
- Required fields: `username`, `password`, `component_id`
- Check JSON syntax if using config file

### Network Errors

**Problem:** `SMANetworkError: Connection failed`

**Solutions:**
- Check internet connection
- Verify SMA API endpoints are accessible
- Check firewall settings

## Support

For issues and feature requests, please open an issue on the project repository.

## Acknowledgments

- SMA Solar Technology AG for the Sunny Portal platform
- The Python community for excellent libraries
