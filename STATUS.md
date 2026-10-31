# STATUS

## What was built

`shift-swap-tracker-cli` — a local-first Python CLI for shift workers to log
shift swaps, coverage requests, and balance hours, with local JSON storage and
CSV export. Built entirely from the standard library (no external runtime
dependencies, no API keys, no network access, no personal data collected).

Package: `shiftswap/`
- `models.py` — Person, Swap, Request, Store dataclasses with JSON serialization
- `storage.py` — local JSON load/save/ensure (`shifts.json` by default)
- `dates.py` — date parsing/validation/normalization, week bounds, date ranges,
  period dates (day/week/month), day arithmetic
- `balance.py` — per-person earned hours vs. target, balance = earned − target,
  with optional date-range and name filtering
- `cli.py` — argparse CLI: init, add-person, swap, request, balance, list,
  export (json/csv)
- `__init__.py` — version

Tests: `tests/test_dates.py` and `tests/test_balance.py` (36 tests).

Other files:
- `pyproject.toml` — project metadata, console script `shift-swap-tracker`,
  pytest config, optional test dependency
- `LICENSE` — MIT, copyright line exactly `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — usage, quick start, command table, credits Asdale Dynamics, LLC
- `.gitignore` — excludes runtime data (`shifts.json`, exports), caches
- `.git/` — initialized, one commit (identity: Dylan Asdale, no co-author
  trailers, never pushed, no remote)

## How to run it

From the project folder:

```bash
# Make the package importable (or `pip install -e .`)
export PYTHONPATH="."

# Initialize the local JSON store
python3 -c 'from shiftswap.cli import main; import sys; sys.exit(main(["init"]))'

# Add coworkers
python3 -c 'from shiftswap.cli import main; import sys; sys.exit(main(["add-person","--name","Alice","--target-hours","40"]))'
python3 -c 'from shiftswap.cli import main; import sys; sys.exit(main(["add-person","--name","Bob","--target-hours","40"]))'

# Record a shift swap (Bob gives his shift to Alice, 8h)
python3 -c 'from shiftswap.cli import main; import sys; sys.exit(main(["swap","--date","2026-11-01","--giver","Bob","--receiver","Alice","--hours","8","--note","Sunday"]))'

# Record a coverage request
python3 -c 'from shiftswap.cli import main; import sys; sys.exit(main(["request","--date","2026-11-05","--owner","Alice","--hours","8","--note","coverage"]))'

# Show balances
python3 -c 'from shiftswap.cli import main; import sys; sys.exit(main(["balance"]))'

# Export to CSV
python3 -c 'from shiftswap.cli import main; import sys; sys.exit(main(["export","--format","csv","--out","shifts.csv"]))'
```

If installed (`pip install -e .`), use the `shift-swap-tracker` command directly.

## Verification results

- `python3 -m py_compile shiftswap/*.py tests/*.py` → compile OK
- `python3 -m pytest -q` → **36 passed** (date logic + balance logic)
- CLI end-to-end workflow (init → add-person → swap → request → list → balance → export json/csv) → all commands run successfully
- LICENSE copyright line confirmed exactly: `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC
- Secret/personal-data scan: clean (no API keys, secrets, emails, phones in source)
- No `.github/workflows` files present
- Git initialized, one plain commit, identity Dylan Asdale, no co-author
  trailers, never pushed, no remote created

## Known gaps

- No test coverage yet for the CLI layer itself (tests cover dates and balance
  logic only, as specified). CLI behavior was verified manually end-to-end.
- Balance treats each swap/request independently and does not enforce that a
  swap's two shifts are reciprocal; imbalances are reflected in the net balance.
- Coverage requests only affect balance when `status == "closed"` and a
  `covered_by` person is set; open requests are tracked but ignored in balance.
- Default data file is `./shifts.json` relative to the working directory; there
  is no OS-specific data dir (e.g. `~/.local/share`) by design to keep it
  local-first and portable.
- No packaging to PyPI / no release automation (intentionally not published).