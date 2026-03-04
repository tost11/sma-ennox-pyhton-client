# SMA Solar API - OAuth2/PKCE Authentication Flow

This document describes the complete authentication flow required to access the SMA Sunny Portal API.

## Overview

The SMA Solar API uses OAuth2 Authorization Code Flow with PKCE (Proof Key for Code Exchange) for authentication. The flow involves 5 main steps:

1. Generate PKCE parameters
2. Initiate OAuth2 flow
3. Submit credentials
4. Exchange authorization code for access token
5. Use access token for API requests

## Authentication Flow Details

### Step 1: Generate PKCE Parameters

Before initiating the OAuth flow, generate the following security parameters:

- **code_verifier**: Random 43-character base64url string
  - Generated from 32 random bytes
  - Example: `dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk`

- **code_challenge**: SHA256 hash of code_verifier, base64url encoded
  - `SHA256(code_verifier)` → base64url encode
  - Example: `E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM`

- **state**: Random 48-character base64url string for CSRF protection
  - Example: `LlBNWF9fdUpQYlhYSnZVZEJXNkpMaTBGbS1uNHJJS29OLUhvSVFOUTBwQ1FZ`

- **nonce**: Random 48-character base64url string
  - Example: `eFZ4bUNWLkVmV2lDR0UxUXBnd1RYcmNKR3dram01endRNXBiSTV2RGdvNUt1`

**Important**: Store `code_verifier` securely - it's required for token exchange in Step 4.

---

### Step 2: Initiate OAuth2 Flow

**Request**:
```
GET https://login.sma.energy/auth/realms/SMA/protocol/openid-connect/auth
```

**Query Parameters**:
```
response_type=code
client_id=SPpbeOS
redirect_uri=https://ennexos.sunnyportal.com/dashboard/initialize
scope=openid profile
code_challenge={generated_code_challenge}
code_challenge_method=S256
state={generated_state}
nonce={generated_nonce}
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
```

**Response**:
- **Status**: `200 OK`
- **Content-Type**: `text/html`
- **Body**: HTML page containing login form
- **Cookies Set**:
  - `AUTH_SESSION_ID`: Keycloak session identifier
  - `KC_RESTART`: Encrypted session data
  - `KC_AUTH_SESSION_HASH`: Session hash

**What to Extract**:
Parse the HTML to extract the login form's `action` attribute, which contains dynamic parameters needed for Step 3.

Example form action URL:
```
https://login.sma.energy/auth/realms/SMA/login-actions/authenticate?
  session_code=fERoDmdW5qvTEYg20tihKHhiTqAX7pM1wNJ88PDXo4A
  &execution=53c7478e-21f1-4f92-a37b-1c1015a7a53a
  &client_id=SPpbeOS
  &tab_id=QTlt0a88ftI
  &client_data=eyJydSI6Imh0dHBzOi8vZW5uZXhvcy5zdW5ueXBvcnRhbC5jb20vZGFzaGJvYXJkL2luaXRpYWxpemUiLCJydCI6ImNvZGUiLCJzdCI6IkxsQk5XRjlmZFVwUVlsaFlTblpWWkVKWE5rcE1hVEJHYlMxdU5ISkpTMjlPTFVodlNWRk9VVEJ3UTFGWiJ9
```

**Important**: All cookies from this response must be sent with the next request.

---

### Step 3: Submit Credentials

**Request**:
```
POST {form_action_url_from_step2}
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Content-Type: application/x-www-form-urlencoded
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Cookie: AUTH_SESSION_ID=...; KC_AUTH_SESSION_HASH=...; KC_RESTART=...
```

**Body** (URL-encoded):
```
username={your_username}
password={your_password}
credentialId=
```

**Important**: Set `allow_redirects=False` to capture the redirect response.

**Response**:
- **Status**: `302 Found`
- **Headers**:
  - `Location`: Redirect URL containing authorization code
- **Cookies Set**:
  - `KC_RESTART`: Cleared (Max-Age=0)
  - `KEYCLOAK_IDENTITY`: JWT session token (not the API access token)
  - `KEYCLOAK_SESSION`: Session identifier

