"""
Configuration Methods Example for SMA Ennox Library

This example demonstrates all available ways to configure and initialize
the SMASolarClient. Choose the method that best fits your use case.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sma_ennox import SMASolarClient, SMAError


def method_1_env_file():
    """
    Method 1: .env File (RECOMMENDED - Primary Method)

    Best for: Most projects, especially when working with version control

    Setup:
        1. Copy .env.example to .env:
           $ cp .env.example .env

        2. Edit .env with your credentials:
           SMA_USERNAME=your-email@example.com
           SMA_PASSWORD=your-password
           SMA_COMPONENT_ID=your-component-id

        3. The .env file is automatically git-ignored for security

    Advantages:
        - Standard 12-factor app pattern
        - Credentials never committed to Git
        - Easy setup for new developers
        - Works across different environments (dev, staging, production)
        - Automatic loading with python-dotenv
    """
    print("=" * 70)
    print("Method 1: .env File (RECOMMENDED)")
    print("=" * 70)

    try:
        # Automatically loads from .env file in project root
        client = SMASolarClient.from_env()
        print("✓ Client initialized from .env file")
        print(f"  Username: {client.config.username}")
        print(f"  Component ID: {client.config.component_id}")

        # Test the connection
        if client.is_authenticated():
            print("✓ Authentication successful")

        return client

    except SMAError as e:
        print(f"✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure .env file exists in project root")
        print("  2. Copy from template: cp .env.example .env")
        print("  3. Verify all three variables are set:")
        print("     - SMA_USERNAME")
        print("     - SMA_PASSWORD")
        print("     - SMA_COMPONENT_ID")
        return None


def method_2_system_environment():
    """
    Method 2: System Environment Variables

    Best for: CI/CD pipelines, Docker containers, cloud deployments

    Setup:
        # Bash/Linux/macOS
        export SMA_USERNAME="your-email@example.com"
        export SMA_PASSWORD="your-password"
        export SMA_COMPONENT_ID="your-component-id"

        # Windows Command Prompt
        set SMA_USERNAME=your-email@example.com
        set SMA_PASSWORD=your-password
        set SMA_COMPONENT_ID=your-component-id

        # Windows PowerShell
        $env:SMA_USERNAME="your-email@example.com"
        $env:SMA_PASSWORD="your-password"
        $env:SMA_COMPONENT_ID="your-component-id"

    Advantages:
        - Standard for containerized applications
        - Works well with orchestration tools (Kubernetes, Docker Compose)
        - No files needed
        - Easy to inject in CI/CD pipelines
    """
    print("\n" + "=" * 70)
    print("Method 2: System Environment Variables")
    print("=" * 70)

    import os

    # Check if environment variables are set
    has_username = bool(os.getenv('SMA_USERNAME'))
    has_password = bool(os.getenv('SMA_PASSWORD'))
    has_component = bool(os.getenv('SMA_COMPONENT_ID'))

    print(f"Environment variables status:")
    print(f"  SMA_USERNAME: {'✓ Set' if has_username else '✗ Not set'}")
    print(f"  SMA_PASSWORD: {'✓ Set' if has_password else '✗ Not set'}")
    print(f"  SMA_COMPONENT_ID: {'✓ Set' if has_component else '✗ Not set'}")

    if not (has_username and has_password and has_component):
        print("\nNote: Using .env file fallback (from_env() auto-loads .env)")

    try:
        # from_env() will use system environment variables if set,
        # otherwise falls back to .env file
        client = SMASolarClient.from_env()
        print("✓ Client initialized from environment variables")
        return client

    except SMAError as e:
        print(f"✗ Error: {e}")
        return None


def method_3_direct_parameters():
    """
    Method 3: Direct Parameters

    Best for: Testing, scripts, programmatic configuration

    Setup:
        Pass credentials directly when creating the client

    Advantages:
        - Simple and direct
        - Good for testing
        - Useful when credentials come from another source (database, vault, etc.)
        - No files or environment variables needed

    Disadvantages:
        - Credentials in source code (security risk if committed)
        - Less flexible for different environments
    """
    print("\n" + "=" * 70)
    print("Method 3: Direct Parameters")
    print("=" * 70)

    # WARNING: Never hardcode real credentials in source code!
    # This is for demonstration only

    print("Example usage:")
    print("""
    client = SMASolarClient(
        username="your-email@example.com",
        password="your-password",
        component_id="your-component-id"
    )
    """)

    print("WARNING: Do not hardcode credentials in source code!")
    print("         Use this method only for testing or when loading")
    print("         credentials from a secure source programmatically.")

    # Example with credentials from another source
    print("\nBetter approach - load from secure source:")
    print("""
    # Example: Load from AWS Secrets Manager, Azure Key Vault, etc.
    credentials = load_from_secrets_manager('sma-credentials')

    client = SMASolarClient(
        username=credentials['username'],
        password=credentials['password'],
        component_id=credentials['component_id']
    )
    """)

    return None


def method_4_config_json():
    """
    Method 4: JSON Configuration File (DEPRECATED)

    Best for: Legacy applications, backward compatibility

    Setup:
        Create a config.json file:
        {
            "username": "your-email@example.com",
            "password": "your-password",
            "component_id": "your-component-id"
        }

    Advantages:
        - Backward compatible with older versions
        - Simple file format

    Disadvantages:
        - DEPRECATED - use .env instead
        - JSON format less standard for credentials
        - Must be git-ignored manually
    """
    print("\n" + "=" * 70)
    print("Method 4: JSON Configuration File (DEPRECATED)")
    print("=" * 70)

    import os

    config_path = "config.json"

    if os.path.exists(config_path):
        try:
            client = SMASolarClient.from_config_file(config_path)
            print("✓ Client initialized from config.json")
            print("\n⚠ DEPRECATION WARNING:")
            print("  config.json is deprecated. Please migrate to .env file.")
            print("  See .env.example for the new format.")
            return client

        except SMAError as e:
            print(f"✗ Error: {e}")
            return None
    else:
        print(f"✗ config.json not found at: {config_path}")
        print("\n⚠ DEPRECATION NOTICE:")
        print("  config.json is deprecated. Use .env file instead.")
        print("  Run: cp .env.example .env")
        return None


def method_5_dictionary():
    """
    Method 5: Dictionary Configuration

    Best for: Programmatic configuration, testing frameworks

    Setup:
        Create a dictionary with configuration

    Advantages:
        - Flexible for programmatic use
        - Easy to generate dynamically
        - Good for testing with mock data
    """
    print("\n" + "=" * 70)
    print("Method 5: Dictionary Configuration")
    print("=" * 70)

    print("Example usage:")
    print("""
    config = {
        'username': 'your-email@example.com',
        'password': 'your-password',
        'component_id': 'your-component-id'
    }

    client = SMASolarClient(config=config)
    """)

    print("\nUseful for:")
    print("  - Testing with different configurations")
    print("  - Loading config from custom sources")
    print("  - Programmatically generated configurations")

    return None


def comparison_table():
    """Print a comparison table of all configuration methods."""
    print("\n" + "=" * 70)
    print("Configuration Methods Comparison")
    print("=" * 70)
    print("""
