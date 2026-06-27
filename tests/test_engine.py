"""Engine smoke + golden-case tests.

Golden cases are taken from the operator's hand-verified analysis in the
private research repo.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.distance import cache_set
from engine.odds import compute_odds
from engine.profile import School, UserProfile
from engine.projection import project_indicators
from engine.shortlist import rank_shortlist


ROOT = Path(__file__).resolve().parent.parent
SCHOOLS = json.loads((ROOT / "data" / "schools.json").read_text())["schools"]
BALLOT = json.loads((ROOT / "data" / "ballot_history.json").read_text())


def _school(slug: str) -> School:
    for s in SCHOOLS:
        if s["slug"] == slug:
            return School.from_dict(s)
    raise KeyError(slug)


def test_pr_within_1km_kheng_cheng_2025_walks_in():
    """2025 indicator at Kheng Cheng was PR1-2: PR<1km should walk in."""
    profile = UserProfile(
        citizenship="PR", gender="female", target_year=2027,
        postal_code="319503",  # near Kheng Cheng
    )
    cache_set("319503", "kheng-cheng", 0.5)
    odds = compute_odds(profile, _school("kheng-cheng"), BALLOT, 0.5, latest_year=2025)
    assert odds.odds_band == "high"
    assert odds.odds_pct >= 90


def test_pr_beyond_2km_pei_chun_shut_out():
    """Pei Chun fills with SC<1km — PR>2km has zero chance."""
    profile = UserProfile(
        citizenship="PR", gender="male", target_year=2027,
        postal_code="000000",
    )
    cache_set("000000", "pei-chun-public", 5.0)
    odds = compute_odds(profile, _school("pei-chun-public"), BALLOT, 5.0, latest_year=2025)
    assert odds.odds_band == "blocked"
    assert odds.odds_pct == 0


def test_sibling_phase_2a1_high_odds():
    """Sibling currently in school → Phase 2A1 near-certain."""
    profile = UserProfile(
        citizenship="PR", gender="female", target_year=2027,
        postal_code="000000",
        sibling_in_school_slugs=["kheng-cheng"],
    )
    odds = compute_odds(profile, _school("kheng-cheng"), BALLOT, 5.0, latest_year=2025)
    assert odds.entry_phase_estimated == "2A1"
    assert odds.odds_pct >= 95


def test_gender_blocks_admission():
    """A male child cannot apply to a girls-only school."""
    profile = UserProfile(
        citizenship="SC", gender="male", target_year=2027,
        postal_code="000000",
    )
    odds = compute_odds(profile, _school("marymount-convent"), BALLOT, 0.3, latest_year=2025)
    assert odds.odds_band == "blocked"
    assert odds.blocked_reason == "gender"


def test_projection_returns_category_for_known_school():
    proj = project_indicators("kheng-cheng", BALLOT["kheng-cheng"], target_year=2027)
    assert proj.projected_category in {"open", "pr", "sc", "unknown"}
    assert proj.confidence in {"high", "medium", "low"}


def test_shortlist_orders_high_first():
    profile = UserProfile(
        citizenship="PR", gender="female", target_year=2027,
        postal_code="319503",
        target_school_slugs=["kheng-cheng", "pei-chun-public", "cedar"],
    )
    cache_set("319503", "kheng-cheng", 0.5)
    cache_set("319503", "pei-chun-public", 0.7)
    cache_set("319503", "cedar", 0.9)
    results = rank_shortlist(profile, latest_year=2025)
    assert len(results) == 3
    # 'high' bands appear before 'blocked'
    bands = [r.odds_band for r in results]
    assert bands.index("blocked") == len(bands) - 1 if "blocked" in bands else True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
