# Launch + distribution playbook — Lala C SG P1 Ballot Tool

> Operator-only. Don't publish. Step-by-step from "code complete" to "first 10 paid customers".

---

## Pre-launch checklist (final week)

### Domain + hosting
- [ ] Buy domain. Recommended order of preference:
  1. `lalac.sg` — brandable, country-specific
  2. `p1odds.sg` — descriptive, SEO-friendly
  3. `sgp1.guide` — descriptive, .guide TLD
  4. `lala-c.com` — fallback if .sg not available
- [ ] Set up Cloudflare DNS.
- [ ] Hosting on **Render** ($7/mo starter) or **Fly.io** (similar pricing). Both deploy from Git.
- [ ] Custom domain → hosting; SSL automatic.
- [ ] Set environment variables on host (see `.env.template`).

### Email
- [ ] Buttondown subscription ($9/mo for under 1k subs) — cleaner than SMTP at this scale.
- [ ] Verify sending domain in Buttondown.
- [ ] Configure DKIM, SPF, DMARC records.
- [ ] Test send: hello@<domain> → personal Gmail; check headers.

### Stripe
- [ ] Sign up for Stripe SG.
- [ ] **Business registration first** — register a sole proprietor with ACRA ($115 + $60/yr).
  Use a business name (e.g. "Lala C Analytics") that's separate from your legal identity.
- [ ] Stripe products:
  - Product: "P1 Strategy Guide PDF" — S$39
  - Product: "1:1 P1 Strategy Session" — S$199
- [ ] Test mode: confirm checkout works end-to-end with test card 4242…
- [ ] Webhook endpoint live at `/webhooks/stripe`.
- [ ] Activate live mode only after the first 3 internal test purchases pass.

### Legal
- [ ] All four legal pages live (Privacy, Terms, Disclaimer, Contact).
- [ ] Lawyer review (1-2 hour engagement; ~$300-500 in SG).
- [ ] Takedown@ inbox monitored — set up email forwarding to your personal address.

### Analytics
- [ ] Plausible account, site added.
- [ ] Script tag added to `base.html`.
- [ ] Verify event tracking on `/tool/report`.

### Final QA
- [ ] Every form combo (SC/PR × M/F × with/without postal × with/without 2A1) renders correctly.
- [ ] Mobile (iPhone Safari + Android Chrome): every page.
- [ ] Search "Lala C" — confirm zero existing brand collision.
- [ ] Every page validates schema.org markup at https://validator.schema.org/.
- [ ] Lighthouse audit: 90+ on Performance, Accessibility, SEO.

---

## Launch day (T-day)

### T-3 (Wednesday)
- Final QA pass.
- Buy enough Userinterviews.com credits OR identify 10 friends to be first test users.
- Draft all distribution posts (see below). Schedule for T-day.

### T-1 (Thursday)
- Soft launch to your 10 closest contacts:
  > "Hey, finally launching the SG P1 ballot tool I've been building. Could you give
  > me 2 mins of feedback on the form flow? Link: <url>"
- Fix anything they break.

### T-day (Friday morning)
- Publish to all distribution channels (see below).
- Monitor analytics every 2 hours.
- Reply to every comment / DM / email within 4 hours.
- Don't ship code changes today unless something is genuinely broken.

### T+1 to T+7
- Daily: 30 min reply to comments, 30 min draft 1 follow-up post, 30 min analytics review.
- Track in spreadsheet: source → visitors → reports generated → email signups → paid sales.

---

## Distribution channels — drafts

### 1. KiasuParents post (the highest-leverage venue)

**Sub-forum:** Primary Schools → Primary 1 Registration.

**Title:** "Built a free P1 ballot odds calculator (independent, MOE-data based)"

**Body:**
> Hi all — long-time lurker, first-time poster (under this name).
>
> I'm a parent who got tired of opening 8 tabs to figure out my child's realistic
> chance of getting into different primary schools. So I built a tool. It walks every
> MOE admission phase that applies to your family (Phase 1 / 2A1 / 2A2 / 2B / 2C), uses
> 6 years of MOE Phase 2C ballot data, and gives you a ranked shortlist for your target
> year — plus a projection of where each school's subscription is heading.
>
> It's free, no signup needed for the basic calculator. Tool: <url>
>
> I'd genuinely love feedback — what's confusing, what's missing, where the model's
> output disagrees with your gut. KiasuParents has been an unofficial source of mine
> while building this; would be great to give back something useful.
>
> Not affiliated with any school or MOE. Independent project. Methodology fully
> documented at <url>/methodology.

**Why it works:** humble, gives credit to KP, asks for feedback (encourages replies),
no spammy product pitch.

---

### 2. Reddit posts

