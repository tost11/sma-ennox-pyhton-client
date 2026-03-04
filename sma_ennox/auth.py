"""OAuth2/PKCE authentication handler for SMA API."""

import secrets
import hashlib
import base64
import time
import logging
from typing import Tuple, Optional
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

from . import endpoints
from .exceptions import SMAAuthenticationError, SMANetworkError

logger = logging.getLogger(__name__)


class OAuth2Handler:
    """Handles OAuth2 Authorization Code Flow with PKCE for SMA API."""

    def __init__(self, username: str, password: str, session: Optional[requests.Session] = None):
        """
        Initialize OAuth2 handler.

        Args:
            username: SMA account usernamea
            password: SMA account password
            session: Optional existing requests.Session instance
        """
        self.username = username
        self.password = password
        self.session = session if session else requests.Session()

        # PKCE parameters (generated during login)
        self.code_verifier: Optional[str] = None
        self.code_challenge: Optional[str] = None
        self.state: Optional[str] = None
        self.nonce: Optional[str] = None

        # Authentication tokens
        self.bearer_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None

    def login(self) -> bool:
        """
        Execute full OAuth2/PKCE authentication flow.

        Returns:
            True if authentication successful, False otherwise

        Raises:
            SMAAuthenticationError: If authentication fails
            SMANetworkError: If network request fails
        """
        try:
            logger.debug("Starting OAuth2/PKCE authentication flow")

            # Step 1: Generate PKCE parameters
            logger.debug("Step 1: Generating PKCE parameters")
            self.code_verifier = self._generate_code_verifier()
            self.code_challenge = self._generate_code_challenge(self.code_verifier)
            self.state = self._generate_random_state()
            self.nonce = self._generate_random_state()

            # Step 2: Initiate OAuth2 flow
            logger.debug("Step 2: Initiating OAuth2 flow")
            html = self._initiate_oauth_flow()

            # Step 3: Extract form action URL
            logger.debug("Step 3: Extracting form action URL")
            form_action_url = self._extract_form_action(html)

            # Step 4: Submit credentials and get authorization code
            logger.debug("Step 4: Submitting credentials")
            authorization_code = self._submit_credentials(form_action_url)

            # Step 5: Exchange authorization code for access token
            logger.debug("Step 5: Exchanging authorization code for token")
            self.bearer_token, self.refresh_token, self.token_expires_at = self._exchange_code_for_token(
                authorization_code
            )

            if self.bearer_token:
                logger.info("OAuth2 authentication successful")
                return True
            else:
                raise SMAAuthenticationError("Failed to obtain bearer token")

        except SMAAuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except SMANetworkError as e:
            logger.error(f"Network error during authentication: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected authentication error: {e}")
            raise SMAAuthenticationError(f"Authentication error: {e}")

    def ensure_valid_token(self) -> bool:
        """
        Ensure we have a valid token, refresh or re-authenticate if needed.

        Returns:
            True if valid token available, False otherwise

        Raises:
            SMAAuthenticationError: If authentication fails
        """
        # Check if token is expired or about to expire
        if self.token_expires_at and time.time() < self.token_expires_at:
            remaining = int(self.token_expires_at - time.time())
            logger.debug(f"Token is valid, expires in {remaining} seconds")
            return True  # Token still valid

        # Try to refresh
        logger.debug("Token expired or expiring soon, refreshing...")
        if self._refresh_access_token():
            return True

        # Refresh failed, re-authenticate
        logger.warning("Token refresh failed, re-authenticating...")
        return self.login()

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated with valid token.

        Returns:
            True if authenticated and token valid, False otherwise
        """
        return (
            self.bearer_token is not None
            and self.token_expires_at is not None
            and time.time() < self.token_expires_at
        )

    def _generate_code_verifier(self) -> str:
        """
        Generate OAuth2 PKCE code verifier.

        Returns:
            Random 43-character base64url string
        """
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

    def _generate_code_challenge(self, code_verifier: str) -> str:
        """
        Generate OAuth2 PKCE code challenge from verifier.

        Args:
            code_verifier: The code verifier string

        Returns:
            SHA256 hash of verifier as base64url string
        """
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

    def _generate_random_state(self, length: int = 48) -> str:
        """
        Generate random state/nonce for OAuth2 flow.

        Args:
            length: Desired length of random string (default: 48)

        Returns:
            Random base64url string of specified length
        """
        num_bytes = (length * 3) // 4
        return base64.urlsafe_b64encode(secrets.token_bytes(num_bytes)).decode('utf-8').rstrip('=')[:length]

    def _initiate_oauth_flow(self) -> str:
        """
        GET OAuth2 authorization endpoint, return HTML login form.

        Returns:
            HTML content of login form

        Raises:
            SMAAuthenticationError: If OAuth initialization fails
            SMANetworkError: If network request fails
        """
        params = {
            'response_type': 'code',
            'client_id': endpoints.CLIENT_ID,
            'redirect_uri': endpoints.REDIRECT_URI,
            'scope': endpoints.SCOPE,
            'code_challenge': self.code_challenge,
            'code_challenge_method': 'S256',
            'state': self.state,
            'nonce': self.nonce
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        # Sanitize URL for logging (remove query parameters)
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(endpoints.OAUTH_AUTH_URL)
        safe_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        logger.debug(f"Sending OAuth authorization request to {safe_url}")

        try:
            response = self.session.get(endpoints.OAUTH_AUTH_URL, params=params, headers=headers)
        except requests.RequestException as e:
            raise SMANetworkError(f"Network error during OAuth initialization: {e}")

        if response.status_code != 200:
            logger.error(f"OAuth initialization failed with status {response.status_code}")
            raise SMAAuthenticationError(f"OAuth initialization failed with status {response.status_code}")

        logger.debug(f"Received login form HTML ({len(response.text)} bytes)")
        return response.text

    def _extract_form_action(self, html: str) -> str:
        """
        Parse HTML to extract login form action URL.

        Args:
            html: HTML content containing login form

        Returns:
            Form action URL

        Raises:
            SMAAuthenticationError: If form parsing fails
        """
        soup = BeautifulSoup(html, 'html.parser')
        form = soup.find('form', {'name': 'loginForm'})

        if not form or 'action' not in form.attrs:
            raise SMAAuthenticationError("Failed to parse login form from HTML")

        return form['action']

    def _submit_credentials(self, form_action_url: str) -> str:
        """
        POST credentials and return authorization code from redirect.

        Args:
            form_action_url: URL to submit credentials to

        Returns:
            Authorization code

        Raises:
            SMAAuthenticationError: If credential submission fails
            SMANetworkError: If network request fails
        """
        # Sanitize URL for logging
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(form_action_url)
        safe_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        logger.debug(f"Submitting credentials to {safe_url}")

        login_data = {
            'username': self.username,
            'password': self.password,
            'credentialId': ''
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        try:
            response = self.session.post(
                form_action_url,
                data=login_data,
                headers=headers,
                allow_redirects=False
            )
        except requests.RequestException as e:
            raise SMANetworkError(f"Network error during credential submission: {e}")

        if response.status_code != 302:
            logger.error(f"Credential submission failed with status {response.status_code}")
            raise SMAAuthenticationError(f"Credential submission failed with status {response.status_code}")

        # Extract authorization code from redirect URL
        redirect_url = response.headers.get('Location', '')
        if 'code=' not in redirect_url:
            logger.error("Authorization code not found in redirect URL")
            raise SMAAuthenticationError("Authorization code not found in redirect URL")

        # Parse the code from the redirect URL
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)

        if 'code' not in query_params:
            logger.error("Failed to extract authorization code")
            raise SMAAuthenticationError("Failed to extract authorization code")

        logger.debug("Received redirect with authorization code")
        return query_params['code'][0]

    def _exchange_code_for_token(self, authorization_code: str) -> Tuple[str, str, float]:
        """
        Exchange authorization code for access token.

        Args:
            authorization_code: Authorization code from OAuth flow

        Returns:
            Tuple of (access_token, refresh_token, expires_at)

        Raises:
            SMAAuthenticationError: If token exchange fails
            SMANetworkError: If network request fails
        """
        logger.debug("Exchanging authorization code for access token")

        token_data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': endpoints.REDIRECT_URI,
            'client_id': endpoints.CLIENT_ID,
            'code_verifier': self.code_verifier
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = self.session.post(
                endpoints.OAUTH_TOKEN_URL,
                data=token_data,
                headers=headers
            )
        except requests.RequestException as e:
            raise SMANetworkError(f"Network error during token exchange: {e}")

        if response.status_code != 200:
            logger.error(f"Token exchange failed with status {response.status_code}")
            raise SMAAuthenticationError(
                f"Token exchange failed with status {response.status_code}: {response.text}"
            )

        token_response = response.json()
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        expires_in = token_response.get('expires_in', 300)
        expires_at = time.time() + expires_in - 30  # 30s buffer

        logger.debug(f"Token received, expires in {expires_in} seconds")
        return (access_token, refresh_token, expires_at)

    def _refresh_access_token(self) -> bool:
        """
        Use refresh token to obtain new access token.

        Returns:
            True if refresh successful, False otherwise
        """
        if not self.refresh_token:
            logger.warning("No refresh token available")
            return False

        logger.debug("Attempting to refresh access token")

        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': endpoints.CLIENT_ID,
            'scope': endpoints.SCOPE
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        try:
            response = self.session.post(endpoints.OAUTH_TOKEN_URL, data=token_data, headers=headers)
            if response.status_code == 200:
                token_response = response.json()
                self.bearer_token = token_response.get('access_token')
                self.refresh_token = token_response.get('refresh_token')
                expires_in = token_response.get('expires_in', 300)
                self.token_expires_at = time.time() + expires_in - 30
                logger.debug(f"Token refresh successful, new expiration in {expires_in} seconds")
                return True
            logger.warning(f"Token refresh failed with status {response.status_code}")
            return False
        except Exception as e:
            logger.warning(f"Token refresh failed with exception: {e}")
            return False
