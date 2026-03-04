# Error Handling and Troubleshooting

This guide covers exception handling and troubleshooting for the SMA Ennox library.

## Table of Contents

- [Exception Hierarchy](#exception-hierarchy)
- [Using Exceptions](#using-exceptions)
- [Exception Types](#exception-types)
- [Common Issues](#common-issues)
  - [Authentication Errors](#authentication-errors)
  - [API Errors](#api-errors)
  - [Configuration Errors](#configuration-errors)
  - [Network Errors](#network-errors)
- [Debugging Tips](#debugging-tips)

## Exception Hierarchy

The library uses a clear exception hierarchy for different error types:

```
SMAError (base exception)
├── SMAAuthenticationError    - Authentication failures
├── SMAAPIError               - API request failures
├── SMAConfigError            - Configuration issues
└── SMANetworkError           - Network request failures
```

All exceptions inherit from `SMAError`, allowing you to catch all library-related errors with a single exception handler if needed.

## Using Exceptions

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

## Exception Types

### SMAError

Base exception for all SMA-related errors. Catch this to handle any error from the library.

**Usage:**
```python
try:
    client = SMASolarClient.from_env()
    data = client.get_energy_balance()
except SMAError as e:
    print(f"An error occurred: {e}")
```

### SMAAuthenticationError

Raised when authentication fails, including:
- Invalid username or password
- Token refresh failures
- OAuth2 flow errors

**Common causes:**
- Incorrect credentials
- Expired refresh token
- Account locked or deactivated
- SMA authentication service unavailable

### SMAAPIError

Raised when an API request fails. Includes additional attributes:
- `status_code` - HTTP status code
- `response_body` - Response body text

**Common causes:**
- Invalid component ID
- Missing permissions
- API endpoint unavailable
- Rate limiting

**Usage:**
```python
try:
    energy = client.get_energy_balance()
except SMAAPIError as e:
    print(f"API request failed with status {e.status_code}")
    print(f"Response: {e.response_body}")
```

### SMAConfigError

Raised when configuration is invalid or missing.

**Common causes:**
- Missing required fields (username, password, component_id)
- Invalid JSON in config file
- Config file not found
- Invalid environment variable format

### SMANetworkError

Raised when network request fails.

**Common causes:**
- No internet connection
- DNS resolution failure
- Connection timeout
- SSL/TLS errors

## Common Issues

### Authentication Errors

**Problem:** `SMAAuthenticationError: Authentication failed`

**Solutions:**
1. Verify your username and password are correct
2. Check that your SMA Sunny Portal account is active
3. Ensure you can log in via the web interface at https://ennexos.sunnyportal.com
4. Check for any account notifications or required actions in the web portal
5. Wait a few minutes and retry (temporary service issues)

**Problem:** `SMAAuthenticationError: Token refresh failed`

**Solutions:**
1. Re-authenticate (restart your application)
2. Check your internet connection
3. Verify SMA authentication service is accessible

### API Errors

**Problem:** `SMAAPIError: API request failed (status 401)`

**Solutions:**
1. Token may have expired - this should be handled automatically, but you can try restarting
2. Verify your account has access to the requested resource
3. Check if the SMA API service is experiencing issues

**Problem:** `SMAAPIError: API request failed (status 404)`

**Solutions:**
1. Verify your `component_id` is correct
2. Check that the component exists in your SMA account
3. Ensure you have access to the specified plant/component

**Problem:** `SMAAPIError: API request failed (status 403)`

**Solutions:**
1. Check that your account has necessary permissions
2. Verify you're accessing resources you own
3. Check if there are any API access restrictions on your account

### Configuration Errors

**Problem:** `SMAConfigError: Missing required field: component_id`

**Solutions:**
1. Ensure all required fields are present in your config
2. Required fields: `username`, `password`, `component_id`
3. If using `.env` file, check it contains all required variables:
   ```
   SMA_USERNAME=your-email@example.com
   SMA_PASSWORD=your-password
   SMA_COMPONENT_ID=your-component-id
   ```
4. If using config file, check JSON syntax is valid

**Problem:** `SMAConfigError: Config file not found`

**Solutions:**
1. Verify the config file path is correct
2. Check file permissions
3. Use absolute path if relative path isn't working

### Network Errors

**Problem:** `SMANetworkError: Connection failed`

**Solutions:**
1. Check your internet connection
2. Verify SMA API endpoints are accessible:
   - https://login.sma.energy
   - https://uiapi.sunnyportal.com
3. Check firewall settings
4. Check proxy settings if behind corporate firewall
5. Try accessing the SMA web portal to verify service availability

**Problem:** `SMANetworkError: SSL certificate verification failed`

**Solutions:**
1. Update CA certificates on your system
2. Check system time is correct (SSL certificates are time-sensitive)
3. Check if corporate firewall is intercepting SSL connections

## Debugging Tips

### Enable Debug Logging

See detailed information about what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from sma_ennox import SMASolarClient
client = SMASolarClient.from_env()
```

For more information about logging, see [LOGGING.md](LOGGING.md).

### Check Configuration

Verify your configuration is being loaded correctly:

```python
# Check environment variables
import os
print("Username:", os.environ.get('SMA_USERNAME'))
print("Component ID:", os.environ.get('SMA_COMPONENT_ID'))
# Don't print password!

# Verify .env file exists
import os.path
print(".env exists:", os.path.exists('.env'))
```

### Verify Authentication Separately

Verify just the authentication without making API calls:

```python
from sma_ennox import SMASolarClient

client = SMASolarClient.from_env()
print("Authenticated:", client.is_authenticated())
```

### Verify Component ID

Make sure you're using the correct component ID from your SMA account:

1. Log into https://ennexos.sunnyportal.com
2. Navigate to your plant/installation
3. Check the URL or plant settings for the component ID

### Check API Status

If you're experiencing issues, check if the SMA API is working:

1. Visit https://ennexos.sunnyportal.com and verify you can log in
2. Check if data is displayed correctly in the web interface
3. Look for any service announcements or maintenance notifications

### Network Diagnostics

Check network connectivity to SMA services:

```bash
# Check DNS resolution
nslookup login.sma.energy
nslookup uiapi.sunnyportal.com

# Check HTTPS connectivity
curl -I https://login.sma.energy
curl -I https://uiapi.sunnyportal.com
```

### Still Having Issues?

If you're still experiencing problems:

1. Enable debug logging to see detailed information
2. Check the library's GitHub issues for similar problems
3. Open a new issue with:
   - Error message (sanitize any sensitive information)
   - Debug log output (sanitize tokens and passwords)
   - Python version
   - Library version
   - Operating system
