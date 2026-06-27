"""Pure-Python odds engine. Zero web-framework imports.

Exports:
  UserProfile       — input dataclass
  SchoolOdds        — output dataclass
  compute_odds      — single-school odds
  rank_shortlist    — multi-school ranked output
  project_indicators — trend forecast
"""
from .profile import UserProfile
from .odds import SchoolOdds, compute_odds
from .shortlist import rank_shortlist
from .projection import project_indicators

__all__ = [
    "UserProfile",
    "SchoolOdds",
    "compute_odds",
    "rank_shortlist",
    "project_indicators",
]