**Example Location Header**:
```
https://ennexos.sunnyportal.com/dashboard/initialize?
  state=LlBNWF9fdUpQYlhYSnZVZEJXNkpMaTBGbS1uNHJJS29OLUhvSVFOUTBwQ1FZ
  &session_state=529dbb42-832b-2bc5-766b-91328d34e1f8
  &iss=https%3A%2F%2Flogin.sma.energy%2Fauth%2Frealms%2FSMA
  &code=2c879d89-0fb8-d5a5-ca51-1e4ba9e43c39.529dbb42-832b-2bc5-766b-91328d34e1f8.b17f711e-b79d-41a8-b699-004f9d53591d
```

**What to Extract**:
Parse the `code` parameter from the Location URL. This is the authorization code needed for Step 4.

Example authorization code:
```
2c879d89-0fb8-d5a5-ca51-1e4ba9e43c39.529dbb42-832b-2bc5-766b-91328d34e1f8.b17f711e-b79d-41a8-b699-004f9d53591d
```

---

### Step 4: Exchange Authorization Code for Access Token

**Request**:
```
POST https://login.sma.energy/auth/realms/SMA/protocol/openid-connect/token
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Content-Type: application/x-www-form-urlencoded
```

**Body** (URL-encoded):
```
grant_type=authorization_code
code={authorization_code_from_step3}
redirect_uri=https://ennexos.sunnyportal.com/dashboard/initialize
client_id=SPpbeOS
code_verifier={code_verifier_from_step1}
```

**Important**: The `code_verifier` must be the same value generated in Step 1. This is how PKCE validates the request.

**Response**:
- **Status**: `200 OK`
- **Content-Type**: `application/json`

**Response Body**:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIyMTd6NUNVMjRvRE1QR2Q1SHZweHFGdFFkY0pFMFBTQldmSVUzaHlNSVM4In0.eyJleHAiOjE3NzA5MDQ5MDQsImlhdCI6MTc3MDkwNDYwNCwiYXV0aF90aW1lIjoxNzcwOTA0NTUxLCJqdGkiOiJvbnJ0YWM6ZjIwOGNlYzYtZWUyNi1lMjBjLTgxODAtYTAyY2VlNTExZGRkIiwiaXNzIjoiaHR0cHM6Ly9sb2dpbi5zbWEuZW5lcmd5L2F1dGgvcmVhbG1zL1NNQSIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJmOmEyYmFhMjFiLTU4MTEtNDEwMy04ZDYzLTdkNzRhMzZiYTJkMTplNTAzMWVhNy1mMjcwLTQ1NDktODJlOC01MGRmODFlMjJlNjUiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJTUHBiZU9TIiwic2lkIjoiMDVjMTI5ZWMtMTRkYy1hZWQzLTY4OGQtOTA3Njg0Y2MxNTQ1IiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vZG1jLXVpLnN1bm55cG9ydGFsLmNvbSIsImh0dHA6Ly9lbm5leG9zLnN1bm55cG9ydGFsLmNvbSIsImh0dHA6Ly80Nndwb3I5OS5wcmQucG9ydGFsLmRtejo4ODg4IiwiaHR0cHM6Ly9lbm5leG9zLnN1bm55cG9ydGFsLmNvbSIsImh0dHA6Ly80NnZwbzAyLnByZC5wb3J0YWwuZG16IiwiaHR0cHM6Ly90c3RwcmQtdWkuc3Vobnlwb3J0YWwuY29tIiwiaHR0cDovLzQ2dnBvMDEucHJkLnBvcnRhbC5kbXoiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGRpZ2l0YWx0d2luQXBpOnJlYWQgZGlnaXRhbHR3aW5BcGk6d3JpdGUgZW1haWwiLCJ1aWQiOiIyMjIwODY0IiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJzbWFVc2VyTW9kZWwiOiJTbWFJZCIsInByZWZlcnJlZF91c2VybmFtZSI6ImFubmUud2llaHJAc29sb2NhbC1lbmVyZ3kuZGUiLCJlbWFpbCI6ImFubmUud2llaHJAc29sb2NhbC1lbmVyZ3kuZGUifQ...",
  "expires_in": 300,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzUxMiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI...",
  "token_type": "Bearer",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI...",
  "not-before-policy": 0,
  "session_state": "529dbb42-832b-2bc5-766b-91328d34e1f8",
  "scope": "openid profile digitalTwinApi:read digitalTwinApi:write email"
}
```

**What to Extract**:
- `access_token`: This is the JWT Bearer token used for API requests
- `expires_in`: Token validity in seconds (typically 300 = 5 minutes)
- `refresh_token`: Can be used to obtain new access tokens without re-authenticating

**Access Token Details**:
- **Type**: JWT (JSON Web Token)
- **Algorithm**: RS256 (RSA with SHA-256)
- **Issuer**: `https://login.sma.energy/auth/realms/SMA`
- **Audience**: `account`
- **Token Type**: `Bearer`
- **Scopes**: `openid profile digitalTwinApi:read digitalTwinApi:write email`

