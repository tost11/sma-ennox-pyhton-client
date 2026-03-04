# API Reference

Complete reference for all SMA Ennox library methods.

## Table of Contents

- [Energy Balance](#energy-balance)
- [CO2 Savings](#co2-savings)
- [Revenue](#revenue)
- [Device States](#device-states)
- [Plant Information](#plant-information)
- [Weather Forecast](#weather-forecast)
- [Sensor Data](#sensor-data)
- [Utility Methods](#utility-methods)

## Energy Balance

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

## CO2 Savings

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

## Revenue

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

## Device States

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

## Plant Information

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

## Weather Forecast

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

## Sensor Data

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

## Utility Methods

```python
# Check if client is authenticated
is_auth = client.is_authenticated()

# Manually refresh token (usually not needed - handled automatically)
success = client.refresh_token()
```
