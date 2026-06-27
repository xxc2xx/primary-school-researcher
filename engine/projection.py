"""Linear-trend projection of school subscription % and indicator category.

v1 model is intentionally simple:
  - Fit OLS on (year, sub_pct) for available years.
  - Project sub_pct for target year.
  - Project indicator category from last-3 mode (with most-recent tiebreak).

v2 will incorporate cohort/birth + BTO data + Bayesian uncertainty.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Category = Literal["open", "pr", "sc", "unknown"]


@dataclass
class Projection:
    school_slug: str
    target_year: int
    projected_sub_pct: int | None
    band_half_width: int | None
    projected_category: Category
    slope_per_year: float
    confidence: Literal["high", "medium", "low"]
    notes: list[str]


def _sub_pct(d: dict | None) -> int | None:
    if not d:
        return None
    v = d.get("vacancy")
    a = d.get("applied")
    if not v or not a:
        return None
    try:
        return round(int(a) / int(v) * 100)
    except (ValueError, ZeroDivisionError):
        return None


def _category(d: dict | None) -> Category:
    if not d:
        return "unknown"
    ind = (d.get("sc_indicator") or "").strip().upper()
    if not ind:
        return "open"
    if ind.startswith("PR"):
        return "pr"
    if ind.startswith("SC"):
        return "sc"
    return "unknown"


def project_indicators(
    school_slug: str,
    yearmap: dict[str, dict],
    target_year: int,
    historical_years: list[int] | None = None,
) -> Projection:
    historical_years = historical_years or list(range(2020, 2026))
    pts: list[tuple[int, int]] = []
    cats: list[tuple[int, Category]] = []
    for y in historical_years:
        d = yearmap.get(str(y)) or yearmap.get(y)
        p = _sub_pct(d)
        if p is not None:
            pts.append((y, p))
        c = _category(d)
        if c != "unknown":
            cats.append((y, c))

    notes: list[str] = []
    if len(pts) < 2:
        return Projection(
            school_slug=school_slug,
            target_year=target_year,
            projected_sub_pct=None,
            band_half_width=None,
            projected_category="unknown",
            slope_per_year=0.0,
            confidence="low",
            notes=["Not enough historical data to project."],
        )

    n = len(pts)
    mean_x = sum(x for x, _ in pts) / n
    mean_y = sum(y for _, y in pts) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in pts)
    den = sum((x - mean_x) ** 2 for x, _ in pts) or 1.0
    slope = num / den
    intercept = mean_y - slope * mean_x

    proj = max(0, round(slope * target_year + intercept))

    # YoY-delta stdev for uncertainty band
    ys = [y for _, y in pts]
    deltas = [ys[i + 1] - ys[i] for i in range(n - 1)]
    if len(deltas) >= 2:
        m = sum(deltas) / len(deltas)
        var = sum((d_ - m) ** 2 for d_ in deltas) / (len(deltas) - 1)
        stdev = var ** 0.5
    else:
        stdev = float(abs(deltas[0])) if deltas else 0.0
    band = round(stdev) if stdev > 0 else 5

    last3 = [c for _, c in cats[-3:]]
    if last3:
        mode = max(set(last3), key=last3.count)
        if last3.count(mode) == 1:
            proj_cat: Category = last3[-1]
        else:
            proj_cat = mode
    else:
        proj_cat = "unknown"

    if abs(slope) >= 5:
        notes.append(f"Strong trend: {slope:+.1f} percentage points per year.")
    elif abs(slope) >= 1.5:
        notes.append(f"Moderate trend: {slope:+.1f} percentage points per year.")
    else:
        notes.append("Flat trend.")

    confidence: Literal["high", "medium", "low"]
    if len(pts) >= 5 and stdev < 8:
        confidence = "high"
    elif len(pts) >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    return Projection(
        school_slug=school_slug,
        target_year=target_year,
        projected_sub_pct=proj,
        band_half_width=band,
        projected_category=proj_cat,
        slope_per_year=slope,
        confidence=confidence,
        notes=notes,
    )
