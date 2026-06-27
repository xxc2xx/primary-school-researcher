"""Build a postal-code → all-schools distance cache.

Strategy:
  1. Geocode postal code via OneMap search (auth-token required).
  2. Compute haversine distance to every school using cached coordinates.
  3. Write result to data/distance_cache.json.

OneMap auth (as of 2026):
  1. Register account at https://www.onemap.gov.sg/
  2. Generate API token from your dashboard.
  3. Set ONEMAP_TOKEN in .env, OR pass --token CLI flag, OR use auth via
     ONEMAP_EMAIL + ONEMAP_PASSWORD (this script will fetch a token).

Usage:
    python -m scripts.build_distance_index 319503 318993
    python -m scripts.build_distance_index --token <bearer> 319503

In production the FastAPI app calls geocode_postal() on demand and caches
the result. For dev / launch, pre-seed common postals to make demos fast.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

from engine.distance import cache_set, haversine_km

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
SCHOOLS = json.loads((ROOT / "data" / "schools.json").read_text())["schools"]

ONEMAP_AUTH = "https://www.onemap.gov.sg/api/auth/post/getToken"
ONEMAP_SEARCH = (
    "https://www.onemap.gov.sg/api/common/elastic/search"
    "?searchVal={code}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
)


def _get_token() -> str | None:
    """Resolve token from env, falling back to email/password login."""
    tok = os.getenv("ONEMAP_TOKEN")
    if tok:
        return tok
    email = os.getenv("ONEMAP_EMAIL")
    pwd = os.getenv("ONEMAP_PASSWORD")
    if not (email and pwd):
        return None
    r = requests.post(ONEMAP_AUTH, json={"email": email, "password": pwd}, timeout=15)
    r.raise_for_status()
    return r.json().get("access_token")


def geocode_postal(postal: str, token: str | None = None) -> tuple[float, float] | None:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = requests.get(ONEMAP_SEARCH.format(code=postal), headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        print(f"  OneMap error: {data['error']}")
        return None
    results = data.get("results") or []
    if not results:
        return None
    hit = results[0]
    try:
        return float(hit["LATITUDE"]), float(hit["LONGITUDE"])
    except (KeyError, ValueError):
        return None


def build_for(postal: str, token: str | None = None) -> int:
    coords = geocode_postal(postal, token)
    if not coords:
        print(f"  {postal}: not found")
        return 0
    lat0, lng0 = coords
    n = 0
    for s in SCHOOLS:
        if s.get("lat") is None or s.get("lng") is None:
            continue
        km = haversine_km(lat0, lng0, s["lat"], s["lng"])
        cache_set(postal, s["slug"], km)
        n += 1
    print(f"  {postal}: ({lat0:.4f}, {lng0:.4f}) → cached {n} distances")
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("postals", nargs="+", help="One or more 6-digit postal codes")
    ap.add_argument("--token", default=None, help="Override OneMap bearer token")
    args = ap.parse_args()

    token = args.token or _get_token()
    if not token:
        print(
            "WARN: No OneMap token. Set ONEMAP_TOKEN in .env, or "
            "ONEMAP_EMAIL + ONEMAP_PASSWORD, or pass --token. "
            "Falling back to unauthenticated request (likely to fail)."
        )

    for postal in args.postals:
        build_for(postal.strip(), token=token)


if __name__ == "__main__":
    main()
