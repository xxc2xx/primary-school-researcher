# lala-c-sg-p1

Public-facing v1 of the Lala C Singapore Primary 1 ballot odds tool.

This repo is **the product**. The private research repo `sg-p1-ballot/`
is the data lab; this repo is what ships to the world.

## What it does

Parents enter their profile (SC/PR, gender, postal code, target year,
optional 2A1/2A2/2B priorities) and get back a ranked shortlist of
Singapore primary schools with personalised odds + 2-3-year projections.

Free. No signup. Independent. Built from MOE public statistics.

## Quick start

```bash
git clone <this repo>
cd lala-c-sg-p1
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env       # fill in keys (Stripe + email are optional for local dev)

# Seed the data from the private research repo (one-shot)
python -m scripts.seed_from_research_repo

# Run tests
pytest -v

# Run the dev server
uvicorn app.main:app --reload
# → http://localhost:8000
```

## Project structure

```
lala-c-sg-p1/
├── app/                 # FastAPI app
│   └── main.py
├── engine/              # Pure-Python odds engine (no web imports)
│   ├── profile.py       # UserProfile, School dataclasses
│   ├── odds.py          # Phase 2A1/2A2/2B/2C decision tree
│   ├── projection.py    # Linear-trend forecast
│   ├── shortlist.py     # Multi-school ranking
│   └── distance.py      # OneMap-backed distance cache
├── data/                # Read-only JSON data (annual refresh)
├── templates/           # Jinja2 + HTMX
├── docs/
│   ├── PRD.md           # Product requirements + sprint plan
│   ├── ARCHITECTURE.md  # System design + data schemas
│   ├── LEGAL.md         # Compliance + takedown SOP
│   └── LAUNCH.md        # Distribution playbook (operator-only)
├── scripts/             # One-shot data seeders + annual refresh tools
└── tests/               # pytest
```

## Key docs (read in this order)

1. `docs/PRD.md` — v1 scope, sprint plan, success metrics, risk register
2. `docs/ARCHITECTURE.md` — layers, data schemas, deployment
3. `docs/LEGAL.md` — data sources, disclaimers, takedown process
4. `docs/LAUNCH.md` — operator-only distribution playbook

## Identity discipline

This is a Lala C product. The operator's legal name and employer never
appear in any public artifact. Git author config for this repo should
use the pen name + a pseudonymous email.

```bash
git config user.name "Lala C"
git config user.email "lalac.sg@gmail.com"   # or your real pseudonym mailbox
```

## Definition of done — see `docs/PRD.md` §9
