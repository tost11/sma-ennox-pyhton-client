"""Main client class for SMA Ennox library."""

from typing import Dict, Any, Optional
import logging
import requests

from .config import Config
from .auth import OAuth2Handler
from . import endpoints
from .exceptions import SMAAuthenticationError, SMAAPIError, SMAConfigError, SMANetworkError

logger = logging.getLogger(__name__)


class SMASolarClient:
    """
    Client for accessing SMA Sunny Portal / Ennexos API.

    This client handles authentication and provides methods to fetch data
    from various API endpoints.

    Example:
        >>> client = SMASolarClient.from_config_file("config.json")
        >>> energy = client.get_energy_balance()
        >>> print(f"PV Generation: {energy['pvGeneration']} W")
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        component_id: Optional[str] = None,
        config: Optional[Dict[str, str]] = None
    ):
        """
        Initialize SMA Solar client.

        Provide either individual parameters OR config dict, not both.

        Args:
            username: SMA account username
            password: SMA account password
            component_id: Plant/component ID
            config: Dictionary containing username, password, and component_id

        Raises:
            SMAConfigError: If configuration is invalid or missing required fields
        """
        logger.debug("Initializing SMASolarClient")

        # Handle configuration
        if config is not None:
            logger.debug("Configuration source: dictionary")
            self.config = Config.from_dict(config)
        elif username and password and component_id:
            logger.debug("Configuration source: parameters")
            self.config = Config(username, password, component_id)
        else:
            logger.error("Initialization failed: missing required configuration")
            raise SMAConfigError(
                "Must provide either (username, password, component_id) or config dict"
            )

        logger.debug(f"Component ID: {self.config.component_id}")

        # Initialize session and auth handler
        self.session = requests.Session()
        self.auth = OAuth2Handler(
            username=self.config.username,
            password=self.config.password,
            session=self.session
        )

        logger.info("SMASolarClient initialized successfully")

    @classmethod
    def from_config_file(cls, config_path: str = "config.json") -> 'SMASolarClient':
        """
        Create client from JSON configuration file.

        Args:
            config_path: Path to JSON config file (default: "config.json")

        Returns:
            SMASolarClient instance

        Raises:
            SMAConfigError: If file not found or invalid

        Example:
            >>> client = SMASolarClient.from_config_file("config.json")
        """
        logger.debug(f"Loading configuration from file: {config_path}")
        config = Config.from_file(config_path)
        logger.debug("Configuration loaded successfully")
        return cls(
            username=config.username,
            password=config.password,
            component_id=config.component_id
        )

    @classmethod
    def from_env(cls, load_dotenv: bool = True) -> 'SMASolarClient':
        """
        Create client from environment variables.

        Automatically loads .env file if present (unless load_dotenv=False).

        Reads configuration from:
            - SMA_USERNAME
            - SMA_PASSWORD
            - SMA_COMPONENT_ID

        Args:
            load_dotenv: If True (default), attempts to load .env file

        Returns:
            SMASolarClient instance

        Raises:
            SMAConfigError: If required environment variables are missing

        Example:
            >>> # Loads .env file automatically if present
            >>> client = SMASolarClient.from_env()

            >>> # Skip .env file loading (use OS environment only)
            >>> client = SMASolarClient.from_env(load_dotenv=False)
        """
        logger.debug("Creating client from environment variables")

        if load_dotenv:
            try:
                from dotenv import load_dotenv as load_env_file
                logger.debug("Attempting to load .env file")
                # load_dotenv() returns True if .env was loaded, False if not found
                if load_env_file():
                    logger.debug(".env file loaded successfully")
                else:
                    logger.debug(".env file not found, using existing environment")
            except ImportError:
                logger.warning("python-dotenv not installed, skipping .env file loading")

        config = Config.from_env()
        return cls(
            username=config.username,
            password=config.password,
            component_id=config.component_id
        )

    def get_energy_balance(self) -> Dict[str, Any]:
        """
        Get current energy balance data.

        Returns:
            Dictionary containing:
                - time (str): Timestamp
                - pvGeneration (float): PV generation in watts
                - totalConsumption (float): Total consumption in watts
                - autarkyRate (float): Autarky rate (0-1)
                - selfConsumptionRate (float): Self consumption rate (0-1)
                - feedIn (float): Feed-in to grid in watts
                - externalConsumption (float): External consumption in watts
                - directConsumption (float): Direct consumption in watts
                - batteryStateOfCharge (float|None): Battery SoC percentage
                - batteryCharging (float|None): Battery charging in watts
                - batteryDischarging (float|None): Battery discharging in watts

        Raises:
            SMAAuthenticationError: If authentication fails
            SMAAPIError: If API request fails
            SMANetworkError: If network request fails

        Example:
            >>> energy = client.get_energy_balance()
            >>> print(f"PV: {energy['pvGeneration']} W")
        """
        logger.debug(f"Fetching energy balance for component {self.config.component_id}")
        params = {'componentId': self.config.component_id}
        result = self._make_request('GET', endpoints.ENERGY_BALANCE_URL, params=params)
        logger.info("Energy balance retrieved successfully")
        pv = result.get('pvGeneration')
        cons = result.get('totalConsumption')
        logger.debug(f"PV Generation: {pv} W, Consumption: {cons} W")
        return result

    def get_co2_savings(self, today_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get CO2 savings data.

        Args:
            today_date: Date in YYYY-MM-DD format (default: current date)

        Returns:
            Dictionary containing:
                - today (int): CO2 saved today in kg
                - total (int): Total CO2 saved in kg

        Raises:
            SMAAuthenticationError: If authentication fails
            SMAAPIError: If API request fails
            SMANetworkError: If network request fails

        Example:
            >>> co2 = client.get_co2_savings()
            >>> print(f"CO2 saved today: {co2['today']} kg")
        """
        from datetime import date

        logger.debug(f"Fetching CO2 savings for component {self.config.component_id}")

        if today_date is None:
            today_date = date.today().strftime("%Y-%m-%d")

        params = {
            'componentId': self.config.component_id,
            'todayDate': today_date
        }
        result = self._make_request('GET', endpoints.CO2_URL, params=params)
        logger.info("CO2 savings retrieved successfully")
        return result

    def get_revenue(self, today_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get revenue/earnings data.

        Args:
            today_date: Date in YYYY-MM-DD format (default: current date)

        Returns:
            Dictionary containing:
                - today (list): List of dicts with currencyCode3 and value
                - total (list): List of dicts with currencyCode3 and value

        Raises:
            SMAAuthenticationError: If authentication fails
            SMAAPIError: If API request fails
            SMANetworkError: If network request fails

        Example:
            >>> revenue = client.get_revenue()
            >>> total = revenue['total'][0]
            >>> print(f"Total: {total['value']:.2f} {total['currencyCode3']}")
        """
        from datetime import date

        logger.debug(f"Fetching revenue for component {self.config.component_id}")

        if today_date is None:
            today_date = date.today().strftime("%Y-%m-%d")

        params = {
            'componentId': self.config.component_id,
            'todayDate': today_date
        }
        result = self._make_request('GET', endpoints.REVENUE_URL, params=params)
        logger.info("Revenue retrieved successfully")
        return result

    def get_device_states(self) -> list:
        """
        Get device states for all devices in the plant.

        Returns:
            List of dictionaries, each containing:
                - componentType (str): Type of component (e.g., "Device")
                - componentId (str): Device ID
                - name (str): Device name/serial number
                - state (int): Device state code
                - additionalStateTag (str|None): Additional state info
                - stateFunctionTag (str|None): Function state info

        Raises:
            SMAAuthenticationError: If authentication fails
            SMAAPIError: If API request fails
            SMANetworkError: If network request fails

        Example:
            >>> devices = client.get_device_states()
            >>> for device in devices:
            ...     print(f"{device['name']}: state {device['state']}")
        """
        logger.debug(f"Fetching device states for component {self.config.component_id}")
        params = {'componentId': self.config.component_id}
        result = self._make_request('GET', endpoints.STATES_URL, params=params)
        logger.info(f"Device states retrieved successfully ({len(result)} devices)")
        return result

    def get_plant_info(self, plant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed plant information.

        Args:
            plant_id: Plant ID (default: uses component_id from config)

        Returns:
            Dictionary containing plant details:
                - plantId (str): Plant ID
                - name (str): Plant name
                - peakPower (int): Peak power in watts
                - startUpUtc (str): Plant startup date
                - city (str): City name
                - street (str): Street address
                - zipCode (str): ZIP code
                - longitude (float): Longitude coordinate
                - latitude (float): Latitude coordinate
                - timezone (str): Timezone identifier
                - countryName (str): Country name
                - currencyCode3 (str): Currency code (e.g., "EUR")
                - hasSelfConsumption (bool): Self-consumption enabled
                - hasTimezoneInfo (bool): Timezone info available
                - co2Factor (float): CO2 factor
                - co2Unit (str): CO2 unit (e.g., "kg")
                - currency (str): Currency symbol

        Raises:
            SMAAuthenticationError: If authentication fails
            SMAAPIError: If API request fails
            SMANetworkError: If network request fails

        Example:
            >>> plant = client.get_plant_info()
            >>> print(f"{plant['name']}: {plant['peakPower']/1000:.1f} kWp")
        """
        if plant_id is None:
            plant_id = self.config.component_id

        logger.debug(f"Fetching plant info for plant {plant_id}")
        url = endpoints.PLANT_URL.format(plant_id=plant_id)
        result = self._make_request('GET', url)
        logger.info("Plant info retrieved successfully")
        return result

    def get_weather_forecast(
        self,
        component_id: Optional[str] = None,
        start_date_utc: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get weather forecast for plant location.

        Args:
            component_id: Component ID (default: uses component_id from config)
            start_date_utc: Start date in ISO format (default: today at midnight UTC)

        Returns:
            Dictionary containing:
                - now (dict): Current weather with time, iconId, temperature
                - tomorrow (dict): Tomorrow's forecast with date, iconId, min/max temp
                - city (str): City name

        Raises:
            SMAAuthenticationError: If authentication fails
            SMAAPIError: If API request fails
            SMANetworkError: If network request fails

        Example:
            >>> weather = client.get_weather_forecast()
            >>> print(f"Current temp: {weather['now']['temperature']}°C")
        """
        from datetime import datetime, timezone

        if component_id is None:
            component_id = self.config.component_id

        logger.debug(f"Fetching weather forecast for component {component_id}")
        url = endpoints.WEATHER_URL.format(component_id=component_id)

        if start_date_utc is None:
            # Use today at midnight UTC
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            start_date_utc = today.isoformat().replace('+00:00', 'Z')

        params = {'startTodayUtc': start_date_utc}
        result = self._make_request('GET', url, params=params)
        logger.info("Weather forecast retrieved successfully")
        return result

    def get_sensor_data(self, sensor_type: str) -> Dict[str, Any]:
        """
        Get sensor data for specified sensor type.

        Args:
            sensor_type: Sensor type identifier. Valid values:
                - "PlantInsolationSensor" - Solar irradiation (W/m²)
                - "PlantWindVelocitySensor" - Wind speed (m/s)
                - "PlantModuleTemperatureSensor" - Module temperature (°C)
                - "PlantAmbientTemperatureSensor" - Ambient temperature (°C)

        Returns:
            Dictionary containing:
                - timestampUtc (str): Timestamp in ISO format
                - value (float): Sensor value (units depend on sensor type)
                - channelId (str): Channel identifier

        Raises:
            SMAAuthenticationError: If authentication fails
            SMAAPIError: If API request fails
            SMANetworkError: If network request fails
            ValueError: If sensor_type is invalid

        Example:
            >>> irradiation = client.get_sensor_data("PlantInsolationSensor")
            >>> print(f"Solar irradiation: {irradiation['value']} W/m²")
        """
        valid_sensors = [
            "PlantInsolationSensor",
            "PlantWindVelocitySensor",
            "PlantModuleTemperatureSensor",
            "PlantAmbientTemperatureSensor"
        ]

        if sensor_type not in valid_sensors:
            raise ValueError(
                f"Invalid sensor_type '{sensor_type}'. "
                f"Valid values: {', '.join(valid_sensors)}"
            )

        logger.debug(f"Fetching sensor data for {sensor_type}")
        params = {
            'componentId': self.config.component_id,
            'widgetType': sensor_type
        }
        result = self._make_request('GET', endpoints.SENSOR_URL, params=params)
        logger.info(f"Sensor data retrieved successfully for {sensor_type}")
        return result

    def is_authenticated(self) -> bool:
        """
        Check if client is currently authenticated with valid token.

        Returns:
            True if authenticated and token valid, False otherwise

        Example:
            >>> if client.is_authenticated():
            ...     print("Already authenticated")
        """
        return self.auth.is_authenticated()

    def refresh_token(self) -> bool:
        """
        Manually refresh authentication token.

        Returns:
            True if refresh successful, False otherwise

        Note:
            Token refresh is handled automatically by API methods,
            so manual refresh is rarely needed.
        """
        return self.auth._refresh_access_token()

    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            **kwargs: Additional arguments passed to requests

        Returns:
            Parsed JSON response

        Raises:
            SMAAuthenticationError: If authentication fails
            SMAAPIError: If API request fails
            SMANetworkError: If network request fails
        """
        # Ensure we have a valid token
        logger.debug("Ensuring valid authentication token")
        if not self.auth.ensure_valid_token():
            raise SMAAuthenticationError("Failed to obtain valid authentication token")

        # Sanitize URL for logging (remove query parameters that might contain sensitive data)
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        safe_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

        # Log request details
        params = kwargs.get('params', {})
        if params:
            logger.debug(f"Making {method} request to {safe_url} with parameters: {params}")
        else:
            logger.debug(f"Making {method} request to {safe_url}")

        # Set required headers
        headers = kwargs.pop('headers', {})
        headers.update({
            'Authorization': f'Bearer {self.auth.bearer_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Origin': 'https://ennexos.sunnyportal.com'
        })

        # Make request
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            raise SMANetworkError(f"Network error during API request: {e}")

        logger.debug(f"Response status code: {response.status_code}")

        # Handle response
        if response.status_code == 200:
            try:
                result = response.json()
                logger.debug("Successfully parsed JSON response")
                return result
            except ValueError as e:
                logger.error(f"Failed to parse response as JSON: {e}")
                raise SMAAPIError(
                    f"Failed to parse API response as JSON: {e}",
                    status_code=response.status_code,
                    response_body=response.text
                )
        elif response.status_code == 401:
            logger.warning("Authorization failed (401) - token may be invalid")
            raise SMAAuthenticationError(
                f"Authorization failed. Token may be invalid or expired. Response: {response.text}"
            )
        elif response.status_code == 403:
            logger.error("Access forbidden (403)")
            raise SMAAPIError(
                "Access forbidden. Check permissions.",
                status_code=response.status_code,
                response_body=response.text
            )
        else:
            logger.error(f"API request failed with status {response.status_code}")
            raise SMAAPIError(
                f"API request failed with status code {response.status_code}",
                status_code=response.status_code,
                response_body=response.text
            )