---

### Step 5: Use Access Token for API Requests

**Request**:
```
GET https://uiapi.sunnyportal.com/api/v1/widgets/energybalance
```

**Query Parameters**:
```
componentId={your_component_id}
```

**Headers**:
```
Authorization: Bearer {access_token_from_step4}
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: application/json
```

**Response**:
- **Status**: `200 OK`
- **Content-Type**: `application/json`

**Response Body**:
```json
{
  "time": "2026-02-12T14:55:00",
  "pvPeakPower": 50000,
  "corrected": null,
  "autarkyRate": 0.07668218625235868,
  "selfConsumptionRate": 1,
  "pvGeneration": 2362.8,
  "dieselGeneration": null,
  "combinedHeatAndPowerGeneration": null,
  "hydroGeneration": null,
  "totalGeneration": 2362.8,
  "feedIn": 0,
  "externalConsumption": 28450.093,
  "totalConsumption": 30812.893,
  "batteryCharging": null,
  "batteryDischarging": null,
  "batteryStateOfCharge": null,
  "directConsumption": 2362.8,
  "peakLoadShavingThreshold": null
}
```

---

## Token Management

### Access Token Expiration

Access tokens typically expire after 5 minutes (300 seconds). When a token expires, API requests will return:
```
HTTP 401 Unauthorized
{"message":"Unauthorized","code":"401"}
```

### Token Refresh

Instead of re-authenticating, use the `refresh_token` from Step 4:

**Request**:
```
POST https://login.sma.energy/auth/realms/SMA/protocol/openid-connect/token
```

**Headers**:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Content-Type: application/x-www-form-urlencoded
Accept: application/json
```

**Body** (URL-encoded):
```
grant_type=refresh_token
refresh_token={refresh_token_from_step4}
client_id=SPpbeOS
scope=openid profile
```

**Response**:
- **Status**: `200 OK`
- **Content-Type**: `application/json`

**Response Body**:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIy...",
  "expires_in": 300,
  "refresh_expires_in": 172800,
  "refresh_token": "eyJhbGciOiJIUzUxMiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI...",
  "token_type": "Bearer",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI...",
  "not-before-policy": 0,
  "session_state": "529dbb42-832b-2bc5-766b-91328d34e1f8",
  "scope": "openid profile digitalTwinApi:read digitalTwinApi:write email"
}
```

**What to Extract**:
- `access_token`: New JWT Bearer token for API requests (valid for 300 seconds)
- `refresh_token`: New refresh token (valid for 172800 seconds = 48 hours)
- `expires_in`: Access token validity in seconds

**Important Notes**:
- Refresh tokens are valid for 48 hours (172800 seconds)
- Each refresh request returns both a new access token AND a new refresh token
- The old refresh token becomes invalid after use
- Always update both tokens after a successful refresh

---

## Security Considerations

### PKCE (Proof Key for Code Exchange)

PKCE prevents authorization code interception attacks:

1. **Code Verifier**: Random secret generated client-side
2. **Code Challenge**: SHA256 hash of code verifier sent in initial request
3. **Verification**: Server validates that code_verifier matches original code_challenge

This ensures that even if the authorization code is intercepted, it cannot be used without the original code_verifier.

### State Parameter

The `state` parameter prevents CSRF attacks:
- Generated before OAuth flow starts
- Sent in initial request
- Returned by server in redirect
- Client must verify state matches before proceeding

