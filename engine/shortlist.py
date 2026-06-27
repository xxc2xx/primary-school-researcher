"""Rank a list of schools for one user profile.

Composes profile.School, odds.compute_odds, and projection.project_indicators
into a single sorted shortlist.
"""
from __future__ import annotations

import json
from pathlib import Path

from .distance import get_distance_km
from .odds import SchoolOdds, compute_odds
from .profile import School, UserProfile
from .projection import project_indicators


ROOT = Path(__file__).resolve().parent.parent
SCHOOLS_FILE = ROOT / "data" / "schools.json"
BALLOT_FILE = ROOT / "data" / "ballot_history.json"


def _load_schools() -> list[School]:
    data = json.loads(SCHOOLS_FILE.read_text(encoding="utf-8"))
    return [School.from_dict(s) for s in data["schools"]]


def _load_ballot() -> dict[str, dict]:
    return json.loads(BALLOT_FILE.read_text(encoding="utf-8"))


def _band_score(band: str) -> int:
    return {"high": 3, "medium": 2, "low": 1, "blocked": 0}.get(band, 0)


def rank_shortlist(
    profile: UserProfile,
    schools: list[School] | None = None,
    ballot: dict[str, dict] | None = None,
    latest_year: int = 2025,
    limit: int = 25,
) -> list[SchoolOdds]:
    schools = schools or _load_schools()
    ballot = ballot or _load_ballot()

    candidates: list[School]
    if profile.target_school_slugs:
        wanted = set(profile.target_school_slugs)
        candidates = [s for s in schools if s.slug in wanted]
    else:
        candidates = schools

    results: list[SchoolOdds] = []
    for s in candidates:
        km = get_distance_km(profile.postal_code, s.slug) if profile.postal_code else None
        odds = compute_odds(profile, s, ballot, km, latest_year=latest_year)

        # Decorate with projection
        proj = project_indicators(
            s.slug,
            ballot.get(s.slug, {}),
            target_year=profile.target_year,
        )
        if proj.projected_sub_pct is not None:
            odds.projected_indicator = {
                profile.target_year: proj.projected_category,
            }
            odds.reasoning.append(
                f"Projected {profile.target_year} subscription: "
                f"{proj.projected_sub_pct}% (±{proj.band_half_width}); "
                f"trend slope {proj.slope_per_year:+.1f} pp/year."
            )

        results.append(odds)

    # Filter out blocked-by-distance (radius gate) when search is broad
    if not profile.target_school_slugs and profile.radius_km:
        results = [
            r for r in results
            if r.distance_km is None or r.distance_km <= profile.radius_km
        ]

    results.sort(
        key=lambda r: (
            -_band_score(r.odds_band),  # high first
            -r.odds_pct,
            r.distance_km if r.distance_km is not None else 999.0,
        )
    )
    return results[:limit]