**Subreddit:** r/singapore.
**Title:** "I built a free SG Primary 1 ballot odds calculator — feedback welcome"
**Body:** similar to KP post but tightened to ~150 words. Reddit users hate long posts.

**Also:** r/SingaporeRaw, r/asksingapore if welcoming.

**Don't:** post the same content verbatim across subs (looks spammy). Tailor each.

---

### 3. Facebook groups — pick 3-5

Test each group's rules first. Many have strict "no self-promotion" — read the rules.
For groups where promotion is allowed:

- HK/SG Mums and Bumps (if cross-relevant)
- Singapore Mums - All About Kids
- IB / IGCSE / IBDP Asia (SG members)
- Singapore Parents / Parenting Forum SG
- Local PSLE / P1 / Education groups

**Body:** same as KP, but shorter (200 words). Lead with the tool. Include screenshot.

---

### 4. Mom influencer DMs (5-10 targeted)

Targets: SG-based parenting Instagram / TikTok accounts with 10k-100k followers and
recent posts about school selection.

**Template:**
> Hi [name] — really enjoyed your post about [specific thing they posted about].
>
> I just launched a free P1 ballot odds calculator for SG parents — built it for my
> own family and figured others would find it useful. Independent, MOE-data based.
>
> No partnership ask — would love your honest take if you want to give it a spin.
> Tool: <url>
>
> If you find it useful and want to share with your audience, that would be lovely
> but no pressure. Happy to chat any time.

---

### 5. Press pitch (3-5 outlets)

Targets:
- **Mothership** — best for human-interest angle ("PR parent built this tool")
- **The Straits Times** — Education desk
- **CNA** — Lifestyle / Education
- **The Smart Local** — listicle-friendly
- **AsiaOne** — broader reach

**Pitch (email):**
> **Subject:** Free tool: SG P1 ballot odds calculator (built by a parent)
>
> Hi [name],
>
> I built a free tool that helps Singapore parents estimate their realistic chance of
> getting their child into specific primary schools, based on 6 years of MOE Phase 2C
> ballot data. It walks every admission phase that applies (1 / 2A1 / 2A2 / 2B / 2C)
> and projects forward to the parent's target P1 year.
>
> I built it for my own family — got frustrated that the data exists but nobody
> assembles it for individual families. Now free for anyone.
>
> Happy to share more, do an interview, or write a guest column. Tool: <url>.
> Methodology: <url>/methodology.
>
> Lala C (independent analyst)

---

## First-week metrics targets

| Day | Visitors | Reports | Emails | Paid |
|---|---|---|---|---|
| T-day | 100-500 | 30-150 | 10-50 | 0-1 |
| T+1 | 200-800 | 50-200 | 20-80 | 0-3 |
| T+7 | 500-2000 | 100-500 | 30-150 | 1-5 |

If visitors look fine but reports/emails are low → form UX problem.
If reports look fine but emails are low → email CTA copy problem.
If emails look fine but paid is zero → product/positioning problem (most common).

Diagnose. Don't add features. Fix the highest-leverage funnel step.

---

## Post-launch (weeks 2-8)

### Weekly cadence
- **Monday:** review last week's analytics + paid sales.
- **Tuesday:** reply to every comment / email / DM from last week.
- **Wednesday:** draft 1 piece of distribution (case study, KP follow-up, mom-influencer DM).
- **Thursday:** ship the piece.
- **Friday:** observe + read forums (don't post). Note what's resonating.

### Month 1 goals
- 10+ paid sales
- 100+ email signups
- 1+ press mention OR mom influencer share
- 5+ replies on the KP post

### Month 2 goals
- 25+ paid sales
- 250+ emails
- 1 case study added (run on real-world demand pattern)
- First AI citation appearance (test by asking Claude / ChatGPT "SG P1 ballot odds for school X")

### Month 3 — decision gate
If month 1-2 metrics hit: invest in v1.1 (expand to all 184 schools, OneMap integration,
Stripe live mode polish).

If month 1-2 metrics miss by 50%+: diagnose. Likely culprits:
1. Domain / brand isn't memorable
2. Conversion CTA is buried
3. Audience hasn't reached people willing to pay (try paid Meta ads, $300 test)

Don't expand scope until conversion works.

---

## What not to do

- ❌ Don't post the same content in 10 channels in a single hour (looks like a bot).
- ❌ Don't reply to negative comments with anything other than "thanks, will look into".
- ❌ Don't argue with KiasuParents users (you will lose).
- ❌ Don't expand to HK before SG conversion is proven.
- ❌ Don't accept free promo offers from agents/agencies in the first 30 days (filter signal
     from noise first).
- ❌ Don't add features that month-1 users requested. Wait for month 3 to evaluate.
