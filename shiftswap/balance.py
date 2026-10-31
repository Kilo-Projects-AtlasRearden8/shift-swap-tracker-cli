"""Balance computation logic.

A person's *earned* hours are computed from recorded swaps and coverage
requests:

- A swap ``giver -> receiver`` for ``h`` hours means the receiver worked the
  shift (+h) and the giver did not (-h).
- A *closed* coverage request means the owner did not work (-h) and the person
  who covered it did (+h).

Balance = earned - target. A positive balance means the person is ahead of
their target; negative means behind.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .dates import parse_date
from .models import Store


@dataclass
class Balance:
    name: str
    target: float
    earned: float
    balance: float

    @property
    def is_ahead(self) -> bool:
        return self.balance > 0

    @property
    def is_behind(self) -> bool:
        return self.balance < 0

    @property
    def is_on_track(self) -> bool:
        return self.balance == 0


def _in_range(date_str: str, start: Optional[str], end: Optional[str]) -> bool:
    if start is not None and parse_date(date_str) < parse_date(start):
        return False
    if end is not None and parse_date(date_str) > parse_date(end):
        return False
    return True


def compute_balances(
    store: Store,
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
    names: Optional[List[str]] = None,
) -> Dict[str, Balance]:
    """Compute per-person balances, optionally filtered by date range and names."""
    target_map = {p.name: p.target_hours for p in store.people}
    earned: Dict[str, float] = {p.name: 0.0 for p in store.people}

    def ensure(name: str) -> None:
        if name not in earned:
            earned[name] = 0.0
            if name not in target_map:
                target_map[name] = 40.0

    for swap in store.swaps:
        if not _in_range(swap.date, start, end):
            continue
        ensure(swap.giver)
        ensure(swap.receiver)
        earned[swap.giver] -= swap.hours
        earned[swap.receiver] += swap.hours

    for req in store.requests:
        if not _in_range(req.date, start, end):
            continue
        if req.status != "closed" or not req.covered_by:
            continue
        ensure(req.owner)
        ensure(req.covered_by)
        earned[req.owner] -= req.hours
        earned[req.covered_by] += req.hours

    if names is not None:
        wanted = set(names)
        earned = {n: v for n, v in earned.items() if n in wanted}
        for n in wanted:
            ensure(n)

    result: Dict[str, Balance] = {}
    for name, value in earned.items():
        target = target_map.get(name, 40.0)
        result[name] = Balance(
            name=name, target=target, earned=value, balance=value - target
        )
    return result


def compute_net_hours(
    store: Store,
    name: str,
    *,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> float:
    """Return the net earned hours for a single person over a date range."""
    balances = compute_balances(store, start=start, end=end, names=[name])
    return balances[name].earned


def total_hours(store: Store, *, start: Optional[str] = None, end: Optional[str] = None) -> float:
    """Return the sum of all swap hours recorded in a date range."""
    return sum(
        s.hours for s in store.swaps if _in_range(s.date, start, end)
    )