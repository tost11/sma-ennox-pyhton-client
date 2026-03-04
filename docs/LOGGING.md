# Logging Guide

The SMA Ennox library uses Python's standard `logging` module. This guide explains how to configure and use logging for debugging and monitoring.

## Table of Contents

- [Quick Start](#quick-start)
- [Log Levels](#log-levels)
- [Controlling Logging](#controlling-logging)
  - [Enable All Logging](#enable-all-logging)
  - [Per-Module Logging](#per-module-logging)
  - [CLI Script Logging](#cli-script-logging)
- [Examples](#examples)

## Quick Start

By default, the library does not output any log messages. To enable logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from sma_ennox import SMASolarClient
client = SMASolarClient.from_env()
```

## Log Levels

The library uses standard Python logging levels:

### DEBUG
Detailed diagnostic information useful for troubleshooting:
- Authentication steps (OAuth2 flow details)
- HTTP requests (method, URL, response codes)
- Token refresh attempts
- PKCE parameter generation

### INFO
General informational messages about successful operations:
- Authentication success
- Data retrieval completion

### WARNING
Unusual conditions that don't prevent operation:
- Token refresh failures (will retry with full login)
- Non-critical API issues

### ERROR
Error conditions that prevent operation:
- Authentication failures
- API errors
- Network errors
- Configuration errors

## Controlling Logging

### Enable All Logging

To see all debug information from the library:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from sma_ennox import SMASolarClient
client = SMASolarClient.from_env()
```

This will show logs from all library modules (auth, client, config).

### Per-Module Logging

Control logging for specific modules by using their logger names:
- `sma_ennox.auth` - Authentication and token management
- `sma_ennox.client` - API requests and responses
- `sma_ennox.config` - Configuration loading

```python
import logging

# Choose the module: 'sma_ennox.auth', 'sma_ennox.client', or 'sma_ennox.config'
logging.getLogger('sma_ennox.auth').setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
logging.getLogger('sma_ennox.auth').addHandler(handler)

from sma_ennox import SMASolarClient
client = SMASolarClient.from_env()
```

### CLI Script Logging

When using the CLI script, use the `--debug` flag:

```bash
# One-shot mode with debug logging
python sma_crawler.py --debug

# Monitoring mode with debug logging
python sma_crawler.py --monitor --interval 60 --debug
```

## Examples

### Debugging Authentication Issues

Enable detailed authentication logging to troubleshoot login problems:

```python
import logging

# Configure logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from sma_ennox import SMASolarClient

try:
    client = SMASolarClient.from_env()
    print("Authentication successful!")
except Exception as e:
    print(f"Authentication failed: {e}")
```

### More Examples

For additional logging configurations including file logging, custom formats, and production setups, see the `examples/` directory in the repository.
