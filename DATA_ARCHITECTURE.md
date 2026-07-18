## Outcome

Build the platform around a **versioned, source-backed card catalog and deterministic rules engine**, not a flat `cards` table. India does not have a universal, open credit-card product API. Public acquisition is largely issuer webpages/PDFs; eligibility and affiliate conversion data generally require manual review or commercial partnerships.

## 1. Authoritative sources

### RBI and government

- **RBI Credit Card and Debit Card – Issuance and Conduct Directions, 2022**, updated March 7, 2024  
  https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300
- **RBI bank-wise ATM/POS/card statistics** — useful for identifying active issuers and validating market presence, but not card terms  
  https://www.rbi.org.in/Scripts/ATMView.aspx
- **RBI statistics index**  
  https://www.rbi.org.in/Scripts/Statistics.aspx
- **RBI Account Aggregator Directions**, updated September 6, 2024  
  https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=10598
- **Digital Personal Data Protection Act, 2023 — official MeitY PDF**  
  https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf
- **Digital Personal Data Protection Rules, 2025 — official Gazette/MeitY PDF**  
  https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf
- **MeitY DPDP Rules page**  
  https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025

The 2025 Rules use phased commencement: Rules 1, 2 and 17–21 commenced on publication on November 13, 2025; Rule 4 is scheduled one year later; Rules 3, 5–16, 22 and 23 are scheduled eighteen months after publication. The product should implement the full target-state controls now rather than rely on transition periods.

### Issuer source examples

- HDFC Bank card catalog  
  https://www.hdfc.bank.in/credit-cards
- SBI Card catalog  
  https://www.sbicard.com/en/personal/credit-cards.html
- SBI Card MITC  
  https://www.sbicard.com/en/most-important-terms-and-conditions.page
- SBI Card application entry point  
  https://www.sbicard.com/en/eapply.page
- Axis Bank card catalog  
  https://www.axis.bank.in/cards/credit-card
- Axis Bank MITC PDF  
  https://www.axis.bank.in/docs/default-source/default-document-library/mitc-credit-cards.pdf
- Axis Bank eligibility guidance  
  https://www.axis.bank.in/blogs/credit-card/credit-card-eligibility
- American Express India card catalog  
  https://www.americanexpress.com/in/credit-cards/
- Axis API developer portal: its credit-card package currently shows **restricted access**, illustrating that bank APIs are partnership products, not an open national catalog  
  https://apiportal.axis.bank.in/portal/product/36541  
  https://apiportal.axis.bank.in/portal/become-partner

## 2. Canonical card data model

Separate stable product identity from changeable terms.

### Stable entities

- `issuer`
  - legal name, display name, RBI entity type, RBI/bank code, regulator, website, active status
- `card_product`
  - issuer, canonical name, slug, consumer/business/corporate type, secured/unsecured, co-brand partner, launch/withdrawal dates
- `card_variant`
  - network (`Visa`, `Mastercard`, `RuPay`, `Amex`, etc.), tier, physical/virtual, domestic/international, contactless, UPI-on-credit availability
- `reward_program`
  - issuer-owned or partner program, reward currency, expiry policy
- `merchant`, `merchant_group`, `spend_category`, `mcc`
- `transfer_partner`, `lounge_program`, `insurance_provider`
- `source_document`

Do not model Visa/Mastercard/RuPay variants as independent products unless their pricing or benefits materially differ.

### Versioned product terms

`card_terms_version` should contain:

- `valid_from`, `valid_to`
- joining, annual, renewal and add-on fees
- GST applicability
- APR/finance-charge variants
- cash-advance fee and interest start rule
- late-payment slabs, over-limit and forex markup
- rent, utility, education, wallet, fuel or government-payment charges
- interest-free period range
- minimum-amount-due rule
- credit/cash limit descriptions
- fee-waiver predicates
- source and review status

RBI requires APR and annual fee to receive equal prominence, clear charge calculation examples, no hidden “free card” charges, prospective charge changes with at least one month’s notice, and detailed MITC disclosure. Therefore these fields cannot safely be reduced to one annual-fee number.

### Reward and benefit rules

Use typed rule tables plus a constrained predicate DSL/JSON, not prose alone:

```text
earning_rule
  reward_program_id
  reward_type                points | cashback | miles
  reward_amount
  spend_amount
  category_id / merchant_id / mcc_set_id
  channel                    online | offline | issuer_portal
  min_transaction
  max_reward
  cap_period                 transaction | statement | month | quarter | year
  spend_threshold
  rounding_unit
  priority
  stackable
  valid_range
```

Also model:

