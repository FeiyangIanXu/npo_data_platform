import json
from typing import Any

import requests


BASE_URL = "https://projects.propublica.org/nonprofits/api/v2"
DEFAULT_TIMEOUT = 30


def build_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }
    )
    return session


def fetch_organization_payload(
    session: requests.Session,
    ein: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    response = session.get(f"{BASE_URL}/organizations/{ein}.json", timeout=timeout)
    response.raise_for_status()
    try:
        payload = response.json()
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON response for EIN {ein}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Unexpected payload type for EIN {ein}: {type(payload).__name__}")
    return payload


def get_nested(payload: dict[str, Any], path: str, default: Any = None) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current
