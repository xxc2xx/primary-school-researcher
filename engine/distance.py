"""Distance lookup — OneMap-backed with a local cache.

Real OneMap API requires an account + token. v1 ships a cache-only mode
that falls back to a manual fixture if the postal isn't in the cache.

Cache file: data/distance_cache.json
  {"postal_code": {"school_slug": km, ...}, ...}
"""
from __future__ import annotations

import json
from math import radians, sin, cos, asin, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = ROOT / "data" / "distance_cache.json"


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * r * asin(sqrt(a))


def get_distance_km(postal_code: str, school_slug: str) -> float | None:
    """Look up cached distance. Returns None if missing.

    To populate the cache:
      1. Call OneMap forward-geocode for the postal.
      2. Use haversine_km against each school's lat/lng (from schools.json).
      3. Persist via cache_set.
    """
    cache = _load_cache()
    return cache.get(postal_code, {}).get(school_slug)


def cache_set(postal_code: str, school_slug: str, km: float) -> None:
    cache = _load_cache()
    cache.setdefault(postal_code, {})[school_slug] = round(km, 3)
    _save_cache(cache)
