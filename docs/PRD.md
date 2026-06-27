# Lala C — SG P1 Ballot Tool · v1 PRD

> Public-facing product. Owner brand: **Lala C**. Operator's legal name and
> employer never appear in any public artifact.

---

## 1. Mission

Help Singapore parents understand their realistic chance of getting their
child into any of the ~184 SG primary schools — given their actual profile
(SC/PR, address, affiliations, target year) — and what to do about it.

## 2. Why now

- MOE publishes ballot results annually; nobody synthesises them into
  personalised odds + forward projection.
- LLMs cannot answer "what are *my* P1 odds at School X in 2028" because
  this requires a computation over fresh data + user profile.
- P1 registration anxiety is annual, predictable, and high-spend.

## 3. v1 scope (4 weeks)

**In scope:**

- ✅ Generalised odds engine — any user profile × any school × any year.
- ✅ All ~184 SG primary schools (data refresh once per year).
- ✅ Phase 2A1 / 2A2 / 2B / 2C priority logic explicit.
- ✅ Simple linear projection layer for next 2-3 years.
- ✅ Free interactive form on the web → personalised odds report.
- ✅ Email capture + paid product checkout (Stripe, scaffolded — toggle live at launch).
- ✅ 3 analytical case studies (no personal data anywhere).
- ✅ About / Methodology / FAQ / Contact pages.
- ✅ Schema.org markup on every page for LLM citation.

**Explicitly OUT of scope (deferred):**

- ❌ School social media aggregation (legal review needed; v2/v3).
- ❌ HK K1 admissions (v2 — port after SG works).
- ❌ Property layer (v2 — neighborhood graph).
- ❌ Bayesian / ML projection (v2 — start with linear).
- ❌ MCP server (v2 — after monetization proven).
- ❌ Mobile app (browser only).
- ❌ User accounts / login (v1 is anonymous + email-gated for reports).

## 4. Success metrics

| Metric | v1 target (week 8 post-launch) |
|---|---|
| Unique visitors | 2,000+ |
| Free reports generated | 500+ |
| Email captures | 150+ |
| Paid product sales ($39 PDF) | 10+ |
| 1:1 session sales ($199) | 2+ |
| AI citation appearances (manual checks) | 1+ |
| Brand search volume ("Lala C P1") | non-zero |

If hit, expand layers. If missed by >50%, diagnose conversion vs. traffic
before adding scope.

## 5. Sprint plan (4 weeks)

### Sprint 1 — Engine (week 1)
Goal: pure-Python module that takes a user profile + school + year → odds.

| Day | Deliverable |
|---|---|
| 1 | Refactor data: extract `ballot_complete.json` → canonical schema covering all 184 schools. (Use existing 25 as starting point; expand later.) |
| 1-2 | Build `engine/profile.py` — user profile dataclass (SC/PR/foreign, gender, postal, affiliations). |
| 2-3 | Build `engine/odds.py` — Phase 2A1/2A2/2B/2C decision tree. |
| 3-4 | Build `engine/projection.py` — linear trend + 2026/2027/2028 forecast. |
| 4-5 | Write unit tests for known cases (Kheng Cheng PR<1, Pei Chun SC<1, etc.). |

### Sprint 2 — Web (week 2)
Goal: working web app local — form → report.

| Day | Deliverable |
|---|---|
| 1-2 | FastAPI app skeleton + Jinja templates. |
| 2-3 | Form page: profile inputs (validated). |
| 3-4 | Report page: ranked schools, ballot odds, projection, scenario tweaks. |
| 4-5 | Static pages: About, Methodology, FAQ, Contact. |

### Sprint 3 — Content + commerce (week 3)
Goal: launch-ready product.

| Day | Deliverable |
|---|---|
| 1-2 | Write 3 analytical case studies (drafts). |
| 2-3 | Email capture (Buttondown or SMTP fallback). |
| 3-4 | Stripe product setup + checkout (test mode); paid PDF generation. |
| 4-5 | Schema.org markup on every page. SEO basics. Legal pages. |

### Sprint 4 — Polish + launch (week 4)
Goal: live.

