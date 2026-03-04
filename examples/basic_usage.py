"""Basic usage example for SMA Ennox library."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sma_ennox import SMASolarClient, SMAError


def main():
    try:
        # Initialize client from .env file
        # Automatically loads credentials from .env file in project root
        client = SMASolarClient.from_env()

        # Get energy balance
        energy = client.get_energy_balance()

        # Display results
        print(f"Time: {energy.get('time', 'N/A')}")

        # Handle None values gracefully
        pv_gen = energy.get('pvGeneration')
        print(f"PV Generation: {pv_gen:.1f} W" if pv_gen is not None else "PV Generation: N/A")

        total_cons = energy.get('totalConsumption')
        print(f"Total Consumption: {total_cons:.1f} W" if total_cons is not None else "Total Consumption: N/A")

        autarky = energy.get('autarkyRate')
        print(f"Autarky Rate: {autarky*100:.1f}%" if autarky is not None else "Autarky Rate: N/A")

        feed_in = energy.get('feedIn')
        print(f"Feed-In: {feed_in:.1f} W" if feed_in is not None else "Feed-In: N/A")

        external = energy.get('externalConsumption')
        print(f"External Consumption: {external:.1f} W" if external is not None else "External Consumption: N/A")

        battery_soc = energy.get('batteryStateOfCharge')
        if battery_soc is not None:
            print(f"Battery SoC: {battery_soc:.1f}%")
        else:
            print("Battery SoC: N/A")

    except SMAError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
