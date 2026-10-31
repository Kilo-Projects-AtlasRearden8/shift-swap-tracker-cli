"""Command-line interface for the shift swap tracker."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from . import __version__
from .balance import compute_balances, compute_net_hours
from .dates import normalize_date, parse_date
from .models import Person, Request, Store, Swap
from .storage import DEFAULT_DATA_FILE, ensure_store, load_store, save_store


def _add_data_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--data",
        default=DEFAULT_DATA_FILE,
        help="Path to the JSON data file (default: %(default)s)",
    )


def _load(path: str) -> Store:
    return load_store(path)


def _save(store: Store, path: str) -> None:
    save_store(store, path)


def cmd_init(args: argparse.Namespace) -> int:
    store = ensure_store(args.data)
    print(f"Initialized {args.data}")
    return 0


def cmd_add_person(args: argparse.Namespace) -> int:
    store = _load(args.data)
    if any(p.name == args.name for p in store.people):
        print(f"error: person {args.name!r} already exists", file=sys.stderr)
        return 1
    store.people.append(Person(name=args.name, target_hours=args.target_hours))
    _save(store, args.data)
    print(f"Added {args.name} (target {args.target_hours}h)")
    return 0


def cmd_swap(args: argparse.Namespace) -> int:
    store = _load(args.data)
    date = normalize_date(args.date)
    if args.giver == args.receiver:
        print("error: giver and receiver must differ", file=sys.stderr)
        return 1
    if args.hours <= 0:
        print("error: hours must be positive", file=sys.stderr)
        return 1
    store.swaps.append(
        Swap(date=date, giver=args.giver, receiver=args.receiver, hours=args.hours, note=args.note or "")
    )
    _save(store, args.data)
    print(f"Recorded swap: {args.giver} -> {args.receiver} on {date} ({args.hours}h)")
    return 0


def cmd_request(args: argparse.Namespace) -> int:
    store = _load(args.data)
    date = normalize_date(args.date)
    if args.hours <= 0:
        print("error: hours must be positive", file=sys.stderr)
        return 1
    store.requests.append(
        Request(date=date, owner=args.owner, hours=args.hours, note=args.note or "")
    )
    _save(store, args.data)
    print(f"Recorded coverage request: {args.owner} on {date} ({args.hours}h)")
    return 0


def cmd_balance(args: argparse.Namespace) -> int:
    store = _load(args.data)
    balances = compute_balances(
        store, start=args.start, end=args.end, names=args.names
    )
    if not balances:
        print("No balances to show. Add people and swaps first.")
        return 0
    print(f"{'Name':<16}{'Target':>10}{'Earned':>10}{'Balance':>10}")
    for name in sorted(balances):
        b = balances[name]
        print(f"{name:<16}{b.target:>10.2f}{b.earned:>10.2f}{b.balance:>10.2f}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    store = _load(args.data)
    if store.swaps:
        print("Swaps:")
        for s in store.swaps:
            print(f"  {s.date}  {s.giver} -> {s.receiver}  {s.hours}h  {s.note}")
    else:
        print("No swaps recorded.")
    if store.requests:
        print("Coverage requests:")
        for r in store.requests:
            extra = f" covered by {r.covered_by}" if r.covered_by else ""
            print(f"  {r.date}  {r.owner}  {r.hours}h  [{r.status}]{extra}  {r.note}")
    else:
        print("No coverage requests recorded.")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    store = _load(args.data)
    out = Path(args.out)
    if args.format == "json":
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            __import__("json").dumps(store.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Exported JSON to {out}")
        return 0
    if args.format == "csv":
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["type", "date", "from", "to", "hours", "note", "status", "covered_by"])
            for s in store.swaps:
                writer.writerow(["swap", s.date, s.giver, s.receiver, s.hours, s.note, "", ""])
            for r in store.requests:
                writer.writerow(
                    ["request", r.date, "", r.owner, r.hours, r.note, r.status, r.covered_by or ""]
                )
        print(f"Exported CSV to {out}")
        return 0
    print(f"error: unknown format {args.format!r}", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="shift-swap-tracker",
        description="Log shift swaps, coverage requests, and balance hours.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="Create the local JSON store.")
    _add_data_arg(p)
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add-person", help="Add a coworker.")
    _add_data_arg(p)
    p.add_argument("--name", required=True)
    p.add_argument("--target-hours", type=float, default=40.0)
    p.set_defaults(func=cmd_add_person)

    p = sub.add_parser("swap", help="Record a shift swap.")
    _add_data_arg(p)
    p.add_argument("--date", required=True)
    p.add_argument("--giver", required=True)
    p.add_argument("--receiver", required=True)
    p.add_argument("--hours", type=float, required=True)
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_swap)

    p = sub.add_parser("request", help="Record a coverage request.")
    _add_data_arg(p)
    p.add_argument("--date", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--hours", type=float, required=True)
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_request)

    p = sub.add_parser("balance", help="Show per-person hour balances.")
    _add_data_arg(p)
    p.add_argument("--start", default=None)
    p.add_argument("--end", default=None)
    p.add_argument("--names", nargs="*", default=None)
    p.set_defaults(func=cmd_balance)

    p = sub.add_parser("list", help="List all swaps and requests.")
    _add_data_arg(p)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("export", help="Export data to JSON or CSV.")
    _add_data_arg(p)
    p.add_argument("--format", choices=["json", "csv"], default="csv")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_export)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())