import logging
from typing import Any

import requests

log = logging.getLogger(__name__)


def fetch_warehouse_id(
    url: str,
    params: dict,
    headers: dict,
    timeout: int,
    id_path: str,
) -> str:
    """Call the warehouse-ID endpoint and dig out the ID.

    `id_path` is a dotted path into the JSON response. List indices are
    supported as integer segments, e.g. "warehouses.0.id".
    """
    log.info("Fetching warehouse id from %s", url)
    resp = requests.get(url, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    value = _dig(payload, id_path)
    log.info("Resolved warehouse id: %s", value)
    return str(value)


def _dig(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur[part]
        elif isinstance(cur, list):
            cur = cur[int(part)]
        else:
            raise KeyError(
                f"cannot navigate id_path '{path}' at '{part}': "
                f"current value is {type(cur).__name__}"
            )
    return cur
