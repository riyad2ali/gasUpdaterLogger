import logging

import requests

log = logging.getLogger(__name__)


def fetch(url: str, params: dict, timeout: int, headers: dict) -> dict:
    log.info("Fetching %s params=%s", url, params)
    resp = requests.get(url, params=params, timeout=timeout, headers=headers)
    resp.raise_for_status()
    return resp.json()
