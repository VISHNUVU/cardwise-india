# CardWise card-profile schema and evidence policy

**Jurisdiction:** India  
**Snapshot date:** 2026-07-18  
**Scope:** consumer credit-card products found on the 17 reviewed issuer surfaces in `CARD_CATALOGUE_2026-07-18.json`.

## Purpose

A profile is a learning record, not a recommendation, approval estimate, or substitute for an issuer’s current MITC/KFS/reward terms. It must help a user understand:

1. what the product is;
2. what is currently supported by evidence;
3. what is unknown;
4. what economic and eligibility questions matter;
5. whether a detailed, reproducible reward model exists; and
6. where to verify the facts.

## Quality layers

| Layer | Meaning | Allowed UI |
|---|---|---|
| Catalogue baseline | Official issuer surface supports identity/catalogue presence | Search, categories, source link, learning checklist |
| Partially enriched | One or more material fields have direct evidence | Supported facts plus visible unknowns |
| Detailed reward model | Fees, rates, caps, exclusions and valuation assumptions are normalized | Directional personalized calculations with trace |
| Stale/withdrawn | Repeatedly unavailable or no longer found | Historical research only; no application/recommendation CTA |

Catalogue presence is not the same as complete term verification or confirmation that new applications are open.

## Profile object

```json
{
  "id": "stable-provider-and-product-id",
  "schemaVersion": "1.0",
  "asOf": "YYYY-MM-DD",
  "identity": {
    "issuer": "...",
    "name": "...",
    "catalogueStatus": "listed_on_official_catalog",
    "officialUrl": "https://...",
    "catalogueUrl": "https://..."
  },
  "overview": "Evidence-aware educational summary",
  "discoveryCategories": ["travel"],
  "knownFacts": {
    "network": {"value": null, "status": "unknown"},
    "annualFeeInr": {"value": null, "status": "unknown"},
    "secured": {"value": null, "status": "unknown"},
    "cobranded": {"value": false, "status": "official_catalogue"},
    "detailedRewardModelAvailable": {"value": false, "status": "platform_capability"}
  },
  "learningGuide": {
    "worthInvestigatingIf": [],
    "mayBePoorFitIf": [],
    "questionsBeforeApplying": [],
    "fullPaymentReminder": "..."
  },
  "missingMaterialFacts": [],
  "contractualTerms": {
    "cost": {"joiningFeeInr": null, "annualFeeInr": null, "renewalFeeWaiver": null, "financeChargeApr": null},
    "rewards": {"currency": null, "baseEarnRule": null, "acceleratedEarnRules": [], "caps": [], "exclusions": [], "redemptionOptions": []},
    "benefits": {"welcomeBenefits": [], "milestones": [], "domesticLounge": null, "internationalLounge": null, "fuelSurchargeWaiver": null},
    "eligibility": {"minimumAge": null, "minimumIncomeInr": null, "publishedCriteria": [], "fdRequirement": null},
    "availability": {"cataloguePresence": "listed_on_official_catalog", "newApplicationsOpen": null, "invitationOnly": null}
  },
  "evidence": [],
  "profileCompleteness": {
    "score": 0,
    "label": "catalogue baseline",
    "meaning": "Coverage, not product quality"
  }
}
```

## Null and boolean semantics

- `null`: unknown or not directly supported by reviewed evidence.
- `false`: evidence supports a negative value.
- `0`: evidence supports a numeric zero.
- Empty array: reviewed and no entries, only when evidence supports that conclusion.

Never turn an unknown fee into lifetime-free, an unknown lounge benefit into no lounge, or missing eligibility into likely approval.

## Material fact groups for future enrichment

### Cost

- joining fee before GST;
- annual/renewal fee before GST;
- first-year-free versus unconditional lifetime-free;
- renewal-waiver threshold, period, and eligible-spend definition;
- APR/finance charges;
- rent, utility, education, wallet and fuel transaction charges;
- redemption fees and supplementary-card fees.

### Rewards

- reward currency and conservative redemption value;
- base rate and category/channel/merchant rules;
- caps, reset periods, minimum transactions and rounding;
- excluded MCCs and transaction types;
- milestones, expiry, reversal and posting rules;
- transfer partners and transfer ratios.

### Travel and benefits

- domestic and international lounge visit counts;
- spend gates and lookback period;
- guest/add-on eligibility;
- forex markup;
- insurance, concierge, golf and hotel conditions.

### Eligibility

- published age, income and employment rules;
- issuer relationship or invite/upgrade requirement;
- geography/serviceability;
- FD requirement and credit-limit ratio for secured cards;
- evidence source and last-verified date.

Eligibility evidence must remain separate from undisclosed issuer underwriting. Never label it an approval probability without validated outcome data.

## Field-level evidence

Every future contractual fact should carry:

```json
{
  "value": 999,
  "currency": "INR",
  "effectiveFrom": null,
  "effectiveTo": null,
  "observedAt": "2026-07-18T00:00:00+05:30",
  "status": "verified",
  "source": {
    "url": "https://issuer/...",
    "documentType": "MITC",
    "locator": "page 4, Annual Fees",
    "contentHash": "sha256:..."
  },
  "review": {
    "method": "manual",
    "reviewer": null,
    "reviewedAt": null
  }
}
```

## Source hierarchy

1. Issuer MITC/KFS/schedule of charges.
2. Issuer reward-program terms and benefit terms.
3. Issuer product page and application page.
4. Issuer catalogue or sitemap.
5. Secondary marketplace/editorial source for discovery only, visibly marked for review.

Conflicts should not be silently resolved. Preserve both observations, prefer the more contractual/current source for publishing, and open a review task.

## Refresh policy

- Save immutable source bytes and hashes.
- Diff monetary terms, caps, exclusions, eligibility and availability.
- Route material changes to human review.
- Publish append-only versions.
- Show last checked and stale status to users.
- Re-run reward-model and recommendation regression tests after every approved material change.

## Current generated artifacts

- `CARD_PROFILES_2026-07-18.json`: 267 baseline learning profiles.
- `card-profile-data.js`: deterministic browser representation.
- `CARD_CATALOGUE_2026-07-18.json`: source catalogue and coverage metadata.
- `CARD_PROFILES_ENRICHMENT_2026-07-18.json`: official excerpts for HDFC, SBI, ICICI, Axis and IDFC FIRST.
- `CARD_ENRICHMENT_TARGET_ISSUERS_2026-07-18.json`: normalized source research for AU, IndusInd, Kotak, YES, RBL, HSBC and Standard Chartered.
- `PROVIDER_PROFILES_2026-07-18.json`: portfolio context for American Express, BOBCARD, Federal Bank and OneCard/FPL; never a substitute for card-level terms.

The canonical snapshot now attaches card-level official-source research to 230 profiles and provider context to 37 profiles. Candidate excerpts remain labelled for human review and are not silently converted into executable reward rules.

Baseline profiles intentionally contain learning questions and explicit missing facts. They become contractually “in-depth” only as product pages, MITCs, schedules and reward terms are attached field by field.