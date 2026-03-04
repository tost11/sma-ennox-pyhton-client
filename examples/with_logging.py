"""Example showing how to enable logging for debugging the SMA Ennox library."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

# Option 1: Enable all debug logging (verbose)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Option 2: Only enable sma_ennox logging (uncomment to use)
# logging.getLogger('sma_ennox').setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# ))
# logging.getLogger('sma_ennox').addHandler(handler)

# Option 3: Enable only specific module (uncomment to use)
# logging.getLogger('sma_ennox.auth').setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
# logging.getLogger('sma_ennox.auth').addHandler(handler)

from sma_ennox import SMASolarClient, SMAError


def main():
    print("=" * 70)
    print("SMA Ennox Library - Logging Example")
    print("=" * 70)
    print("\nWatch for log messages showing:")
    print("  - Configuration loading")
    print("  - OAuth2 authentication steps (5 steps)")
    print("  - Token management")
    print("  - API request/response flow")
    print("\n" + "=" * 70 + "\n")

    try:
        # Initialize client - you'll see DEBUG logs showing authentication steps
        print(">>> Initializing client from .env file...\n")
        client = SMASolarClient.from_env()

        print("\n>>> Fetching energy balance...\n")
        # Get energy balance - you'll see DEBUG logs showing HTTP requests
        energy = client.get_energy_balance()

        print("\n" + "=" * 70)
        print("Result:")
        print("=" * 70)
        pv = energy.get('pvGeneration')
        cons = energy.get('totalConsumption')
        print(f"PV Generation: {pv if pv is not None else 'N/A'} W")
        print(f"Total Consumption: {cons if cons is not None else 'N/A'} W")

    except SMAError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
