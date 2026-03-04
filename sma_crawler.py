"""CLI script for SMA Solar data crawler."""

import sys
import json
import argparse
import time
import signal
import logging
from datetime import datetime
from sma_ennox import SMASolarClient, SMAError


# Global flag for monitoring
_running = True

# Configure CLI logging
logger = logging.getLogger(__name__)


def setup_logging(debug=False):
    """Configure logging for CLI."""
    level = logging.DEBUG if debug else logging.WARNING

    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set library logger level
    logging.getLogger('sma_ennox').setLevel(level)

    if debug:
        logger.info("Debug logging enabled")


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global _running
    logger.info("Shutdown signal received")
    print("\nShutdown signal received. Stopping monitoring...")
    _running = False


def print_energy_data(energy_data):
    """Pretty print energy data."""
    logger.debug("Formatting energy data for display")
    print("\n=== SMA Energy Balance Data ===\n")

    # Extract key fields from the response
    fields_to_display = [
        ('time', 'Time'),
        ('pvGeneration', 'PV Generation'),
        ('totalConsumption', 'Total Consumption'),
        ('autarkyRate', 'Autarky Rate'),
        ('selfConsumptionRate', 'Self Consumption Rate'),
        ('feedIn', 'Feed In'),
        ('externalConsumption', 'External Consumption'),
        ('directConsumption', 'Direct Consumption'),
        ('batteryStateOfCharge', 'Battery State of Charge')
    ]

    for field_key, field_label in fields_to_display:
        if field_key in energy_data:
            value = energy_data[field_key]

            # Handle None values
            if value is None:
                print(f"{field_label}: N/A")
            # Format based on field type
            elif field_key in ['autarkyRate', 'selfConsumptionRate']:
                print(f"{field_label}: {value}%")
            elif isinstance(value, (int, float)):
                print(f"{field_label}: {value} W")
            else:
                print(f"{field_label}: {value}")

    print("\n=== Raw JSON Response ===\n")
    print(json.dumps(energy_data, indent=2))


def print_compact_data(energy_data):
    """Print compact format for monitoring."""
    logger.debug("Formatting compact energy data")
    pv = energy_data.get('pvGeneration', 'N/A')
    consumption = energy_data.get('totalConsumption', 'N/A')
    autarky = energy_data.get('autarkyRate', 'N/A')
    self_consumption = energy_data.get('selfConsumptionRate', 'N/A')
    feed_in = energy_data.get('feedIn', 'N/A')
    external = energy_data.get('externalConsumption', 'N/A')
    battery = energy_data.get('batteryStateOfCharge', 'N/A')

    print(f"  PV Generation: {pv} W | Total Consumption: {consumption} W")
    print(f"  Autarky Rate: {autarky}% | Self-Consumption: {self_consumption}%")
    print(f"  Feed-In: {feed_in} W | External: {external} W | Battery: {battery}")
    print("-" * 60)


def start_monitoring(client, interval=60):
    """Start continuous monitoring loop."""
    global _running
    _running = True

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info(f"Starting continuous monitoring with {interval}s interval")
    print("Starting continuous monitoring...")
    update_count = 0
    next_update = time.time()

    while _running:
        current_time = time.time()

        # Check if it's time for the next update
        if current_time >= next_update:
            update_count += 1
            logger.debug(f"Monitoring iteration {update_count}")

            try:
                energy_data = client.get_energy_balance()

                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Update #{update_count}")
                print_compact_data(energy_data)

                # Show token expiry if available
                if hasattr(client, 'auth') and hasattr(client.auth, 'token_expires_at'):
                    token_remaining = int(client.auth.token_expires_at - time.time())
                    print(f"Token expires in: {token_remaining}s")

                # Schedule next update
                next_update = current_time + interval

            except SMAError as e:
                logger.error(f"Error during monitoring: {e}", exc_info=True)
                print(f"Error: {e}")
                # Retry after interval
                next_update = current_time + interval

        # Sleep for 1 second and check again
        if _running:
            remaining = int(next_update - time.time())
            if remaining > 0:
                print(f"\rNext update in {remaining} seconds... (Ctrl+C to stop)", end='', flush=True)
            time.sleep(1)

    logger.info("Monitoring stopped")
    print("\nMonitoring stopped gracefully.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch energy data from SMA Sunny Portal API"
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Enable continuous monitoring mode"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Update interval in seconds for monitoring mode (default: 60)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (shows detailed authentication and API info)"
    )
    args = parser.parse_args()

    # Setup logging based on --debug flag
    setup_logging(debug=args.debug)

    try:
        logger.info("Initializing SMA Solar client")
        # Load credentials from .env file (automatically loads from project root)
        client = SMASolarClient.from_env()

        if args.monitor:
            start_monitoring(client, args.interval)
        else:
            logger.info("Fetching energy balance (one-shot mode)")
            energy = client.get_energy_balance()
            print_energy_data(energy)

    except SMAError as e:
        logger.error(f"Error: {e}", exc_info=args.debug)
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\nInterrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
