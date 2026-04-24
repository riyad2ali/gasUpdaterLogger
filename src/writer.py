import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

log = logging.getLogger(__name__)

CENTRAL = ZoneInfo("America/Chicago")


def write_record(path: Path, name: str, prices: dict, raw: Optional[dict] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(CENTRAL).strftime("%Y-%m-%d %H:%M:%S CT")
    pairs = "  ".join(f"{k}={v}" for k, v in prices.items()) if prices else "(no prices extracted)"
    line = f"[{ts}]   {name:<22}  {pairs}"
    if raw is not None:
        line += "  |  raw=" + json.dumps(raw, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    log.info("Wrote record (%s): %s", name, pairs)


def write_separator(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write("\n")
