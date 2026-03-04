"""API endpoint definitions and constants."""

# OAuth2 endpoints
AUTH_BASE_URL = "https://login.sma.energy/auth/realms/SMA"
OAUTH_AUTH_URL = f"{AUTH_BASE_URL}/protocol/openid-connect/auth"
OAUTH_TOKEN_URL = f"{AUTH_BASE_URL}/protocol/openid-connect/token"

# API endpoints
API_BASE_URL = "https://uiapi.sunnyportal.com/api/v1"
ENERGY_BALANCE_URL = f"{API_BASE_URL}/widgets/energybalance"

# OAuth2 constants
CLIENT_ID = "SPpbeOS"
REDIRECT_URI = "https://ennexos.sunnyportal.com/dashboard/initialize"
SCOPE = "openid profile"
