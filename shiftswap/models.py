"""Data models for the shift swap tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Person:
    name: str
    target_hours: float = 40.0

    def to_dict(self) -> dict:
        return {"name": self.name, "target_hours": self.target_hours}

    @classmethod
    def from_dict(cls, data: dict) -> "Person":
        return cls(name=data["name"], target_hours=float(data.get("target_hours", 40.0)))


@dataclass
class Swap:
    date: str
    giver: str
    receiver: str
    hours: float
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "giver": self.giver,
            "receiver": self.receiver,
            "hours": self.hours,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Swap":
        return cls(
            date=data["date"],
            giver=data["giver"],
            receiver=data["receiver"],
            hours=float(data["hours"]),
            note=data.get("note", ""),
        )


@dataclass
class Request:
    date: str
    owner: str
    hours: float
    note: str = ""
    status: str = "open"  # "open" or "closed"
    covered_by: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "owner": self.owner,
            "hours": self.hours,
            "note": self.note,
            "status": self.status,
            "covered_by": self.covered_by,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Request":
        return cls(
            date=data["date"],
            owner=data["owner"],
            hours=float(data["hours"]),
            note=data.get("note", ""),
            status=data.get("status", "open"),
            covered_by=data.get("covered_by"),
        )


@dataclass
class Store:
    people: List[Person] = field(default_factory=list)
    swaps: List[Swap] = field(default_factory=list)
    requests: List[Request] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "people": [p.to_dict() for p in self.people],
            "swaps": [s.to_dict() for s in self.swaps],
            "requests": [r.to_dict() for r in self.requests],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Store":
        return cls(
            people=[Person.from_dict(p) for p in data.get("people", [])],
            swaps=[Swap.from_dict(s) for s in data.get("swaps", [])],
            requests=[Request.from_dict(r) for r in data.get("requests", [])],
        )