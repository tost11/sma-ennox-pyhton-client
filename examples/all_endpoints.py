"""Comprehensive example demonstrating all API endpoints."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sma_ennox import SMASolarClient, SMAError


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def safe_print(label: str, value, unit: str = ""):
    """Print value with None handling."""
    if value is not None:
        if isinstance(value, float):
            print(f"{label}: {value:.2f} {unit}".strip())
        else:
            print(f"{label}: {value} {unit}".strip())
    else:
        print(f"{label}: N/A")


def main():
    try:
        # Initialize client
        print("Initializing SMA Ennox client...")
        client = SMASolarClient.from_env()
        print("Client initialized successfully")

        # 1. Energy Balance
        print_section("Energy Balance")
        energy = client.get_energy_balance()
        print(f"Time: {energy.get('time', 'N/A')}")
        safe_print("  PV Generation", energy.get('pvGeneration'), "W")
        safe_print("  Total Consumption", energy.get('totalConsumption'), "W")
        autarky = energy.get('autarkyRate')
        safe_print("  Autarky Rate", autarky * 100 if autarky is not None else None, "%")
        self_cons = energy.get('selfConsumptionRate')
        safe_print("  Self Consumption Rate", self_cons * 100 if self_cons is not None else None, "%")
        safe_print("  Feed-In", energy.get('feedIn'), "W")
        safe_print("  External Consumption", energy.get('externalConsumption'), "W")
        safe_print("  Direct Consumption", energy.get('directConsumption'), "W")
        safe_print("  Battery SoC", energy.get('batteryStateOfCharge'), "%")
        safe_print("  Battery Charging", energy.get('batteryCharging'), "W")
        safe_print("  Battery Discharging", energy.get('batteryDischarging'), "W")

        # 2. CO2 Savings
        print_section("CO2 Savings")
        co2 = client.get_co2_savings()
        print(f"  Today: {co2['today']} kg")
        print(f"  Total: {co2['total']} kg ({co2['total']/1000:.1f} tons)")

        # 3. Revenue
        print_section("Revenue")
        revenue = client.get_revenue()
        if revenue['today']:
            today_rev = revenue['today'][0]
            print(f"  Today: {today_rev['value']:.2f} {today_rev['currencyCode3']}")
        if revenue['total']:
            total_rev = revenue['total'][0]
            print(f"  Total: {total_rev['value']:.2f} {total_rev['currencyCode3']}")

        # 4. Device States
        print_section("Device States")
        devices = client.get_device_states()
        print(f"  Total Devices: {len(devices)}")
        for device in devices:
            print(f"  - {device['name']}: state {device['state']}")

        # 5. Plant Information
        print_section("Plant Information")
        plant = client.get_plant_info()
        print(f"  Name: {plant['name']}")
        print(f"  Plant ID: {plant['plantId']}")
        print(f"  Peak Power: {plant['peakPower']/1000:.1f} kWp")
        print(f"  Location: {plant['city']}, {plant['countryName']}")
        print(f"  Coordinates: {plant['latitude']:.6f}, {plant['longitude']:.6f}")
        print(f"  Timezone: {plant['timezone']}")
        print(f"  Start Date: {plant['startUpUtc']}")
        print(f"  Currency: {plant['currencyCode3']}")
        print(f"  Self Consumption: {'Yes' if plant['hasSelfConsumption'] else 'No'}")

        # 6. Weather Forecast
        print_section("Weather Forecast")
        weather = client.get_weather_forecast()
        print(f"  City: {weather['city']}")
        print(f"  Current:")
        print(f"    Time: {weather['now']['time']}")
        print(f"    Temperature: {weather['now']['temperature']}°C")
        print(f"    Icon ID: {weather['now']['iconId']}")
        print(f"  Tomorrow:")
        print(f"    Date: {weather['tomorrow']['date']}")
        print(f"    Min Temp: {weather['tomorrow']['minTemperature']}°C")
        print(f"    Max Temp: {weather['tomorrow']['maxTemperature']}°C")
        print(f"    Icon ID: {weather['tomorrow']['iconId']}")

        # 7. Sensor Data
        print_section("Sensor Data")

        # Solar irradiation
        irradiation = client.get_sensor_data("PlantInsolationSensor")
        print(f"  Solar Irradiation:")
        print(f"    Time: {irradiation['timestampUtc']}")
        print(f"    Value: {irradiation['value']} W/m²")

        # Wind speed
        wind = client.get_sensor_data("PlantWindVelocitySensor")
        print(f"  Wind Speed:")
        print(f"    Time: {wind['timestampUtc']}")
        print(f"    Value: {wind['value']} m/s")

        # Module temperature
        module_temp = client.get_sensor_data("PlantModuleTemperatureSensor")
        print(f"  Module Temperature:")
        print(f"    Time: {module_temp['timestampUtc']}")
        print(f"    Value: {module_temp['value']}°C")

        # Ambient temperature
        ambient_temp = client.get_sensor_data("PlantAmbientTemperatureSensor")
        print(f"  Ambient Temperature:")
        print(f"    Time: {ambient_temp['timestampUtc']}")
        print(f"    Value: {ambient_temp['value']}°C")

        print_section("Summary")
        print("All API endpoints retrieved successfully!")

    except SMAError as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