- `earning_exclusion`: MCC/category/merchant/transaction type
- `milestone_rule`: spend window, threshold, reward, reset semantics
- `redemption_option`: conversion ratio, minimum, increment, fee, transfer time
- `benefit_rule`: lounge quota, spend gate, guest charge, fuel waiver, concierge, insurance
- `promotional_offer`: explicit start/end dates and target segment
- `devaluation_event`: old/new terms and announcement/effective dates

Keep editorial point valuations separate from contractual facts:

```text
valuation_estimate(reward_currency, use_case, value_inr, methodology, as_of)
```

Reward computation must support caps, statement-cycle windows, thresholds, exclusions, rounding and rule priority. A single `reward_rate` column will produce incorrect recommendations.

### Eligibility

`eligibility_rule` should represent:

- age minimum/maximum
- Indian residency/NRI status
- salaried, self-employed or business categories
- income amount, frequency and gross/net basis
- serviceable city/pincode
- existing issuer relationship
- secured deposit amount
- bureau requirement, where explicitly stated
- invite-only/pre-approved flag
- required documents
- `hard | indicative | unknown`
- source, confidence and last verification

Issuer underwriting, bureau cut-offs, internal scorecards and credit limits are usually unpublished. Present results as **“likely eligible”**, never “approved” or “guaranteed,” unless an issuer returns a binding pre-qualified result. Do not invent income thresholds from competitor sites.

## 3. Issuer registry

Seed from:

1. RBI-regulated bank/NBFC lists and bank-wise card statistics.
2. Issuer legal entities.
3. Verified issuer product catalogs.

The system must distinguish brands from legal issuers, for example a bank, its card-subsidiary/NBFC, and a co-brand partner. Co-brand partners are not automatically issuers.

RBI requires co-branded marketing to display the issuer clearly. Co-brand partner involvement is generally limited to marketing/distribution and access to partner goods/services. The partner must not access or store transaction data merely because it is the co-brand; RBI permits encrypted display directly from the issuer under restrictive conditions.

## 4. Data acquisition reality

| Data | Best source | Acquisition | Human/partner requirement |
|---|---|---|---|
| Product identity/status | Issuer catalog | Weekly crawl | Human resolve renames/withdrawals |
| Fees/APR/MITC | Issuer MITC and schedule PDFs | PDF/HTML fetch, hash and extract | Mandatory review for changed clauses/slabs |
| Reward earn/exclusions | Product page plus reward T&C | Crawl and parse | High manual review; prose is irregular |
| Lounge/insurance | Issuer and benefit-provider terms | Weekly/monthly crawl | Manual reconciliation |
| Eligibility | Issuer eligibility/application pages | Crawl public facts | Hidden underwriting requires issuer/lead partner |
| Issuer activity | RBI card statistics | Monthly ingestion | Automated |
| Limited-time offers | Issuer/merchant pages | Daily crawl | Review segmentation and expiry |
| Application status/conversion | Issuer or affiliate network | Partner API/postback/report | Partner-only |
| Commission/payout | Affiliate contract/network | Partner feed | Partner-only and commercially confidential |
| Transaction history | User input, bank statements, or regulated AA flow | CSV/parser or AA partner | AA/FIU partnership and consent |
| Credit score/report | RBI-registered CIC/issuer | Licensed partner flow | Not public; permissible-purpose and consent controls |
| MCC assigned to a merchant | Network/acquirer/issuer result | Partner or observed transactions | Often unavailable before purchase |

### API conclusion

- No RBI API provides card names, fees, rewards, eligibility or affiliate links.
- Issuer public sites are primarily human-facing HTML/PDF sources.
- Some banks have developer portals, but card APIs may be restricted and designed for authenticated partners or servicing, not catalog syndication.
- Expect issuer-specific commercial integrations rather than a common Indian “credit card product API.”
- Public-site extraction must respect site terms, robots controls and copyright. Store factual normalized data and source hashes; avoid republishing entire documents.

## 5. Update and verification pipeline

1. Maintain a per-issuer source registry: product pages, MITC, fee schedule, reward T&C, offer pages.
2. Fetch on appropriate cadence using conditional requests where available.
3. Store immutable raw HTML/PDF in object storage with SHA-256, retrieval time, URL and HTTP metadata.
4. Extract candidate facts with parser name/version and exact source span/page.
5. Diff against the currently approved version.
6. Auto-approve only safe syntactic changes; route monetary, eligibility, cap, exclusion and withdrawal changes to review.
7. Publish a new append-only version with both:
   - `effective_from/effective_to`: when the issuer says the term applies.
   - `observed_from/observed_to`: when the platform knew it.
8. Re-run rule-engine regression scenarios and recommendation snapshots.
9. Mark stale cards when sources fail repeatedly; do not silently preserve old terms as current.
10. Retain correction history and issue user-facing “terms last checked” dates.

Prioritize daily checks for promotions, weekly checks for product/reward pages, monthly checks for broader MITC and RBI issuer statistics, plus event-driven processing of issuer/partner notifications.

