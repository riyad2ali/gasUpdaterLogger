import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


def write_record(path: Path, prices: dict, raw: Optional[dict] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    pairs = ", ".join(f"{k}={v}" for k, v in prices.items()) if prices else "(no prices extracted)"
    line = f"[{ts}] {pairs}"
    if raw is not None:
        line += " | raw=" + json.dumps(raw, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    log.info("Wrote record to %s: %s", path, pairs)
