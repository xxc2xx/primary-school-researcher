"""User profile and request models for the odds engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Citizenship = Literal["SC", "PR", "Foreigner"]
Gender = Literal["male", "female"]


@dataclass(frozen=True)
class UserProfile:
    citizenship: Citizenship
    gender: Gender
    target_year: int                # P1 year (e.g. 2027)
    postal_code: str                # 6-digit SG postal, can be empty for "no address yet"
    # Phase 2A1 — sibling currently in the school OR parent is an alum
    sibling_in_school_slugs: list[str] = field(default_factory=list)
    parent_alumni_school_slugs: list[str] = field(default_factory=list)
    # Phase 2A2 — staff
    parent_staff_school_slugs: list[str] = field(default_factory=list)
    moe_staff: bool = False
    # Phase 2B — PVP (40+ volunteer hours), clan, religion
    parent_volunteer_school_slugs: list[str] = field(default_factory=list)
    clan_affiliation: list[str] = field(default_factory=list)
    religious_affiliation: list[str] = field(default_factory=list)
    # Search scope
    target_school_slugs: list[str] = field(default_factory=list)
    radius_km: float = 2.0

    def has_2a1(self, slug: str) -> bool:
        return slug in self.sibling_in_school_slugs or slug in self.parent_alumni_school_slugs

    def has_2a2(self, slug: str) -> bool:
        return slug in self.parent_staff_school_slugs or self.moe_staff

    def has_2b(self, slug: str, school_religion: str | None, school_clan: str | None) -> bool:
        if slug in self.parent_volunteer_school_slugs:
            return True
        if school_religion and school_religion in self.religious_affiliation:
            return True
        if school_clan and school_clan in self.clan_affiliation:
            return True
        return False


@dataclass(frozen=True)
class School:
    slug: str
    name: str
    town: str
    planning_area: str
    gender: str                       # "co-ed" / "male" / "female"
    religion: str | None
    affiliated_secondary: str | None
    gep_former_9: bool
    module_host_2024: bool
    lat: float | None = None
    lng: float | None = None
    address: str | None = None

    @classmethod
    def from_dict(cls, d: dict) -> "School":
        return cls(
            slug=d["slug"], name=d["name"], town=d["town"],
            planning_area=d.get("planning_area") or d["town"],
            gender=d.get("gender") or "co-ed",
            religion=d.get("religion"),
            affiliated_secondary=d.get("affiliated_secondary"),
            gep_former_9=bool(d.get("gep_former_9")),
            module_host_2024=bool(d.get("module_host_2024")),
            lat=d.get("lat"),
            lng=d.get("lng"),
            address=d.get("address"),
        )

    def is_gender_compatible(self, profile_gender: Gender) -> bool:
        return self.gender == "co-ed" or self.gender == profile_gender