## 6. Practical PostgreSQL design

Core tables:

```text
issuer
card_product
card_variant
card_terms_version
reward_program
earning_rule
earning_exclusion
milestone_rule
redemption_option
transfer_partner
benefit_rule
eligibility_rule
promotional_offer

source
source_document
source_snapshot
extracted_fact
fact_review
change_event

user_profile
consent_record
consent_event
recommendation_run
recommendation_result
calculation_trace

affiliate_program
affiliate_campaign
affiliate_link
click_event
conversion_event
payout_event
partner_import
```

Recommended implementation details:

- PostgreSQL range types/exclusion constraints to prevent overlapping approved versions.
- JSON predicates only for the variable condition tree; retain typed columns for rates, money, dates, caps and categories.
- Store money as integer paise plus currency.
- Use stable internal IDs; issuer URLs and names are mutable.
- Add `source_id`, exact citation locator, confidence and reviewer to every publishable fact.
- Create a materialized `current_card_catalog` view, while calculations reference immutable version IDs.
- Save complete `calculation_trace` data so every recommendation can explain fee, reward, cap and eligibility assumptions.
- Object storage holds raw documents; PostgreSQL holds metadata and extracted facts.
- Keep recommendation editorial weights separate from product facts.

## 7. Consent, privacy and financial-data constraints

A basic recommender can operate with coarse, optionally anonymous inputs:

- monthly spend by category
- travel/lounges preference
- fee tolerance
- broad income band and employment type
- city/pincode only when required

Avoid collecting PAN, Aadhaar, full card numbers, CVV, bank credentials, detailed bureau reports or raw statements unless a specific partner workflow genuinely requires them.

Implement:

- itemized notice by purpose and data category
- separate consent for recommendations, transaction import, issuer lead submission and marketing
- consent version, timestamp, UI text hash, channel and withdrawal events
- withdrawal as easy as consent
- processor/vendor registry and contracts
- purpose-based retention and erasure jobs
- encryption, least privilege, breach workflow and audit logs
- user access/correction/grievance paths
- no pre-ticked marketing or bundled consent

Account Aggregator data is not a general-purpose scraping shortcut. The RBI AA framework says customer financial information is not the AA’s property and cannot be used in other ways. A recommender should integrate through an appropriately regulated AA/FIU arrangement and use explicit, purpose-bounded consent; it should not claim direct AA access merely because it has an app.

Under RBI card directions, issuers may not reveal customer data without explicit consent stating purposes and recipient organizations. DSA/DMA disclosures must be limited to what is required, and outsourced card data sharing requires necessity and explicit consent. If the platform becomes an issuer’s agent, the issuer’s mis-selling, privacy and outsourcing controls will flow down contractually.

## 8. Affiliate attribution

Model attribution separately from product ranking.

Minimum fields:

```text
affiliate_campaign:
  partner, issuer, eligible_products, payout_model
  event_definition, attribution_window, dedupe_rule
  start/end, contract_version

click_event:
  click_id, campaign_id, product_version_id
  pseudonymous_session_id, timestamp, landing_url
  sub_id, consent_state

conversion_event:
  partner_event_id, click_id
  stage = lead | application | approved | issued | activated
  event_time, received_time, status, reversal_reason
```

Recommended flow:

1. Generate an opaque first-party `click_id`.
2. Pass only contract-approved `sub_id` values in the outbound link.
3. Record redirect and product-version context.
4. Ingest signed server-to-server postbacks or scheduled partner reports.
5. Verify signatures, timestamps, replay protection and idempotency.
6. Separate application, approval, issuance and activation because payouts may depend on different events.
7. Support reversals, duplicate leads and attribution-window disputes.
8. Do not put PAN, mobile number or email in query parameters.
9. Show a clear commission/sponsored disclosure and label promoted placement.
10. Keep an organic suitability score independent of commission; log any commercial boost.

Public affiliate-network pages demonstrate campaigns exist, but exact payouts and rules are volatile and not authoritative product terms. Treat those feeds as commercial data, not as a source for fees/rewards. Ordinary affiliate attribution is distinct from RBI “co-branding”; do not claim co-brand status without a supported issuer arrangement.

## Key build recommendation

Launch with a curated set of 30–50 high-demand cards and:

- issuer/RBI primary sources only for contractual facts
- weekly crawlers plus human review
- an append-only bitemporal rule store
- anonymous spend-profile recommendations
- redirect-only affiliate tracking
- no credit-bureau or transaction ingestion initially

Add partner eligibility, AA or application-status integrations only after issuer/regulated-provider contracts and purpose-specific consent controls are in place.

**Files modified:** none.  
**Issue encountered:** some government and bank pages block automated browsers or redirect domains; official direct PDFs and RBI master-direction pages remained accessible.