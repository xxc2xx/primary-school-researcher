"""Seed v1 data from the private research repo (sg-p1-ballot).

This is a one-shot transformation:
  ~/sg-p1-ballot/data/ballot_complete.json  →  ./data/schools.json + ./data/ballot_history.json

It strips all personal-narrative / sentiment / KP-forum / Schlah ranking
fields. Only objective public statistics survive. Run once; re-run when
research repo is refreshed.

Usage:
    python -m scripts.seed_from_research_repo
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path.home() / "sg-p1-ballot" / "data" / "ballot_complete.json"
SCHOOLS_OUT = ROOT / "data" / "schools.json"
BALLOT_OUT = ROOT / "data" / "ballot_history.json"

# Hardcoded enrichments derived from public MOE / school directory info.
# These should later move to their own data sources (`affiliations.json`,
# `gep_modules.json`) — but v1 inlines them so seed is one-shot.
AFFILIATIONS = {
    "catholic-high": "Catholic High School",
    "kuo-chuan-presbyterian": "Kuo Chuan Presbyterian Secondary",
    "canossa-catholic": "St. Anthony's Canossian Secondary",
    "geylang-methodist": "Geylang Methodist Secondary",
    "maha-bodhi": "Manjusri Secondary",
    "ngee-ann": "Ngee Ann Secondary",
    "chij-toa-payoh": "CHIJ Secondary (Toa Payoh)",
    "maris-stella-high": "Maris Stella High School",
    "chij-st-nicholas-girls": "CHIJ St. Nicholas Girls' School",
    "st-andrew-junior": "St. Andrew's Secondary",
}

# Single-gender schools (verify against MOE directory before launch).
GENDER = {
    "marymount-convent": "female",
    "chij-toa-payoh": "female",
    "haig-girls": "female",
    "chij-st-nicholas-girls": "female",
    "maris-stella-high": "male",
    "catholic-high": "male",
    "st-andrew-junior": "male",
}

GEP_FORMER_9 = {"catholic-high", "tao-nan"}
MODULE_HOST_2024 = {"kheng-cheng"}


def transform() -> None:
    src = json.loads(SRC.read_text(encoding="utf-8"))
    schools = []
    ballot: dict[str, dict] = {}

    for s in src:
        slug = s["slug"]
        schools.append({
            "slug": slug,
            "name": s["name"],
            "town": s["town"],
            "planning_area": s["town"],
            "gender": GENDER.get(slug, "co-ed"),
            "religion": None,
            "affiliated_secondary": AFFILIATIONS.get(slug),
            "gep_former_9": slug in GEP_FORMER_9,
            "module_host_2024": slug in MODULE_HOST_2024,
            "lat": s.get("schlah_lat"),
            "lng": s.get("schlah_lng"),
            "address": s.get("schlah_address"),
        })

        yearmap = {}
        for y, info in s.get("years", {}).items():
            yk = str(y)

            def _maybe_int(v):
                try:
                    return int(v) if v is not None and v != "" else None
                except (ValueError, TypeError):
                    return None

            yearmap[yk] = {
                "vacancy": _maybe_int(info.get("vacancy")),
                "applied": _maybe_int(info.get("applied")),
                "taken": _maybe_int(info.get("taken")),
                "sc_indicator": (info.get("sc_indicator") or "").strip(),
                "ballot_chance_pct": info.get("sc_ballot_chance"),
                "bucket_applicants": info.get("sc_bucket_applicants"),
                "bucket_vacancies": info.get("sc_bucket_vacancies"),
            }
        ballot[slug] = yearmap

    SCHOOLS_OUT.write_text(
        json.dumps({"schools": schools, "as_of_year": 2025}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    BALLOT_OUT.write_text(
        json.dumps(ballot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(schools)} schools → {SCHOOLS_OUT}")
    print(f"Wrote ballot history → {BALLOT_OUT}")


if __name__ == "__main__":
    transform()