### Important Cookies

- **KEYCLOAK_IDENTITY**: Server-side session token (not for API use)
- **KEYCLOAK_SESSION**: Server-side session identifier
- **AUTH_SESSION_ID**: Temporary session during login flow

These cookies are only needed during the authentication flow (Steps 2-3), not for API requests.

---

## Constants

| Parameter | Value |
|-----------|-------|
| Client ID | `SPpbeOS` |
| Redirect URI | `https://ennexos.sunnyportal.com/dashboard/initialize` |
| Auth Base URL | `https://login.sma.energy/auth/realms/SMA` |
| API Base URL | `https://uiapi.sunnyportal.com/api/v1` |
| Scopes | `openid profile` |
| Code Challenge Method | `S256` |

---

## Error Handling

### Step 2 Errors
- **Non-200 Status**: OAuth endpoint unavailable
- **Missing Form**: HTML structure changed, form parsing failed

### Step 3 Errors
- **Non-302 Status**: Invalid credentials or server error
- **Missing Location Header**: Authentication failed
- **No Code in Location**: OAuth flow failed

### Step 4 Errors
- **400 Bad Request**: Invalid authorization code or code_verifier mismatch
- **401 Unauthorized**: Code expired or already used
- **Missing access_token**: Unexpected response format

### Step 5 Errors
- **401 Unauthorized**: Access token expired or invalid
- **403 Forbidden**: Insufficient permissions for resource
- **404 Not Found**: Invalid component ID

---

## Flow Diagram

```
┌──────────────┐
│    Client    │
└──────┬───────┘
       │
       │ 1. Generate PKCE parameters
       │    (code_verifier, code_challenge, state, nonce)
       │
       │ 2. GET /auth/...?code_challenge=...
       ├──────────────────────────────────────────────────────────┐
       │                                                          │
       │                                      ┌───────────────────▼─────┐
       │                                      │  Keycloak (SMA Auth)   │
       │◄─────────────────────────────────────┤  Returns HTML form      │
       │  HTML with login form                └───────────────────┬─────┘
       │  + Cookies (AUTH_SESSION_ID, etc.)                       │
       │                                                           │
       │ 3. Extract form action URL                               │
       │                                                           │
       │ 4. POST credentials to form URL                          │
       ├──────────────────────────────────────────────────────────►
       │                                                           │
       │◄──────────────────────────────────────────────────────────┤
       │  302 Redirect with authorization code                    │
       │  Location: ...?code=xxx&state=...                        │
       │  + Cookies (KEYCLOAK_IDENTITY, SESSION)                  │
       │                                                           │
       │ 5. Extract authorization code from redirect              │
       │                                                           │
       │ 6. POST /token with code + code_verifier                 │
       ├──────────────────────────────────────────────────────────►
       │                                                           │
       │◄──────────────────────────────────────────────────────────┤
       │  200 OK                                                   │
       │  { "access_token": "...", "refresh_token": "..." }       │
       │                                                           │
       │ 7. Store access_token                                    │
       │                                                           │
       │ 8. GET /api/v1/widgets/energybalance                     │
       │    Authorization: Bearer {access_token}     ┌────────────▼──────┐
       ├─────────────────────────────────────────────►  SMA API Server   │
       │                                             └────────────┬──────┘
       │◄─────────────────────────────────────────────────────────┘
       │  200 OK
       │  { "pvGeneration": 2362.8, ... }
       │
       ▼
```

---

## Implementation Notes

1. **Session Management**: Use a single HTTP session (e.g., `requests.Session()`) to maintain cookies throughout Steps 2-4.

2. **HTML Parsing**: Use a robust HTML parser (e.g., BeautifulSoup) to extract the form action URL, as it contains dynamic session parameters.

3. **URL Parsing**: Use proper URL parsing libraries to extract query parameters from redirect URLs.

4. **Token Storage**: Store access tokens securely. Consider encryption for long-term storage.

5. **Error Messages**: Credential errors may be embedded in HTML responses rather than HTTP status codes.

6. **Rate Limiting**: The API may have rate limits. Implement exponential backoff for retries.

7. **Token Lifecycle**: Implement token refresh before expiration to avoid service interruptions.
