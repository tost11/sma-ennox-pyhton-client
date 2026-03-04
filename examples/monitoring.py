"""Continuous monitoring example for SMA Ennox library."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sma_ennox import SMASolarClient, SMAError
import time
import signal
from datetime import datetime


running = True


def signal_handler(signum, frame):
    global running
    print("\nShutdown signal received. Stopping monitoring...")
    running = False


def main():
    global running

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Initialize client from .env file
        # Automatically loads credentials from .env file in project root
        client = SMASolarClient.from_env()
        print("Starting continuous monitoring...")

        update_count = 0
        interval = 60  # seconds
        next_update = time.time()

        while running:
            current_time = time.time()

            # Check if it's time for the next update
            if current_time >= next_update:
                update_count += 1

                try:
                    energy = client.get_energy_balance()

                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Update #{update_count}")

                    # Handle None values gracefully
                    pv = energy.get('pvGeneration')
                    pv_str = f"{pv:.1f} W" if pv is not None else "N/A"

                    cons = energy.get('totalConsumption')
                    cons_str = f"{cons:.1f} W" if cons is not None else "N/A"

                    autarky = energy.get('autarkyRate')
                    autarky_str = f"{autarky*100:.1f}%" if autarky is not None else "N/A"

                    feed_in = energy.get('feedIn')
                    feed_in_str = f"{feed_in:.1f} W" if feed_in is not None else "N/A"

                    print(f"  PV: {pv_str} | Consumption: {cons_str}")
                    print(f"  Autarky: {autarky_str} | Feed-In: {feed_in_str}")
                    print("-" * 60)

                    # Schedule next update
                    next_update = current_time + interval

                except SMAError as e:
                    print(f"Error fetching data: {e}")
                    # Retry after interval
                    next_update = current_time + interval

            # Sleep for 1 second and check again
            if running:
                remaining = int(next_update - time.time())
                if remaining > 0:
                    print(f"\rNext update in {remaining} seconds... (Ctrl+C to stop)", end='', flush=True)
                time.sleep(1)

        print("\nMonitoring stopped gracefully.")

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except SMAError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
