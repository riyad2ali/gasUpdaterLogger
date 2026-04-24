# gasUpdaterLogger

A Python service that polls the Costco gas price API on an interval and
appends the prices to a text file. Runs until you stop it.

## Run

1. Install dependencies (one-time):
   ```bash
   pip install -r requirements.txt
   ```

2. Start the service from the project root:
   ```bash
   python src/main.py
   ```

3. Stop it with **Ctrl+C** (or `kill <pid>` — SIGTERM is handled). Shutdown
   finishes within ~1 second.

Output is appended to `gas_prices.txt` in the project root, one line per
hour:

```
[2026-04-24T18:00:05+00:00] premium=3.789, regular=3.099
```

Operational messages (fetching, errors, sleep intervals) go to the console.

## Run unattended on a VM

Pick whichever fits your VM — the service doesn't assume any specific
supervisor:

- **tmux / screen**: `tmux new -s gas` then `python src/main.py`, detach
  with `Ctrl+b d`. Reattach with `tmux attach -t gas`.
- **nohup** (Linux): `nohup python src/main.py > service.log 2>&1 &`
- **systemd** (Linux): create a unit file that runs
  `ExecStart=/usr/bin/python /path/to/gasUpdaterLogger/src/main.py` with
  `Restart=always`.
- **Task Scheduler** (Windows): create a task that runs
  `python.exe D:\...\gasUpdaterLogger\src\main.py` at startup.

## Configure

Everything lives in [config.yaml](config.yaml). Common edits:

- `schedule.interval_seconds` — polling cadence (default `3600` = 1 hour).
- `api.params.warehouseid` — which Costco warehouse to poll.
- `warehouse_api.enabled` — set `true` to fetch the warehouseid from a
  separate endpoint each iteration (see [CLAUDE.md](CLAUDE.md) for details).
- `output.data_file` — where price records are appended.
- `logging.level` — `DEBUG`, `INFO`, `WARNING`, `ERROR`.

Changes require a restart. See [CLAUDE.md](CLAUDE.md) for the full project
layout and pipeline details.
