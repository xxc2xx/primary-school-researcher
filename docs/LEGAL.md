# Legal, Privacy, and Compliance — Lala C SG P1 Ballot Tool

> Not legal advice. Pre-launch checklist for the operator to review with a
> Singapore-qualified lawyer before going live. Designed to minimise risk of
> complaint or takedown from MOE, individual schools, or other parties.

---

## 1. Data sources — what's used and why each is OK

| Source | What we use | Why it's safe |
|---|---|---|
| MOE Phase 2C ballot results (annual) | School name, year, vacancies, applicants, admitted, "indicator" (which group balloted) | MOE publishes this publicly every Aug. Re-presenting public statistics is fair use; cite MOE on every figure. |
| SC Schooling site (sc-schooling.com) | Aggregated tables | Their data is itself aggregated from MOE. We cite MOE directly and add value (personalization + projection). |
| OneMap (data.gov.sg) | Postal code → coordinates → distance to school | Official SG government API; free for non-commercial use; verify the licence permits commercial. |
| SingStat (Department of Statistics SG) | Births by planning area, household composition | Public domain government statistics. Cite source. |
| URA Master Plan | Planning area boundaries | Public. Cite. |
| HDB BTO completion | Completion dates + unit counts | Public on HDB site. Cite. |
| School official names + secondary affiliations | School name, address, affiliations | Factual; MOE publishes school directory. |

**Hard rules we never break:**

- ❌ Never republish proprietary content (KiasuParents threads, school IG/FB photos, paywalled articles).
- ❌ Never claim affiliation with MOE / any school / any government entity.
- ❌ Never editorialise about a school's quality unless quoting a clearly attributed source.
- ❌ Never publish photos of any school, child, or family.
- ❌ Never identify the operator's personal child / school choice / address.

## 2. Disclaimers — required text on every page

Footer (every page):

> **Lala C** is an independent analysis service. We are **not affiliated with
> the Singapore Ministry of Education** or any individual school. All ballot
> figures are sourced from MOE public statistics. Odds are estimates based on
> historical data and modelling assumptions; actual admission outcomes are
> determined by MOE alone.

Report page (additional):

> This estimate is based on historical Phase 2C ballot results and a
> projection model. It is a guide, not a guarantee. MOE's admission process
> is the sole authority on actual outcomes. **Updated: \<ISO date\>**.

## 3. Privacy

- **No accounts in v1.** Anonymous use only.
- **Email capture** is opt-in for "send me my report PDF." Single-use; we
  send the PDF + occasional updates (max monthly). One-click unsubscribe.
- **Form inputs (postal, profile)** are processed in-memory; not stored
  unless the user opts in to email capture.
- **Analytics** via Plausible (privacy-first, no cookies, no fingerprinting).
- **No third-party trackers**. No Google Analytics. No Facebook Pixel.
- **Stripe** processes payments; only the email + customer ID we keep.
- **Singapore PDPA compliance**:
  - Privacy policy page lists data collected, purpose, retention, contact.
  - "Do not sell my data" not applicable (we don't sell).
  - Data subject request route: email `privacy@<domain>`.

## 4. Takedown / complaint process

Public-facing on Contact page:

> If you represent a school, MOE, or any other party and have a concern
> about data on this site, email `takedown@<domain>` with the specific URL
> and concern. We will respond within 5 business days. Genuine data errors
> are corrected within 48 hours of confirmation.

Internal SOP (operator-only):

1. Acknowledge within 24h.
2. Pause the offending page (return 503 with brief message) within 48h if
   the complaint is from MOE, a named school, or alleges legal violation.
3. Verify the underlying data; cite the source publicly if data is correct.
4. If data is wrong, fix + publish a correction note.
5. Never engage publicly with the complainant — only via email log.
6. Keep a copy of every complaint + response.

## 5. School-by-school sensitivity flags

Some schools may be more litigious or sensitive. Pre-launch, audit each
of the 184 schools for:

- **Single-gender schools** — clearly mark gender in profile so the user
  isn't shown irrelevant odds.
- **Religious schools (CHIJ, Methodist, Catholic, SDA)** — present
  Phase 2B affiliations factually; never comment on religious doctrine.
- **GEP former-9 schools** — present the 2024 policy change neutrally;
  cite the National Day Rally announcement.
- **Schools with recent press controversies** — do NOT reference; show
  only ballot statistics.

Maintain an internal list of "be extra careful" schools (~10 of 184) at
`docs/sensitivity_flags.md` (not public).

## 6. Pricing / commerce legal

- **Refund policy** — clearly stated. v1 default: 7-day money-back on
  paid PDF; no refund on 1:1 sessions after delivery.
- **Stripe seller account** — register as sole proprietor / business
  with ACRA before going live. Use a business name (not Lala C if Lala C
  is purely a pen name) on the Stripe account; the consumer-facing brand
  can still be Lala C.
- **GST** — SG GST registration kicks in at S$1M annual turnover. Not
  applicable v1; revisit.
- **Receipts** — Stripe handles automatically.

## 7. Intellectual property

- **Our IP**: site copy, analysis writeups, projection model, brand assets
  — all owned by the operator / Lala C business entity.
- **MOE data**: not IP-protected (government statistics); attribution
  required.
- **User-submitted data** (form inputs): user retains; we have a limited
  licence to process for the report.

## 8. Operator-employer separation

> Operator works full-time for a different employer. This project is a
> personal side-project on personal time, on personal hardware, using
> personally-paid hosting + tools. No employer IP, no employer time, no
> employer customer data is used. The brand "Lala C" is intentionally
> distinct from the operator's professional identity.

Recommended steps:

- [ ] Check employment contract for moonlighting / IP-assignment clauses.
- [ ] If contract requires disclosure: notify employer in writing of the
      side-project at a high level. Keep the notification on file.
- [ ] Never use employer email / device / network for any Lala C work.
- [ ] Set up separate GitHub account or use a clearly-personal account
      with no employer references in the profile.
- [ ] Use a separate bank account for revenue.

## 9. Pre-launch checklist (legal items only)

- [ ] Lawyer review of Privacy Policy, Terms, Disclaimer pages.
- [ ] Lawyer review of refund policy + Stripe terms acceptance.
- [ ] Lawyer review of how MOE / school complaints are addressed.
- [ ] Business / sole-prop registration with ACRA done.
- [ ] Stripe live mode approved with that business identity.
- [ ] DKIM, SPF, DMARC set on the sending domain.
- [ ] Sensitivity-flag list reviewed for the top 50 launch schools.
- [ ] Operator confirms employment contract permits the side project.
- [ ] Takedown@/Privacy@/Contact@ inboxes monitored.