┌─────────────────────────┬─────────────┬──────────────┬─────────────┐
│ Method                  │ Best For    │ Git-Safe     │ Status      │
├─────────────────────────┼─────────────┼──────────────┼─────────────┤
│ 1. .env file            │ Most cases  │ Yes (auto)   │ PRIMARY     │
│ 2. System env vars      │ CI/CD       │ Yes          │ Recommended │
│ 3. Direct parameters    │ Testing     │ Depends      │ Supported   │
│ 4. config.json          │ Legacy      │ Yes (manual) │ DEPRECATED  │
│ 5. Dictionary           │ Testing     │ Depends      │ Supported   │
└─────────────────────────┴─────────────┴──────────────┴─────────────┘

Recommendation Order:
  1st choice: .env file (Method 1)
  2nd choice: System environment variables (Method 2)
  3rd choice: Direct parameters from secure source (Method 3)

Avoid:
  - Hardcoding credentials in source code
  - Using config.json for new projects (deprecated)
  - Committing credentials to version control
""")


def main():
    """Demonstrate all configuration methods."""
    print("\nSMA Ennox Library - Configuration Methods Demo\n")

    # Show comparison table first
    comparison_table()

    print("\n" + "=" * 70)
    print("DEMONSTRATIONS")
    print("=" * 70)

    # Method 1: .env file (PRIMARY - will actually work)
    client = method_1_env_file()

    if client:
        # Test fetching data
        print("\nTesting data fetch with .env configuration:")
        try:
            energy = client.get_energy_balance()
            print(f"✓ Successfully fetched energy data")
            print(f"  PV Generation: {energy.get('pvGeneration', 'N/A')} W")
            print(f"  Consumption: {energy.get('totalConsumption', 'N/A')} W")
        except SMAError as e:
            print(f"✗ Error fetching data: {e}")

    # Method 2: System environment variables
    method_2_system_environment()

    # Method 3: Direct parameters (explanation only)
    method_3_direct_parameters()

    # Method 4: config.json (deprecated)
    method_4_config_json()

    # Method 5: Dictionary
    method_5_dictionary()

    # Final recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("""
For most projects:
  1. Copy .env.example to .env
  2. Fill in your credentials
  3. Use: client = SMASolarClient.from_env()

For Docker/CI/CD:
  1. Set environment variables in your deployment
  2. Use: client = SMASolarClient.from_env()

For testing:
  1. Use direct parameters or dictionary config
  2. Load test credentials from secure source

Security best practices:
  - Never commit .env or config.json to Git
  - Use .env.example as a template (committed)
  - Rotate credentials regularly
  - Use least-privilege component IDs
""")


if __name__ == "__main__":
    main()