| Day | Deliverable |
|---|---|
| 1 | Domain + hosting (Cloudflare Pages / Render / Railway). DNS. |
| 2 | Stripe live mode. Email DKIM/SPF. |
| 3 | Final QA: every form combo, every page, mobile. |
| 4 | Soft launch: post to KiasuParents + Reddit + 5 mom FB groups. |
| 5 | Monitor + iterate. |

## 6. Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| MOE / school issues a complaint / takedown | **High** | Use only MOE-published data; cite source on every figure; clear "not affiliated with MOE" disclaimer; takedown email visible on every page; pre-launch legal pages review |
| Linking personal narrative to operator | **High** | Lala C identity strict; no personal photos; no real address mentioned anywhere; case studies use synthetic profiles; PRD + memory enforce |
| Wrong odds → angry parent | **Medium** | Every odds number shows year + sources + confidence band; "this is a guide, not legal advice" disclaimer; provide downloadable methodology |
| Stripe / payment issues at launch | **Medium** | Stripe test mode for 7 days pre-launch; manual order processing as fallback first 30 days |
| AI / LLMs cite the wrong year's data | **Medium** | Schema.org `dateModified` everywhere; explicit "data as of: <date>" on every page |
| Hosting outage during launch | **Low** | Use static-friendly host (Cloudflare Pages or Render). Cache aggressively. |
| Operator identity leak via git author | **High** | Use separate git config: name="Lala C", email="lalac.sg@gmail.com" (or pseudonymous) for this repo only |
| Operator employer (adidas) concerns about side project | **Medium** | Personal time, separate IP, separate identity, no overlap with employer's market. Document this. |

## 7. Tech stack (final)

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11+ | Reuses existing logic |
| Web framework | FastAPI | Modern, async, OpenAPI free, easy to add MCP later |
| Templates | Jinja2 | Standard, clean |
| Frontend | HTMX + Tailwind (CDN) | Zero build step; fast to ship |
| Data store | JSON files in repo | v1 is read-only public data; no DB needed |
| Email | Buttondown (cheap) or SMTP | Lock-in low |
| Payments | Stripe | Standard; agent-commerce-ready |
| Hosting | Cloudflare Pages + Workers, or Render | Free tier viable |
| Domain | `lalac.sg` or `p1odds.sg` (TBD) | $20-40/yr |
| Analytics | Plausible (privacy-first) | $9/mo, GDPR-friendly |
| Error tracking | Sentry free tier | Standard |

## 8. Identity / branding

| Field | Value |
|---|---|
| Public name | **Lala C** |
| About-page tagline | "Independent analyst. P1 ballot data for SG parents who want straight answers." |
| Tone | Helpful, data-driven, mildly contrarian, never marketing-speak |
| Visual | Calm green/cream palette (no panic colors). Clean type. No stock photos. |
| Avatar | Either a brand mark or an illustrated/AI-generated portrait. Never operator's photo. |
| Email | `hello@<domain>` or pseudonymous Gmail forwarded |
| Contact | Form on site + email; no phone, no address |

## 9. Definition of done — v1 ships when

- [ ] All ~184 schools have ballot history loaded (or top 50 if data unavailable for tail)
- [ ] User can enter profile + get a report in < 30 seconds
- [ ] Report shows ranked schools, odds, projection, and 1+ scenario tweak
- [ ] All 4 static pages written (About, Methodology, FAQ, Contact)
- [ ] Email capture works end-to-end (test)
- [ ] Stripe checkout works end-to-end (test mode passes)
- [ ] Schema.org markup validates on schema.org validator
- [ ] Mobile view works on iPhone Safari + Android Chrome
- [ ] Domain pointing, SSL, DNS, email DKIM all green
- [ ] Legal pages (Privacy, Terms, Disclaimer) reviewed against `docs/LEGAL.md`
- [ ] First 3 distribution posts drafted (KiasuParents, Reddit, FB)
- [ ] Operator has reviewed every page for personal-data leakage

## 10. Open decisions (need owner input before sprint 4)

- Domain choice (lalac.sg vs p1odds.sg vs sgp1.guide vs other)
- Hosting choice (Cloudflare Pages vs Render vs Vercel)
- Email vendor (Buttondown $9/mo vs SMTP free)
- Pricing tiers — $39 PDF / $199 session confirmed? Or $29 / $149?
- Sole proprietorship / private business registration (for Stripe payouts)
