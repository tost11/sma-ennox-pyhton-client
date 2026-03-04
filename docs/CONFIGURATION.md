# Configuration Guide

This guide covers all available methods to configure the SMA Ennox library, helping you choose the best approach for your use case.

## Table of Contents

- [Overview](#overview)
- [Method 1: .env File (Recommended)](#method-1-env-file-recommended)
- [Method 2: System Environment Variables](#method-2-system-environment-variables)
- [Method 3: Direct Parameters](#method-3-direct-parameters)
- [Method 4: JSON Config File (Deprecated)](#method-4-json-config-file-deprecated)
- [Method 5: Dictionary Configuration](#method-5-dictionary-configuration)
- [Examples](#examples)

## Overview

The SMA Ennox library requires three pieces of information to connect to the SMA Sunny Portal API:

- **Username** - Your SMA Sunny Portal email address
- **Password** - Your SMA Sunny Portal password
- **Component ID** - Your plant/component identifier

The library supports multiple configuration methods to suit different deployment scenarios. The recommended method for most projects is using a `.env` file.

## Method 1: .env File (Recommended)

**Best for:** Most projects, local development, version-controlled codebases

### Setup

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

3. Use the library (automatically loads from `.env`):
```python
from sma_ennox import SMASolarClient

# Automatically loads from .env file in project root
client = SMASolarClient.from_env()
energy = client.get_energy_balance()
```

### File Location

The `.env` file should be placed in your project root directory (same level as your script or where you run Python).


## Method 2: System Environment Variables

Loads parameters from system environment variables.

### Setup

Set environment variables in your system or deployment environment:

**Linux / macOS (bash/zsh):**
```bash
export SMA_USERNAME="your-email@example.com"
export SMA_PASSWORD="your-password"
export SMA_COMPONENT_ID="your-component-id"
```

To make permanent, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export SMA_USERNAME="your-email@example.com"' >> ~/.bashrc
echo 'export SMA_PASSWORD="your-password"' >> ~/.bashrc
echo 'export SMA_COMPONENT_ID="your-component-id"' >> ~/.bashrc
source ~/.bashrc
```

**Windows (Command Prompt):**
```cmd
set SMA_USERNAME=your-email@example.com
set SMA_PASSWORD=your-password
set SMA_COMPONENT_ID=your-component-id
```

To make permanent:
```cmd
setx SMA_USERNAME "your-email@example.com"
setx SMA_PASSWORD "your-password"
setx SMA_COMPONENT_ID "your-component-id"
```

**Windows (PowerShell):**
```powershell
$env:SMA_USERNAME="your-email@example.com"
$env:SMA_PASSWORD="your-password"
$env:SMA_COMPONENT_ID="your-component-id"
```

To make permanent:
```powershell
[Environment]::SetEnvironmentVariable("SMA_USERNAME", "your-email@example.com", "User")
[Environment]::SetEnvironmentVariable("SMA_PASSWORD", "your-password", "User")
[Environment]::SetEnvironmentVariable("SMA_COMPONENT_ID", "your-component-id", "User")
```

### Usage

```python
from sma_ennox import SMASolarClient

# Loads from system environment variables
client = SMASolarClient.from_env()
energy = client.get_energy_balance()
```

### Note on Priority

When using `from_env()`, system environment variables take precedence over `.env` file. This allows you to:
- Use `.env` for local development
- Override with system environment variables in production

## Method 3: Direct Parameters

Loads parameters from directly with given variables.

### Usage

```python
from sma_ennox import SMASolarClient

client = SMASolarClient(
    username="your-email@example.com",
    password="your-password",
    component_id="your-component-id"
)

energy = client.get_energy_balance()
```

## Method 4: JSON Config File (Deprecated)

**Status:** Deprecated - use `.env` file instead

Loads parameters from JSON configuration file.

### JSON Format

```json
{
    "username": "your-email@example.com",
    "password": "your-password",
    "component_id": "your-component-id"
}
```

**Required fields:**
- `username` (string) - Your SMA Sunny Portal email address
- `password` (string) - Your SMA Sunny Portal password
- `component_id` (string) - Your plant/component identifier

### Setup

1. Copy the example file:
```bash
cp config.json.example config.json
```

2. Edit `config.json` with your credentials. The file is already configured in `.gitignore` and will not be committed.

3. Use in code:
```python
from sma_ennox import SMASolarClient

client = SMASolarClient.from_config_file("config.json")
energy = client.get_energy_balance()
```

## Method 5: Dictionary Configuration

Loads parameters from dictionary

### Usage

```python
from sma_ennox import SMASolarClient

config = {
    'username': 'your-email@example.com',
    'password': 'your-password',
    'component_id': 'your-component-id'
}

client = SMASolarClient(config=config)
energy = client.get_energy_balance()
```

### Verifying Configuration

**Verify that configuration is loaded correctly:**

```python
from sma_ennox import SMASolarClient

try:
    client = SMASolarClient.from_env()
    print(f"✓ Configuration loaded")
    print(f"  Username: {client.config.username}")
    print(f"  Component ID: {client.config.component_id}")

    if client.is_authenticated():
        print("✓ Authentication successful")
    else:
        print("✗ Authentication failed")

except Exception as e:
    print(f"✗ Error: {e}")
```

## Examples

For working code examples demonstrating all configuration methods, see:

- **[examples/configuration_methods.py](../examples/configuration_methods.py)** - Comprehensive demonstration of all 5 configuration methods with detailed explanations, comparison table, and best practices

This example script includes:
- Working code for each method
- Detailed explanations and use cases
- Troubleshooting tips
- Security considerations
- Comparison table
- Recommendations for different scenarios

Run it to see all configuration methods in action:
```bash
python examples/configuration_methods.py
```