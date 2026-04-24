# gasUpdaterLogger

A long-running Python service that polls the Costco gas price API on an
interval and appends the prices to a text file. Designed to be started once
on a VM and left running until manually stopped.

## Layout

```
gasUpdaterLogger/
├── config.yaml           # all runtime settings (API URL, interval, paths, log level)
├── requirements.txt      # requests, PyYAML
├── Dockerfile            # python:3.12-slim image, non-root user
├── docker-compose.yml    # build + run with host-mounted config.yaml and data/
├── .dockerignore
├── data/
│   └── gas_prices.txt    # output data file (created on first run)
└── src/
    ├── main.py           # pipeline orchestrator + forever loop + signal handling
    ├── config_loader.py  # loads config.yaml
    ├── warehouse_id.py   # (optional) resolve warehouseid from a separate API
    ├── fetcher.py        # GET request to the gas price API, returns parsed JSON
    ├── price_parser.py   # extracts price-looking fields from the JSON payload
    ├── writer.py         # appends a timestamped record to the data file
    └── logger_setup.py   # configures the root logger to stdout
```

`main.py` is the pipeline: for each iteration it calls
`(optional warehouse-id lookup) -> fetch -> parse_prices -> write_record`,
then sleeps `interval_seconds`. Exceptions in any stage are logged and the
loop continues.

## Running

```bash
pip install -r requirements.txt
python src/main.py
```

Stop with Ctrl+C (or `kill <pid>` — SIGTERM is handled). The loop finishes
the current iteration's sleep in ~1s chunks so shutdown is responsive.

For unattended operation on a VM, run under `tmux`/`screen`, `nohup`, a
systemd unit, or Task Scheduler — nothing in the service assumes a specific
supervisor.

## Configuration

Everything configurable lives in [config.yaml](config.yaml). Common edits:

- `api.params.warehouseid` — change the Costco warehouse (ignored when
  `warehouse_api.enabled: true` — see next bullet).
- `warehouse_api.*` — when `enabled: true`, each iteration first calls this
  URL, digs into the JSON at `id_path` (dotted, supports list indices like
  `warehouses.0.id`), and uses that value as the `warehouseid` param on the
  gas price call. Leave `enabled: false` until your ID endpoint is live.
- `schedule.interval_seconds` — polling cadence. Default `3600` (1 hour).
- `output.data_file` — where price records are appended. Relative paths
  resolve from the project root.
- `output.include_raw_json` — set `true` to also dump the full API payload
  on each line (useful if the parser isn't extracting a field you expect).
- `logging.level` — `DEBUG`, `INFO`, `WARNING`, `ERROR`.

Changes require a restart.

## Output format

Each line in `gas_prices.txt` looks like:

```
[2026-04-23T18:00:05+00:00] regular=3.79, premium=4.29
```

With `include_raw_json: true`, the raw JSON is appended after ` | raw=`.

If `price_parser.py` doesn't find any price-looking keys in the payload, the
line is written with `(no prices extracted)` — inspect the raw JSON (enable
the flag above) and extend `PRICE_KEY_HINTS` in `src/price_parser.py` to
match the actual field names.

## Logging

Console-only, via the stdlib `logging` module. The operational log
(fetching, sleep intervals, errors) goes to stdout; the gas-price *data*
goes to `gas_prices.txt` via `writer.py`. These are intentionally separate:
one stream for humans watching the service, one file for later review.
