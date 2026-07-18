# CardWise India — market, product, data and UX research

**Research date:** 18 July 2026  
**Scope:** India-first consumer credit-card discovery and recommendation.  
**Prototype status:** the working site uses a deliberately small, illustrative card snapshot. It is not a production catalogue, credit decision, financial advice, or a claim of guaranteed approval.

### Deep-research companion reports

- [`COMPETITIVE_RESEARCH.md`](COMPETITIVE_RESEARCH.md) — live review of BankBazaar, Paisabazaar, CardExpert, CreditMantri, Wishfin AI, CardInsider, Card Maven, Finology Select, SBI Card, ICICI Bank and adjacent app competitors.
- [`METHODOLOGY.md`](METHODOLOGY.md) — deterministic 12-month reward simulation, Year-1 vs ongoing value, explainability contract, accessibility, dark-pattern safeguards and 14 acceptance tests.
- [`DATA_ARCHITECTURE.md`](DATA_ARCHITECTURE.md) — authoritative-source map, bitemporal data model, ingestion/review pipeline, privacy/consent, Account Aggregator constraints and affiliate attribution.

Together, these reports contain 1,019 lines of source-linked implementation research, in addition to this consolidated product brief.

## 1. Executive recommendation

The Indian market already has strong comparison and lead-generation businesses. A new product should **not** compete by making a longer “best cards” list. The useful wedge is a transparent decision tool that:

1. gives useful results before asking for a phone number;
2. models the user’s actual annual spend by category;
3. includes fees, waivers, caps, exclusions and point valuations;
4. shows *why* each result ranked where it did;
5. treats product fit and approval/eligibility confidence as separate concepts;
6. dates every product fact and links to the issuer source;
7. identifies affiliate relationships and does not let commission silently control rank.

The prototype in `index.html` demonstrates that direction with a one-minute questionnaire, explainable scoring, conservative annual-value estimates and a three-card comparison tray.

---

## 2. Similar products: what exists and how it works

The observations below come from public pages. Statements about internal databases, ranking engines or commercial arrangements are **inferences** unless the company publicly documents them.

