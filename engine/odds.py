"""Phase 2A1 / 2A2 / 2B / 2C decision tree.

MOE Phase 2C priority order (within Phase 2C, when balloting is needed):

    1. SC <1km    2. SC 1-2km    3. SC >2km
    4. PR <1km    5. PR 1-2km    6. PR >2km

The "indicator" field on each year names the *one* group that had to
ballot for the last seats. Everyone in a higher-priority group got in
automatically; everyone in a lower-priority group got nothing.

Reasoning translation:

    Indicator    → my-bucket outcome
    ─────────────────────────────────────────────────────────
    (undersub)   → walk in (everyone got a seat)
    PR<1         → if me=PR<1km: ballot. else walk in (PR<1km) or shut out (PR1-2/>2)
    PR1-2        → if me=PR1-2: ballot. PR<1km walks. PR>2 shut out.
    PR>2         → if me=PR>2: ballot. PR<1 / PR1-2 walked.
    SC<1         → SC<1 balloted; all PR shut out.
    SC1-2        → SC<1 walked; SC1-2 balloted; SC>2 + PR all shut out.
    SC>2         → SC<=2 walked; SC>2 balloted; PR shut out.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .profile import School, UserProfile


OddsBand = Literal["high", "medium", "low", "blocked"]
EntryPhase = Literal["2A1", "2A2", "2B", "2C", "ineligible"]


@dataclass
class ScenarioTweak:
    label: str           # e.g. "If you move within 1km of this school"
    delta_pct: int       # +/- percentage points change to odds
    notes: str = ""


@dataclass
class SchoolOdds:
    school_slug: str
    school_name: str
    distance_km: float | None
    distance_band: Literal["<1km", "1-2km", ">2km", "unknown"]
    entry_phase_estimated: EntryPhase
    odds_pct: int
    odds_band: OddsBand
    historical_indicator_latest: str
    historical_year: int
    projected_indicator: dict[int, str] = field(default_factory=dict)
    confidence: Literal["high", "medium", "low"] = "medium"
    reasoning: list[str] = field(default_factory=list)
    scenario_tweaks: list[ScenarioTweak] = field(default_factory=list)
    blocked_reason: str | None = None


def distance_band(km: float | None) -> Literal["<1km", "1-2km", ">2km", "unknown"]:
    if km is None:
        return "unknown"
    if km < 1.0:
        return "<1km"
    if km <= 2.0:
        return "1-2km"
    return ">2km"


def _band_to_2c_bucket(citizenship: str, dist_band: str) -> str | None:
    """Map (citizenship, distance band) to Phase 2C bucket name."""
    if citizenship == "Foreigner":
        return None
    prefix = "SC" if citizenship == "SC" else "PR"
    if dist_band == "<1km":
        return f"{prefix}<1"
    if dist_band == "1-2km":
        return f"{prefix}1-2"
    if dist_band == ">2km":
        return f"{prefix}>2"
    return None


_PRIORITY_ORDER = ["SC<1", "SC1-2", "SC>2", "PR<1", "PR1-2", "PR>2"]


def _phase_2c_outcome(my_bucket: str | None, indicator: str) -> tuple[OddsBand, int, str]:
    """Return (band, odds_pct, rationale) for Phase 2C with given indicator."""
    if my_bucket is None:
        return "blocked", 0, "Foreigners are not eligible for Phase 2C."

    ind = (indicator or "").strip()
    if not ind:
        return "high", 95, "School was undersubscribed — everyone in Phase 2C got a seat."

    if ind not in _PRIORITY_ORDER:
        return "medium", 50, f"Indicator {ind!r} not recognised; defaulting to medium."

    my_rank = _PRIORITY_ORDER.index(my_bucket)
    ind_rank = _PRIORITY_ORDER.index(ind)

    if my_rank < ind_rank:
        return "high", 95, (
            f"Your group ({my_bucket}) ranks above the balloted group ({ind}). "
            f"You would have walked in."
        )
    if my_rank > ind_rank:
        return "blocked", 0, (
            f"Your group ({my_bucket}) ranks below the balloted group ({ind}). "
            f"All seats filled before your bucket — you would have been shut out."
        )
    # equal — actually ballot
    return "medium", 50, (
        f"Your group ({my_bucket}) was the one that balloted. Outcome depends on "
        f"how many in your bucket applied versus seats remaining."
    )


def compute_odds(
    profile: UserProfile,
    school: School,
    ballot_history: dict[str, dict],
    distance_km: float | None,
    latest_year: int = 2025,
) -> SchoolOdds:
    """Compute current-year-equivalent odds for one school under one profile."""
    reasoning: list[str] = []
    tweaks: list[ScenarioTweak] = []

    # 0. Gender compatibility short-circuit
    if not school.is_gender_compatible(profile.gender):
        return SchoolOdds(
            school_slug=school.slug, school_name=school.name,
            distance_km=distance_km, distance_band=distance_band(distance_km),
            entry_phase_estimated="ineligible",
            odds_pct=0, odds_band="blocked",
            historical_indicator_latest="",
            historical_year=latest_year,
            confidence="high",
            reasoning=[f"This school is {school.gender}-only; your child's gender excludes admission."],
            blocked_reason="gender",
        )

    # 1. Phase 2A1 (sibling / parent alum) — near-certain entry
    if profile.has_2a1(school.slug):
        return SchoolOdds(
            school_slug=school.slug, school_name=school.name,
            distance_km=distance_km, distance_band=distance_band(distance_km),
            entry_phase_estimated="2A1",
            odds_pct=99, odds_band="high",
            historical_indicator_latest="",
            historical_year=latest_year,
            confidence="high",
            reasoning=[
                "You qualify for Phase 2A1 (sibling currently in this school, or parent is an alumnus).",
                "Phase 2A1 places typically suffice for all applicants in this bucket.",
            ],
        )

    # 2. Phase 2A2 (staff)
    if profile.has_2a2(school.slug):
        return SchoolOdds(
            school_slug=school.slug, school_name=school.name,
            distance_km=distance_km, distance_band=distance_band(distance_km),
            entry_phase_estimated="2A2",
            odds_pct=95, odds_band="high",
            historical_indicator_latest="",
            historical_year=latest_year,
            confidence="high",
            reasoning=[
                "You qualify for Phase 2A2 (parent is staff at this school or MOE staff).",
                "Phase 2A2 places almost always suffice.",
            ],
        )

    # 3. Phase 2B (PVP 40+ hrs, clan, or affiliated religion)
    if profile.has_2b(school.slug, school.religion, None):
        reasoning.append(
            "You qualify for Phase 2B (parent volunteer 40+ hours, clan/religion affiliation). "
            "Phase 2B reserves ~20 seats; balloting may apply within this bucket."
        )
        # Phase 2B base odds: depends on school popularity, but typically high
        odds_2b = 75
        return SchoolOdds(
            school_slug=school.slug, school_name=school.name,
            distance_km=distance_km, distance_band=distance_band(distance_km),
            entry_phase_estimated="2B",
            odds_pct=odds_2b, odds_band="high",
            historical_indicator_latest="",
            historical_year=latest_year,
            confidence="medium",
            reasoning=reasoning,
        )

    # 4. Phase 2C — fall-through path for most parents
    yearmap = ballot_history.get(school.slug, {})
    latest = yearmap.get(str(latest_year)) or {}
    indicator = latest.get("sc_indicator", "")
    my_bucket = _band_to_2c_bucket(profile.citizenship, distance_band(distance_km))

    band, odds_pct, why = _phase_2c_outcome(my_bucket, indicator)
    reasoning.append(why)

    if my_bucket and indicator and my_bucket == indicator and latest.get("ballot_chance_pct"):
        # We have a real bucket-specific probability from MOE
        odds_pct = int(latest["ballot_chance_pct"])
        band = "medium" if 30 <= odds_pct <= 70 else ("high" if odds_pct > 70 else "low")
        reasoning.append(
            f"MOE-published ballot chance for {indicator} in {latest_year}: {odds_pct}%."
        )

    # Scenario tweaks (counterfactual hints)
    if profile.citizenship == "PR" and distance_band(distance_km) != "<1km":
        tweaks.append(ScenarioTweak(
            label="If you move within 1km of this school",
            delta_pct=20,
            notes="Moves you up the Phase 2C priority ladder (PR1-2 → PR<1km).",
        ))

    return SchoolOdds(
        school_slug=school.slug, school_name=school.name,
        distance_km=distance_km, distance_band=distance_band(distance_km),
        entry_phase_estimated="2C",
        odds_pct=odds_pct, odds_band=band,
        historical_indicator_latest=indicator,
        historical_year=latest_year,
        confidence="medium",
        reasoning=reasoning,
        scenario_tweaks=tweaks,
    )
