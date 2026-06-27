# Architecture — Lala C SG P1 Ballot Tool v1

## Layers

```
┌─────────────────────────────────────────────────────────┐
│  WEB (FastAPI)                                          │
│   • Form (Jinja+HTMX) → JSON profile                    │
│   • Report (Jinja+HTMX) ← engine output                 │
│   • Static pages (About, Methodology, FAQ, Contact)     │
│   • Email + Stripe endpoints                            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  ENGINE (pure Python, deterministic, testable)          │
│   • profile.py      — UserProfile dataclass             │
│   • odds.py         — Phase 2A1/2A2/2B/2C decision tree │
│   • projection.py   — linear trend + 2-3yr forecast     │
│   • shortlist.py    — rank schools for a profile        │
│   • scenarios.py    — counterfactual scenario engine    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  DATA (JSON files in repo, refreshed annually)          │
│   • schools.json         — directory of 184 schools     │
│   • ballot_history.json  — 6+ years × N schools         │
│   • distance_index.json  — postal → distance map        │
│   • affiliations.json    — primary→secondary mapping    │
│   • gep_modules.json     — module-host designations     │
│   • singstat_births.json — births by planning area      │
│   • bto_completions.json — upcoming HDB BTO data        │
└─────────────────────────────────────────────────────────┘
```

## Why this shape

1. **Engine is pure.** Zero web framework imports. Easy to test, easy to
   port to MCP server later, easy to embed in PDF generator.
2. **Data is read-only JSON.** No DB in v1. Annual refresh = git commit.
   Versioned. Cacheable on edge.
3. **Web is thin.** FastAPI is < 200 lines of routing. Jinja for HTML.
   HTMX for interactivity without a JS framework.
4. **Stateless.** No user accounts. Sessions are ephemeral.

## Canonical data schemas

### `schools.json`

```json
{
  "schools": [
    {
      "slug": "kheng-cheng",
      "name": "Kheng Cheng Primary",
      "town": "Toa Payoh",
      "planning_area": "Bishan",
      "address": "26 Lorong 4 Toa Payoh, S319503",
      "lat": 1.336,
      "lng": 103.847,
      "gender": "co-ed",
      "religion": null,
      "affiliated_secondary": null,
      "gep_former_9": false,
      "module_host_2024": true,
      "moe_school_code": "0001"
    }
  ]
}
```

### `ballot_history.json`

```json
{
  "kheng-cheng": {
    "2020": {
      "vacancy": 132,
      "applied": 140,
      "taken": 132,
      "sc_indicator": "PR<1",
      "phase_2c_breakdown": {
        "sc_lt_1km": {"applicants": null, "vacancies": null},
        "sc_1_2km":  {"applicants": null, "vacancies": null},
        "sc_gt_2km": {"applicants": null, "vacancies": null},
        "pr_lt_1km": {"applicants": null, "vacancies": null}
      },
      "ballot_chance_pct": null,
      "source_url": "https://moe.gov.sg/..."
    }
  }
}
```

### `UserProfile`

```python
@dataclass
class UserProfile:
    citizenship: Literal["SC", "PR", "Foreigner"]
    gender: Literal["male", "female"]
    target_year: int                   # P1 year
    postal_code: str                   # 6-digit SG postal
    # Phase 2A1
    sibling_in_school_slugs: list[str] = []
    parent_alumni_school_slugs: list[str] = []
    # Phase 2A2
    parent_staff_school_slugs: list[str] = []
    moe_staff: bool = False
    # Phase 2B
    parent_volunteer_school_slugs: list[str] = []  # PVP 40+ hours
    clan_affiliation: list[str] = []
    religious_affiliation: list[str] = []
    # Search scope
    target_school_slugs: list[str] = []   # if empty, search all 184
    radius_km: float = 2.0
```

### Engine output: `SchoolOdds`

```python
@dataclass
class SchoolOdds:
    school_slug: str
    school_name: str
    distance_km: float
    distance_band: Literal["<1km", "1-2km", ">2km"]
    eligible_phases: list[str]           # ["2A1", "2C"] etc.
    entry_phase_estimated: str            # "2A1" if sibling, else "2C"
    odds_pct: int                         # 0-100
    odds_band: Literal["high", "medium", "low", "blocked"]
    historical_indicator_2025: str
    projected_indicator_2026: str
    projected_indicator_2027: str
    projected_indicator_2028: str
    confidence: Literal["high", "medium", "low"]
    reasoning: list[str]                  # human-readable rationale
    scenario_tweaks: list[ScenarioTweak]  # "Move within 1km → odds become X%"
```

## Folder layout

```
lala-c-sg-p1/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── home.py
│   │   ├── tool.py          # form + report
│   │   ├── content.py       # case studies, about, etc.
│   │   ├── checkout.py      # Stripe
│   │   └── webhooks.py
│   └── deps.py              # dependency injection (data loaders)
├── engine/
│   ├── __init__.py
│   ├── profile.py
│   ├── odds.py
│   ├── projection.py
│   ├── shortlist.py
│   ├── scenarios.py
│   └── distance.py          # OneMap wrapper + cache
├── data/
│   ├── schools.json
│   ├── ballot_history.json
│   ├── affiliations.json
│   ├── gep_modules.json
│   ├── singstat_births.json
│   └── bto_completions.json
├── docs/
│   ├── PRD.md
│   ├── LEGAL.md
│   ├── ARCHITECTURE.md
│   ├── LAUNCH.md
│   └── METHODOLOGY.md       # public-facing copy of methodology
├── prompts/                 # for any LLM-assisted features later
├── static/
│   ├── css/                 # Tailwind via CDN initially
│   └── img/
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── tool/
│   │   ├── form.html
│   │   └── report.html
│   ├── content/
│   │   ├── case_study_*.html
│   │   ├── about.html
│   │   ├── methodology.html
│   │   ├── faq.html
│   │   └── contact.html
│   └── legal/
│       ├── privacy.html
│       ├── terms.html
│       └── disclaimer.html
├── tests/
│   ├── test_odds.py
│   ├── test_projection.py
│   └── test_shortlist.py
├── scripts/
│   ├── refresh_ballot_data.py     # annual MOE data refresh
│   ├── refresh_singstat.py
│   └── build_distance_index.py
├── .env.template
├── .gitignore
├── pyproject.toml
└── README.md
```

## Deployment topology (v1)

```
[Cloudflare DNS]
       │
       ▼
[Cloudflare Pages] ◄─── static assets
       │
       ▼
[Render / Railway / Fly.io] ◄─── FastAPI app (uvicorn)
       │
       ├─► [Stripe API]
       ├─► [Buttondown API or SMTP]
       └─► [Plausible analytics endpoint]
```

Estimated monthly cost at v1 scale:
- Domain: $1-3/mo amortised
- Hosting: $0-7/mo (Render free tier or $7 starter)
- Email: $0-9/mo
- Analytics: $9/mo (Plausible)
- Stripe: 3.4% + S$0.50/txn
- **Total fixed: ~$20-30/mo**

## Annual maintenance load (year 2+)

| Task | When | Owner | Effort |
|---|---|---|---|
| Refresh MOE ballot data | Aug each year | Operator | 2-3 hrs |
| Refresh SingStat births | Annual (Jan) | Operator | 1 hr |
| Refresh BTO completions | Quarterly | Operator | 1 hr/quarter |
| Sensitivity-flag audit | Annual | Operator + lawyer | 4 hrs |
| Methodology page update | Annual | Operator | 1-2 hrs |
| Stripe / hosting renewal | Annual | Operator | 1 hr |

Annual ops time: ~15-20 hours. Truly "passive-shaped" after launch.
