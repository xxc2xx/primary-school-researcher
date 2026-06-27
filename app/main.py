"""FastAPI app — Lala C SG P1 Ballot Tool.

Run:
    uvicorn app.main:app --reload
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.security import SecurityHeadersMiddleware, assert_safe_origin
from engine.distance import cache_set, get_distance_km
from engine.profile import UserProfile
from engine.shortlist import rank_shortlist

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = Jinja2Templates(directory=ROOT / "templates")
STATIC = ROOT / "static"

app = FastAPI(title="Lala C — SG P1 Ballot Tool", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")

# Security headers on every response
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiter — per-IP via X-Forwarded-For when behind Cloudflare/Render
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return PlainTextResponse(
        "Too many requests. Please slow down and try again in a minute.",
        status_code=429,
    )

SITE_NAME = os.getenv("SITE_NAME", "Lala C")
SITE_URL = os.getenv("SITE_URL", "http://localhost:8000")


def _ctx(**extra) -> dict:
    base = {
        "site_name": SITE_NAME,
        "site_url": SITE_URL,
        "contact_email": os.getenv("CONTACT_EMAIL", "hello@lalac.sg"),
        "takedown_email": os.getenv("TAKEDOWN_EMAIL", "takedown@lalac.sg"),
        "as_of_year": 2025,
    }
    base.update(extra)
    return base


def _render(request: Request, template: str, **extra) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(request, template, _ctx(**extra))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return _render(request, "home.html")


@app.get("/tool", response_class=HTMLResponse)
def tool_form(request: Request):
    return _render(request, "tool/form.html")


@app.post("/tool/report", response_class=HTMLResponse)
@limiter.limit("10/hour")
def tool_report(
    request: Request,
    citizenship: str = Form(...),
    gender: str = Form(...),
    target_year: int = Form(...),
    postal_code: str = Form(""),
    radius_km: float = Form(2.0),
    sibling_school: str = Form(""),
    alumni_school: str = Form(""),
    pvp_school: str = Form(""),
    _origin: None = Depends(assert_safe_origin),
):
    profile = UserProfile(
        citizenship=citizenship,  # type: ignore[arg-type]
        gender=gender,  # type: ignore[arg-type]
        target_year=target_year,
        postal_code=postal_code,
        sibling_in_school_slugs=[s.strip() for s in sibling_school.split(",") if s.strip()],
        parent_alumni_school_slugs=[s.strip() for s in alumni_school.split(",") if s.strip()],
        parent_volunteer_school_slugs=[s.strip() for s in pvp_school.split(",") if s.strip()],
        radius_km=radius_km,
    )

    # For demo: if no postal, set a sentinel "all schools far" so engine still runs
    if postal_code:
        # In v1, we ship a small distance fixture; OneMap integration is a v1.1 task
        # If no cache entry exists, the engine treats distance as unknown and
        # most schools become non-blocked but uncertain.
        pass

    results = rank_shortlist(profile, latest_year=2025, limit=25)
    return _render(request, "tool/report.html", profile=profile, results=results)


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return _render(request, "content/about.html")


@app.get("/methodology", response_class=HTMLResponse)
def methodology(request: Request):
    return _render(request, "content/methodology.html")


@app.get("/faq", response_class=HTMLResponse)
def faq(request: Request):
    return _render(request, "content/faq.html")


@app.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    return _render(request, "content/contact.html")


@app.get("/case-studies", response_class=HTMLResponse)
def case_studies(request: Request):
    return _render(request, "content/case_studies.html")


@app.get("/case-studies/{slug}", response_class=HTMLResponse)
def case_study(request: Request, slug: str):
    return _render(request, f"content/case_study_{slug}.html", slug=slug)


@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return _render(request, "legal/privacy.html")


@app.get("/terms", response_class=HTMLResponse)
def terms(request: Request):
    return _render(request, "legal/terms.html")


@app.get("/disclaimer", response_class=HTMLResponse)
def disclaimer(request: Request):
    return _render(request, "legal/disclaimer.html")


# --- Commerce stubs (gated until Stripe keys go live) ---

@app.post("/email-capture")
@limiter.limit("5/hour")
def email_capture(
    request: Request,
    email: str = Form(...),
    _origin: None = Depends(assert_safe_origin),
):
    """v1 stub — append to data/email_signups.jsonl. Replace with Buttondown in launch sprint."""
    sink = ROOT / "data" / "email_signups.jsonl"
    sink.parent.mkdir(exist_ok=True)
    with sink.open("a", encoding="utf-8") as f:
        import json, datetime
        f.write(json.dumps({"email": email, "ts": datetime.datetime.utcnow().isoformat()}) + "\n")
    return RedirectResponse(url="/tool?signed_up=1", status_code=303)


@app.get("/buy/pdf", response_class=HTMLResponse)
def buy_pdf(request: Request):
    """Stub — Stripe Checkout session creation goes here."""
    return _render(request, "checkout/pdf_stub.html")


@app.get("/buy/session", response_class=HTMLResponse)
def buy_session(request: Request):
    """Stub — Stripe Checkout session creation goes here."""
    return _render(request, "checkout/session_stub.html")


# --- Crawl / discoverability + security disclosure ---

_ROBOTS_TXT = """\
# Lala C — SG P1 Ballot Tool
# Crawlers welcome. The GEO strategy depends on AI ingestion.

User-agent: *
Allow: /
Disallow: /buy/
Disallow: /email-capture
Disallow: /tool/report

# Explicit allow for major AI crawlers (some respect specific UAs).
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: {site}/sitemap.xml
"""


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    return _ROBOTS_TXT.format(site=os.getenv("SITE_URL", "http://localhost:8000").rstrip("/"))


_STATIC_PATHS = [
    "/", "/tool", "/about", "/methodology", "/faq", "/contact",
    "/case-studies",
    "/case-studies/flip-watch",
    "/case-studies/tengah-bto",
    "/case-studies/bishan-sc",
    "/privacy", "/terms", "/disclaimer",
]


@app.get("/sitemap.xml")
def sitemap_xml():
    site = os.getenv("SITE_URL", "http://localhost:8000").rstrip("/")
    urls = "\n".join(
        f"  <url><loc>{site}{p}</loc><changefreq>monthly</changefreq></url>"
        for p in _STATIC_PATHS
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
    return Response(content=body, media_type="application/xml")


@app.get("/.well-known/security.txt", response_class=PlainTextResponse)
def security_txt():
    site = os.getenv("SITE_URL", "http://localhost:8000").rstrip("/")
    contact = os.getenv("SECURITY_EMAIL", "security@lalac.sg")
    return (
        f"Contact: mailto:{contact}\n"
        f"Expires: 2027-12-31T23:59:59Z\n"
        "Preferred-Languages: en\n"
        f"Canonical: {site}/.well-known/security.txt\n"
        "# Responsible disclosure welcomed. We respond within 5 business days.\n"
    )
