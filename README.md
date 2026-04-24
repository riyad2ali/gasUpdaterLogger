# gasUpdaterLogger

A Python service that polls the Costco gas price API on an interval and
appends the prices to a text file. Runs until you stop it.

Output goes to `data/gas_prices.txt`, one line per hour:

```
[2026-04-24T18:00:05+00:00] premium=3.789, regular=3.099
```

Operational messages (fetching, errors, sleep intervals) go to the console
(or to `docker logs` when containerized).

---

## Run with Docker (recommended for the VM)

### With docker compose

From the project root:

```bash
docker compose up -d --build
```

That builds the image, starts the container in the background, and
auto-restarts it unless you explicitly stop it.

**View logs:**
```bash
docker compose logs -f
```

**View the price data file** (on the host):
```bash
cat data/gas_prices.txt
```

**Stop the service:**
```bash
docker compose down
```

**Apply config changes:**
Edit [config.yaml](config.yaml), then:
```bash
docker compose restart
```

**Rebuild after code changes:**
```bash
docker compose up -d --build
```

### With plain docker (no compose)

```bash
docker build -t gas-updater-logger .

docker run -d \
  --name gas-updater-logger \
  --restart unless-stopped \
  -v "$(pwd)/config.yaml:/app/config.yaml:ro" \
  -v "$(pwd)/data:/app/data" \
  gas-updater-logger
```

Then `docker logs -f gas-updater-logger` to follow output, and
`docker stop gas-updater-logger && docker rm gas-updater-logger` to stop.

### What the volumes do

- `./config.yaml:/app/config.yaml:ro` — you edit config on the host; the
  container reads it at startup. Restart the container to apply changes.
- `./data:/app/data` — where price records are written. Survives rebuilds
  and container removal.

---

## Run natively (without Docker)

1. Install dependencies (one-time):
   ```bash
   pip install -r requirements.txt
   ```

2. Start the service from the project root:
   ```bash
   python src/main.py
   ```

3. Stop it with **Ctrl+C** (or `kill <pid>` — SIGTERM is handled).

For unattended operation without Docker, run under tmux/screen, `nohup`,
systemd, or Task Scheduler.

---

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
