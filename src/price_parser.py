import logging
from typing import Any

log = logging.getLogger(__name__)

# Substrings used to identify price fields in the response. Matched
# case-insensitively against dict keys.
PRICE_KEY_HINTS = ("regular", "premium", "diesel", "midgrade", "mid_grade")


def parse_prices(payload: Any) -> dict:
    """Walk the API response and pull out any gas price fields.

    The Costco endpoint's shape has varied over time, so this searches both
    top-level and nested dicts/lists for keys that look like prices.
    """
    prices: dict = {}
    if isinstance(payload, dict):
        for key, val in payload.items():
            if isinstance(key, str) and any(h in key.lower() for h in PRICE_KEY_HINTS):
                prices[key] = val
            if isinstance(val, (dict, list)):
                prices.update(parse_prices(val))
    elif isinstance(payload, list):
        for item in payload:
            prices.update(parse_prices(item))
    return prices
