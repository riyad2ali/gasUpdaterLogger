"""Gas price logger pipeline.

Loop forever: for each warehouse fetch -> parse -> write, sleeping
`interval_seconds` between full cycles. Runs until killed (Ctrl+C or SIGTERM).
"""
import logging
import signal
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from config_loader import load_config
from fetcher import fetch
from logger_setup import setup_logger
from price_parser import parse_prices
from warehouse_id import fetch_warehouse_id
from writer import write_record, write_separator

log = logging.getLogger("gas_logger")

_should_stop = False


def _handle_signal(signum, _frame):
    global _should_stop
    log.info("Received signal %s, shutting down after current iteration", signum)
    _should_stop = True


def run_once(cfg: dict) -> None:
    api = cfg["api"]
    warehouses = cfg.get("warehouses") or []
    output = cfg["output"]
    data_path = ROOT / output["data_file"]

    if warehouses:
        for warehouse in warehouses:
            wh_name = warehouse["name"]
            wh_id = str(warehouse["id"])
            try:
                raw = fetch(
                    url=api["url"],
                    params={"warehouseid": wh_id},
                    timeout=api.get("timeout_seconds", 30),
                    headers=api.get("headers", {}),
                )
                prices = parse_prices(raw)
                write_record(
                    path=data_path,
                    name=wh_name,
                    prices=prices,
                    raw=raw if output.get("include_raw_json") else None,
                )
            except Exception:
                log.exception("Failed for warehouse %s (id=%s)", wh_name, wh_id)
        write_separator(data_path)
    else:
        # Single-warehouse fallback — uses api.params.warehouseid or warehouse_api.
        params = dict(api.get("params", {}))
        wh_cfg = cfg.get("warehouse_api") or {}
        if wh_cfg.get("enabled"):
            warehouse_id = fetch_warehouse_id(
                url=wh_cfg["url"],
                params=wh_cfg.get("params", {}),
                headers=wh_cfg.get("headers", {}),
                timeout=wh_cfg.get("timeout_seconds", 30),
                id_path=wh_cfg["id_path"],
            )
            params["warehouseid"] = warehouse_id
        raw = fetch(
            url=api["url"],
            params=params,
            timeout=api.get("timeout_seconds", 30),
            headers=api.get("headers", {}),
        )
        prices = parse_prices(raw)
        write_record(
            path=data_path,
            name=params.get("warehouseid", "unknown"),
            prices=prices,
            raw=raw if output.get("include_raw_json") else None,
        )
        write_separator(data_path)


def _sleep_responsive(seconds: float) -> None:
    # Short chunks so Ctrl+C / SIGTERM don't wait the full interval.
    end_at = time.monotonic() + seconds
    while not _should_stop and time.monotonic() < end_at:
        time.sleep(min(1.0, end_at - time.monotonic()))


def main() -> int:
    config_path = ROOT / "config.yaml"
    cfg = load_config(config_path)
    setup_logger(cfg["logging"]["level"], cfg["logging"]["format"])
    log.info("Starting gas price logger (config=%s)", config_path)

    signal.signal(signal.SIGINT, _handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_signal)

    interval = cfg["schedule"]["interval_seconds"]
    while not _should_stop:
        start = time.monotonic()
        try:
            run_once(cfg)
        except Exception:
            log.exception("Iteration failed; will retry next interval")

        if _should_stop:
            break

        remaining = max(1.0, interval - (time.monotonic() - start))
        log.info("Sleeping %.0fs until next run", remaining)
        _sleep_responsive(remaining)

    log.info("Exited cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
