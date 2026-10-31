# Shift Swap Tracker CLI

A small, local-first command-line tool for shift workers to log shift swaps,
coverage requests, and balance hours. Stores everything in a local JSON file
(no network, no API keys, no personal data collected) and can export to CSV.

Built by [Asdale Dynamics, LLC](https://github.com/dylanasdale) — beginner-friendly
AI education, books and guides, and practical tools that the LLC can publish or sell.

## Who this is for

Shift workers who rotate schedules and need a simple, private way to track who
covered whom and whether they are ahead or behind on hours. No accounts, no
cloud, no tracking. Just a JSON file on your machine and a few commands.

## Features

- Log shift swaps between coworkers.
- Log coverage requests (someone to cover your shift).
- Balance hours: see whether you are ahead or behind your target hours.
- Local JSON storage (default `./shifts.json`).
- Export to CSV.
- Date and balance logic covered by tests.

## Installation

```bash
pip install -e .
```

Or run directly from a checkout:

```bash
python -m shiftswap --help
```

## Quick start

```bash
# Initialize a new tracker
shift-swap-tracker init

# Add a coworker
shift-swap-tracker add-person --name Alice --target-hours 40
shift-swap-tracker add-person --name Bob --target-hours 40

# Log a swap: Alice covers Bob's shift on 2026-11-01 (Alice gains 8h, Bob loses 8h)
shift-swap-tracker swap --date 2026-11-01 --giver Bob --receiver Alice --hours 8 --note "Sunday shift"

# Request coverage
shift-swap-tracker request --date 2026-11-05 --owner Alice --hours 8 --note "Need coverage"

# Show balances
shift-swap-tracker balance

# Export to CSV
shift-swap-tracker export --format csv --out shifts.csv
```

## Commands

| Command | Description |
| --- | --- |
| `init` | Create the local JSON store if it does not exist. |
| `add-person` | Add a coworker with a target weekly hours value. |
| `swap` | Record a shift swap between two people. |
| `request` | Record a coverage request. |
| `balance` | Show per-person hour balance vs. target. |
| `list` | List all recorded swaps and requests. |
| `export` | Export data to JSON or CSV. |

## Data file

By default data is stored in `./shifts.json`. Use `--data` to use a different file.

## Testing

```bash
pip install -e .
pytest -q
```

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.