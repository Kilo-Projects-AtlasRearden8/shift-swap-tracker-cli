"""Tests for balance logic."""

from shiftswap.balance import compute_balances, compute_net_hours, total_hours
from shiftswap.models import Person, Request, Store, Swap


def _store_with_swaps():
    return Store(
        people=[Person(name="Alice", target_hours=40.0), Person(name="Bob", target_hours=40.0)],
        swaps=[
            Swap(date="2026-11-01", giver="Bob", receiver="Alice", hours=8.0, note="Sunday"),
            Swap(date="2026-11-02", giver="Alice", receiver="Bob", hours=8.0, note="Monday"),
        ],
    )


def _store_with_requests():
    return Store(
        people=[Person(name="Alice", target_hours=40.0), Person(name="Bob", target_hours=40.0)],
        requests=[
            Request(
                date="2026-11-01",
                owner="Alice",
                hours=8.0,
                status="closed",
                covered_by="Bob",
            )
        ],
    )


class TestComputeBalances:
    def test_swap_receiver_gains_giver_loses(self):
        store = _store_with_swaps()
        balances = compute_balances(store)
        assert balances["Alice"].earned == 0.0
        assert balances["Alice"].balance == -40.0
        assert balances["Bob"].earned == 0.0
        assert balances["Bob"].balance == -40.0

    def test_single_swap(self):
        store = Store(
            people=[Person(name="Alice", target_hours=40.0), Person(name="Bob", target_hours=40.0)],
            swaps=[Swap(date="2026-11-01", giver="Bob", receiver="Alice", hours=8.0)],
        )
        balances = compute_balances(store)
        assert balances["Alice"].earned == 8.0
        assert balances["Alice"].balance == -32.0
        assert balances["Bob"].earned == -8.0
        assert balances["Bob"].balance == -48.0

    def test_unknown_person_defaults_to_40(self):
        store = Store(
            swaps=[Swap(date="2026-11-01", giver="Bob", receiver="Carol", hours=8.0)]
        )
        balances = compute_balances(store)
        assert balances["Carol"].target == 40.0
        assert balances["Carol"].earned == 8.0

    def test_date_range_filter(self):
        store = _store_with_swaps()
        balances = compute_balances(store, start="2026-11-02", end="2026-11-02")
        assert balances["Alice"].earned == -8.0
        assert balances["Bob"].earned == 8.0

    def test_names_filter(self):
        store = _store_with_swaps()
        balances = compute_balances(store, names=["Alice"])
        assert set(balances) == {"Alice"}

    def test_closed_request_flow(self):
        store = _store_with_requests()
        balances = compute_balances(store)
        # Alice got covered (-8), Bob covered her (+8)
        assert balances["Alice"].earned == -8.0
        assert balances["Bob"].earned == 8.0

    def test_open_request_ignored(self):
        store = Store(
            people=[Person(name="Alice", target_hours=40.0)],
            requests=[
                Request(date="2026-11-01", owner="Alice", hours=8.0, status="open")
            ],
        )
        balances = compute_balances(store)
        assert balances["Alice"].earned == 0.0


class TestComputeNetHours:
    def test_net_for_single_person(self):
        store = _store_with_swaps()
        assert compute_net_hours(store, "Alice") == 0.0


class TestTotalHours:
    def test_sum_of_swap_hours(self):
        store = _store_with_swaps()
        assert total_hours(store) == 16.0

    def test_date_range_filter(self):
        store = _store_with_swaps()
        assert total_hours(store, start="2026-11-01", end="2026-11-01") == 8.0