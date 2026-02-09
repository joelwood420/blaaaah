import requests
import keyring
from typing import Optional, Dict

DEVICE_URL = "https://github.com/login/device/code"
TOKEN_URL = "https://github.com/login/oauth/access_token"

SERVICE_NAME = "blaaaah"


def start_device_flow(client_id: str, scope: str = "repo") -> Dict:
    """Start GitHub device flow. Returns the response dict with device_code, user_code, verification_uri, interval."""
    resp = requests.post(DEVICE_URL, data={"client_id": client_id, "scope": scope}, headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()


def poll_token_once(client_id: str, device_code: str) -> Dict:
    """Poll token endpoint once. Returns dict; on success contains access_token."""
    data = {
        "client_id": client_id,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }
    resp = requests.post(TOKEN_URL, data=data, headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()


def save_token(token: str):
    keyring.set_password(SERVICE_NAME, "github_token", token)


def get_saved_token() -> Optional[str]:
    return keyring.get_password(SERVICE_NAME, "github_token")