| Product | Public flow observed | UI/content pattern | Likely business/data model | Product lesson |
|---|---|---|---|---|
| [BankBazaar](https://www.bankbazaar.com/credit-card.html) | The credit-card page begins an eligibility journey with employment type (salaried, business owner, professional, independent worker, student, retired, homemaker), then continues toward eligible offers/application. | Large educational page, guided form, category education, issuer/card content and application CTAs. | Likely issuer/partner catalogue plus editorial CMS and lead/application routing. Exact private schema and ranking logic are not public. | Eligibility segmentation is useful, but a new product can deliver comparative value before lead capture and publish ranking logic. |
| [Paisabazaar](https://www.paisabazaar.com/credit-card/top-10-credit-cards-in-india/) | Editorial list plus card cards; mobile number is requested for pre-approved offers. Users can add cards to compare, open details or check eligibility. | Fees, ratings, benefit bullets, category tags, “add to compare,” issuer/application CTAs and update timestamps. | Likely normalized card catalogue + CMS + offer/lead system + credit-bureau/partner integrations with consent. Internal details are not public. | Side-by-side comparison works. Improve it by modelling personal annual value and distinguishing editorial score, fit score and eligibility. |
| [CardExpert](https://www.cardexpert.in/best-credit-cards-india/) | Long-form expert-curated lists grouped by entry, premium, travel, super-premium and HNI segments; detailed reviews and apply links. | Editorial depth, author identity, update date, comments/community, “best for” labels, income/spend guidance. | Editorial CMS and affiliate links are plausible; no claim is made here about a private recommendation database. | Human expertise and nuanced reward valuation build trust. Preserve this depth in structured rule notes and changelogs. |
| [CreditMantri](https://www.creditmantri.com/credit-card/) | Mobile-number-led eligibility start, card catalogue, issuer partners, personalized-match positioning and credit-score ecosystem. | Digital-process claims, card carousel/list, fees, application CTAs and educational content. | Likely catalogue + lead routing + bureau-enabled eligibility products, subject to consent and partner terms. | Do not make “personalized” a black box; expose the factors and confidence level. Avoid unsupported approval-rate claims. |
| [Wishfin](https://www.wishfin.com/credit-cards/) | Professional details (income, occupation, employer, city), WhatsApp/application paths, AI-advisor entry and customized-card lists. | Income-led form, category filters, card cards with fees and benefits, application CTAs. | Likely rule/partner matching layered on a catalogue and lead-routing operation. Private AI/ranking details are not public. | Conversational help is useful, but deterministic calculations should remain inspectable and reproducible. |

### Shared market patterns

- **Lead capture appears early**, commonly phone number, employment and income.
- **Catalogues and “top cards” editorial pages coexist.** One is transactional; the other brings search traffic and explains categories.
- **Comparison is usually feature-based**, while realized annual value often remains the user’s manual calculation.
- **Eligibility and pre-approved language is commercially powerful**, but approval remains the issuer’s decision.
- **Reward values are hard to compare** because one point may have different values by redemption route, transfer partner and cap.
- **Data goes stale quickly.** Devaluations, lounge-spend conditions, fee waivers, exclusions and limited-time offers create a versioning problem.

### Defensible opportunity

Build a **trust and calculation layer**, not merely an application marketplace:

- no-login result preview;
- coverage disclosure (“8 of 150+ cards modeled” in early stages);
- product facts with `effective_from`, `last_verified_at`, source URL and reviewer;
- reproducible annual value calculation;
- “why this / why not this” explanations;
- commission-independent default ranking, with sponsored placements visually separated;
- change alerts for users who save a card portfolio later.

---

## 3. User experience and information architecture

### Primary surfaces

1. **Configure:** one-minute profile: spend, category split, income band, credit-profile band, fee comfort and travel needs.
2. **Compare:** ranked results aligned on annual value, fee, rewards, eligibility signal and important limitations.
3. **Inspect:** detailed rule sheet for one card: caps, excluded merchant categories, point valuations, milestones and official sources.
4. **Learn:** focused guides for cashback, travel, fuel, UPI/RuPay, secured cards and first-card users.
5. **Portfolio (later):** cards already owned, renewal dates, waiver progress and “which card for this purchase?” routing.

### Recommended onboarding questions

Ask only inputs that materially change rank:

- location/pincode only when issuer serviceability requires it;
- employment type and monthly/annual income band;
- broad credit profile: new, fair, good, unknown (do not force a bureau pull);
- monthly category spends: online retail, grocery, dining, travel, fuel, utilities, UPI, offline/general and rent/education/government where exclusions differ;
- preferred reward type: cash, simple points, airline/hotel transfer, merchant ecosystem;
- annual-fee ceiling and willingness to hit a spend waiver;
- domestic/international lounge need and approximate trips;
- cards already held and issuer/application recency (later, for duplicate and velocity rules).

### Result-card content

Every result should show:

- personalized match score and its factor breakdown;
- estimated gross reward value, fee, waiver assumption and net value;
- top two reasons for the rank;
- “watch-outs” (cap, exclusions, transfer-value assumption, ecosystem lock-in);
- eligibility confidence as **strong / possible / weak / unknown**, never an approval probability unless contractually and statistically validated;
- official issuer link and last verification date;
- affiliate/commercial disclosure near the action, not hidden in a footer.

### Trust and anti-dark-pattern rules

- Never label a card “best” without a visible profile or methodology.
- Never say “guaranteed,” “instant approval” or “pre-approved” unless the issuer/authorized process has made that exact determination.
- Do not pre-check marketing consent.
- Do not bundle a credit-bureau pull into acceptance of general terms.
- Show results before optional phone-number capture.
- Do not create fake scarcity countdowns.
- Separate sponsored inventory from organic rank.
- Allow deletion/export of saved profile data.
- Keep a public correction channel and card-data changelog.

---

## 4. Recommendation engine

### Separate three outputs

1. **Product fit:** Does the reward structure match the spending pattern and preferences?
2. **Estimated economics:** What is the likely annual rupee value after fees?
3. **Eligibility confidence:** Are known broad issuer requirements compatible? This is not approval.

A card can have high product fit but low eligibility confidence. Do not hide it; explain the trade-off and offer an accessible alternative.

### Production value model

For card `c` and user category spends `s_k`:

```text
gross_rewards(c) = Σ_k reward_value(c, k, s_k)
                   + achievable_milestone_value(c)
                   + welcome_value(c, year)
                   + valued_perks(c, user)

net_value(c) = gross_rewards(c)
               - annual_fee_after_waiver(c, annual_spend)
               - redemption_costs(c)
               - expected_forex_cost(c, foreign_spend)
```

`reward_value` cannot be a single percentage field. It is a rules engine that should support:

- spend slabs;
- monthly/quarterly/annual caps;
- merchant/merchant-category inclusions and exclusions;
- transaction-size minimums and rounding;
- point earn rate and point-to-rupee value by redemption route;
- bonus portals and co-brand ecosystems;
- milestone thresholds;
- expiry;
- reversal/refund behavior;
- taxes on fees;
- lounge conditions tied to prior-quarter spend.

### Suggested rank composition

The prototype uses an intentionally simple demonstrator:

| Component | Weight | Production interpretation |
|---|---:|---|
| Net yearly value | 45% | Percentile-normalized among covered cards; use conservative point value. |
| Category fit | 25% | Share of relevant spend receiving accelerated value. |
| Eligibility confidence | 20% | Rules compatibility and data completeness, not approval probability. |
| Preference fit | 10% | Fee ceiling, simplicity, lounge and reward-type preferences. |

Production should show a confidence interval or scenario range rather than false precision:

- **Conservative:** cash-like redemption, no uncertain milestone.
- **Expected:** user’s chosen redemption route and likely milestones.
- **Optimized:** best plausible transfer/portal value, clearly labeled.

### Bias controls

- Organic score must not include affiliate commission.
- If only partner cards can be applied for, still allow non-partner cards in rank or clearly label catalogue coverage.
- Log score-input versions so an old recommendation can be reproduced.
- Run rank-parity tests by income band, employment type and new-to-credit status.
- Human review is required for unusually high calculated returns.

---

## 5. Database and service design

### Recommended stack

- **PostgreSQL** for normalized, versioned product facts and audit history.
- **Object storage** for source PDFs/screenshots/terms snapshots with content hashes.
- **Search index** (Postgres full-text initially; OpenSearch later) for editorial discovery.
- **Queue/workers** for scheduled source checks, diffing and reviewer tasks.
- **Rules evaluator** as a versioned service/library with deterministic tests.
- **Analytics warehouse** only after consent-safe event instrumentation is defined.

Avoid treating a spreadsheet or unversioned JSON file as the production source of truth. They are acceptable for initial editorial ingestion but not for auditability.

### Core relational model

```sql
issuers (
  id, name, legal_name, website_url, active
)

cards (
  id, issuer_id, canonical_name, network, variant,
  secured, cobranded, status, application_url
)

card_versions (
  id, card_id, effective_from, effective_to,
  joining_fee_minor, annual_fee_minor, fee_tax_rate,
  waiver_spend_minor, min_income_minor,
  source_id, verified_at, verified_by, review_status
)

reward_programs (
  id, card_version_id, currency_name,
  default_point_value_minor, expiry_months
)

reward_rules (
  id, reward_program_id, category_id, merchant_filter,
  earn_numerator, earn_denominator_minor,
  value_multiplier, cap_minor, cap_period,
  min_txn_minor, rounding_rule, exclusion_expression,
  rule_priority, effective_from, effective_to
)

benefits (
  id, card_version_id, type, quantity, period,
  estimated_value_minor, condition_expression, notes
)

eligibility_rules (
  id, card_version_id, employment_type, min_income_minor,
  min_age, max_age, geography_expression,
  credit_profile_hint, secured_deposit_min_minor,
  evidence_strength, notes
)

sources (
  id, url, source_type, issuer_owned,
  fetched_at, content_hash, archive_object_key
)

affiliate_offers (
  id, card_id, partner_id, destination_url,
  payout_model, starts_at, ends_at, disclosure_text
)

recommendation_runs (
  id, anonymous_profile_id, ruleset_version,
  catalogue_snapshot_at, created_at
)

recommendation_results (
  run_id, card_version_id, rank, fit_score,
  eligibility_confidence, gross_value_minor,
  net_value_minor, explanation_json
)
```

Store money in integer paise/minor units. Keep issuer facts separate from editorial interpretation. Use `effective_from/effective_to` rather than overwriting terms.

### Data categories and provenance

| Data | Best source | Automation realism |
|---|---|---|
| Fees, waiver, APR, forex markup | Issuer MITC / schedule of charges / product page | Fetch + diff; human verification required. |
| Reward earn rules, caps, exclusions | Issuer reward T&C PDFs/product pages | Often semi-structured; parser-assisted editorial ingestion. |
| Lounge entitlement/conditions | Issuer/network/benefit T&C | High change risk; human verification and dated version. |
| Eligibility | Issuer public criteria and partner feed | Public rules are incomplete; store evidence strength. |
| Application/serviceability | Issuer or affiliate partner API/feed | Usually commercial integration; do not scrape application flows. |
| Point valuation | Issuer redemption catalogue/transfer table plus editorial scenarios | Multiple values; store by redemption method, not one universal value. |
| Popularity/reviews | First-party, consented events and moderated reviews | Never confuse popularity with quality. |

There is no known comprehensive, stable, public India-wide API that supplies all card terms, eligibility, exclusions and live affiliate availability. Expect a hybrid of issuer documents, editorial review and contracted partner feeds.

### Update workflow

1. Register official source URL and expected check cadence.
2. Fetch source, store hash and archived copy.
3. Diff against prior version; classify fee/reward/eligibility/language changes.
4. Create a pending card version—never mutate the published version directly.
5. Require reviewer confirmation for material changes.
6. Run golden-profile regression tests and flag rank changes.
7. Publish with `effective_from`, reviewer and changelog.
8. Expire stale cards/offers automatically when evidence is too old.

Suggested freshness SLO: critical fees/reward caps 7 days after detected change; all active cards re-verified at least every 30–60 days, with higher frequency for volatile/partner cards.

---

## 6. Privacy, consent and regulatory product requirements

This is product research, not legal advice; engage Indian counsel before launch.

### RBI credit-card conduct

The RBI FAQ on the **Master Direction — Credit Card and Debit Card: Issuance and Conduct Directions, 2022** states, among other things:

- unsolicited cards are prohibited and prior explicit consent is required;
- activation is customer-initiated, with OTP-based consent rules for cards not activated within the stated period;
- interest/late-fee treatment applies to adjusted outstanding amounts as described by RBI;
- over-limit usage requires prior explicit consent;
- cardholders must have a route to issuer grievance redressal and then RBI Ombudsman escalation;
- a co-branding partner must not access/store card transaction data merely by virtue of that role; encrypted display directly from the issuer has specific limitations.

Source: [RBI FAQ, dated 7 March 2024](https://www.rbi.org.in/commonperson/English/Scripts/FAQs.aspx?Id=3580). Consult the underlying Master Direction and amendments for the authoritative legal text.

### Data protection

Design for the Digital Personal Data Protection framework and applicable rules:

- collect only necessary fields;
- use specific, understandable consent notices;
- separate recommendation use, bureau pull, application sharing and marketing;
- document processors and partner transfers;
- establish retention/deletion schedules and grievance handling;
- encrypt sensitive data in transit and at rest;
- avoid storing PAN, full card numbers or bureau reports unless essential and contractually/legally supported;
- allow anonymous comparison without persistent identity.

Official starting point: [Digital Personal Data Protection Act, 2023 — MeitY](https://www.meity.gov.in/data-protection-framework).

### Bureau and eligibility integrations

A credit score/report flow requires a lawful, consented arrangement with authorized parties and should not be simulated by a generic “AI approval score.” Keep soft profile matching available without a bureau pull. If bureau data is introduced, log consent artifact, purpose, partner, timestamp and retention policy.

---

## 7. UI direction implemented

The prototype is a **Compare-first** surface with a secondary **Configure** panel:

- warm neutral canvas with one green action accent;
- no generic centered hero/feature-tile composition;
- persistent desktop questionnaire and single-column mobile layout;
- visibly ranked card rows rather than decorative tiles;
- estimated net value and fit score in the same scan line;
- accessible form labels, focus states, 44px-class touch targets and reduced-motion support;
- comparison modal for up to three cards;
- persistent disclaimers and issuer verification links.

### Deliberate prototype simplifications

- only eight sample cards;
- broad category shares rather than a full spend allocation editor;
- point values represented as approximate effective rates;
- some caps simplified to an annual model;
- GST, welcome-benefit timing, milestones, detailed exclusions and merchant-category codes are not fully modeled;
- income and credit profile are broad signals only;
- data is embedded in the browser rather than backed by PostgreSQL.

These are appropriate for validating the interaction model, not for public financial recommendations.

---

## 8. MVP roadmap

### Phase 1 — trustworthy calculator

- 25–40 high-demand cards across cashback, travel, fuel, RuPay/UPI, secured and premium segments;
- versioned Postgres catalogue;
- detailed spend allocation and conservative/expected/optimized scenarios;
- card-detail rule sheet and source history;
- anonymous recommendations and shareable result snapshot;
- editorial admin/review workflow;
- automated regression tests for reward caps and waivers.

### Phase 2 — partner and retention layer

- explicit affiliate disclosures and partner feeds;
- saved profile, current-wallet optimizer and renewal alerts;
- optional consented eligibility/pre-qualified-offer integration;
- portfolio “best card for this purchase” routing;
- terms-change notifications.

### Phase 3 — defensibility

- verified user correction loop;
- issuer data partnerships;
- public methodology and coverage audit;
- recommendation outcome measurement without pushing unnecessary applications;
- multilingual education (Hindi plus priority regional languages).

### KPIs that do not reward harmful behavior

- recommendation completion rate;
- percentage viewing “why this card” or comparison;
- data freshness and correction turnaround;
- user-reported expected vs realized value;
- application quality/issuer acceptance where lawfully available;
- repeat usage for wallet optimization;
- complaint rate and consent withdrawal completion time.

Do not make raw application clicks the sole north-star metric; it creates incentives to overstate eligibility and promote high-commission cards.

---

## 9. Sources reviewed

1. [Reserve Bank of India — FAQs on Master Direction (Credit Card and Debit Card — Issuance and Conduct Directions, 2022)](https://www.rbi.org.in/commonperson/English/Scripts/FAQs.aspx?Id=3580), dated 7 March 2024, accessed 18 July 2026.
2. [BankBazaar — Credit Cards](https://www.bankbazaar.com/credit-card.html), accessed 18 July 2026.
3. [Paisabazaar — Credit Cards / top cards](https://www.paisabazaar.com/credit-card/top-10-credit-cards-in-india/), accessed 18 July 2026.
4. [CardExpert — Best Credit Cards in India](https://www.cardexpert.in/best-credit-cards-india/), page showed update 11 April 2026, accessed 18 July 2026.
5. [CreditMantri — Credit Cards](https://www.creditmantri.com/credit-card/), accessed 18 July 2026.
6. [Wishfin — Credit Cards](https://www.wishfin.com/credit-cards/), accessed 18 July 2026.
7. [MeitY — Data Protection Framework](https://www.meity.gov.in/data-protection-framework), official legal-policy starting point.
8. Issuer verification links are attached to each sample card inside `index.html`; product terms should be re-checked before any launch.
9. [RBI — Master Direction: Credit Card and Debit Card — Issuance and Conduct Directions, 2022](https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300), updated 7 March 2024.
10. [RBI — bank-wise ATM/POS/card statistics](https://www.rbi.org.in/Scripts/ATMView.aspx), useful for issuer activity rather than product terms.
11. [MeitY — Digital Personal Data Protection Act, 2023, official PDF](https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf).
12. [MeitY — Digital Personal Data Protection Rules, 2025, official PDF](https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf).
13. [CCPA — Guidelines for Prevention and Regulation of Dark Patterns, 2023](https://consumeraffairs.nic.in/sites/default/files/file-uploads/latestnews/Guidelines%20for%20Prevention%20and%20Regulation%20of%20Dark%20Patterns%2C%202023.pdf).
14. [W3C — What’s New in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/).

## 10. Research limitations

- Public pages can change, personalize content or block automated access.
- Competitor internal schemas, models, partner contracts and commission logic are generally private; this document does not claim access to them.
- Issuer product terms are volatile and sometimes split among product pages, MITC documents and reward T&Cs.
- Regulatory requirements may have changed after a cited source’s publication date; production launch requires current legal review and direct review of RBI/MeitY texts and amendments.
