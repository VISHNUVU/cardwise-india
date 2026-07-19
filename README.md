# CardWise India

A working, India-first credit-card recommendation prototype focused on transparent ranking rather than lead capture.

## Live app

**https://vishnuvu.github.io/cardwise-india/**

## Run locally

```bash
python3 -m http.server 4173
```

Then open <http://localhost:4173>.

No build step or package install is required.

## Verify

```bash
python3 validate_profiles.py
python3 tests/test_decision_details.py -v
python3 qa_test.py
```

## What works

- detailed two-minute form with seven monthly spending categories, reward goal, income band, credit profile, card journey, fee comfort, lounge, international-use, UPI and network preferences;
- deterministic ranking across seven currently allow-listed reward models;
- evidence-aware product-fit recommendations across all 267 catalogue cards, with visible scores, reasons and evidence-confidence labels;
- questionnaire inputs update both the seven detailed-math rankings and the market-wide catalogue ranking;
- detailed annual-value models use the entered category amounts instead of an assumed category split;
- market-wide product-fit scoring uses dominant spending, stated goal, known fee comfort, secured/starter signals, lounge, UPI, international-use and network preferences plus evidence coverage; it is explicitly not an approval prediction;
- official-source discovery catalogue with 267 products across 16 issuers, after reviewing 17 issuer surfaces, in [`catalog-data.js`](catalog-data.js);
- full normalized research dataset and coverage metadata in [`CARD_CATALOGUE_2026-07-18.json`](CARD_CATALOGUE_2026-07-18.json);
- 267 evidence-aware learning profiles in [`CARD_PROFILES_2026-07-18.json`](CARD_PROFILES_2026-07-18.json) and [`card-profile-data.js`](card-profile-data.js).
- Cashback percentage evidence on every individual profile: 52 cards currently have 136 explicit percentage-bearing official-source records; the other 215 display “No cashback percentage verified” rather than a fabricated 0%.
- Cashback records preserve percentage, merchant/category clues, channel, cap/spend/exclusion flags, offer type, validity text, source description, official URL, checked date and review state. Reward points are not mislabeled as cashback.
- card-level official-source research attached to 230 profiles, including 53 supported annual fees and 3,296 source-ledger entries;
- provider-level context and freshness alerts for the remaining American Express, BOBCARD, Federal Bank and OneCard/FPL portfolio in [`PROVIDER_PROFILES_2026-07-18.json`](PROVIDER_PROFILES_2026-07-18.json);
- raw issuer enrichment snapshots in [`CARD_PROFILES_ENRICHMENT_2026-07-18.json`](CARD_PROFILES_ENRICHMENT_2026-07-18.json) and [`CARD_ENRICHMENT_TARGET_ISSUERS_2026-07-18.json`](CARD_ENRICHMENT_TARGET_ISSUERS_2026-07-18.json);
- per-card Learn modal covering known facts, structured offer conditions, fees/waivers, reward-conversion status, year-one versus ongoing value, unknowns, fit questions, borrowing warning, evidence and profile completeness;
- profile contract and field-provenance policy in [`PROFILE_SCHEMA.md`](PROFILE_SCHEMA.md);
- implementation-ready profile information architecture in [`PROFILE_PAGE_IA.md`](PROFILE_PAGE_IA.md);
- progressive India-specific filtering specification in [`FILTER_DESIGN.md`](FILTER_DESIGN.md);
- catalogue/reward-model separation audit in [`IMPLEMENTATION_AUDIT.md`](IMPLEMENTATION_AUDIT.md);
- search plus issuer, network, use-case, fee, minimum recorded cashback offer, cashback-record-available, lounge, UPI, forex, secured, co-brand, detailed-model and official-fee filters;
- highest-recorded-cashback-offer sorting and condition-aware cashback labels;
- best-product-fit sorting across the full catalogue;
- shareable `#card=<canonical-id>` profile links with a Copy link control;
- estimated ongoing yearly rewards, effective fee and net value, while year-one value remains explicitly unmodeled until welcome-benefit value is normalized;
- separate eligibility compatibility signal inside the score;
- explanations for each rank;
- sorting by match, yearly value or fee;
- add up to three cards and compare side by side;
- responsive/mobile layout and keyboard-accessible modal;
- direct issuer verification links;
- full research hub in [`RESEARCH.md`](RESEARCH.md);
- 11-product competitive review in [`COMPETITIVE_RESEARCH.md`](COMPETITIVE_RESEARCH.md);
- recommendation, UX and 14 acceptance tests in [`METHODOLOGY.md`](METHODOLOGY.md);
- source-backed ingestion and governance design in [`DATA_ARCHITECTURE.md`](DATA_ARCHITECTURE.md);
- production-oriented PostgreSQL model in [`schema.sql`](schema.sql);
- reproducible browser/mobile test in [`qa_test.py`](qa_test.py) and results in [`QA.md`](QA.md).

## Prototype warning

The discovery catalogue is broad but is **not claimed to be permanently exhaustive**. It separates official-source product discovery from the seven catalogue cards currently linked to normalized reward maths. DBS was reviewed but contributed zero rows because no current consumer-card product could be verified on its accessible official surface. Product terms change often, and the simplified calculator does not fully model GST, all reward caps, exclusions, merchant category codes, milestones, welcome-benefit timing, transfer-partner values or issuer underwriting. Do not publish it as financial advice or an approval engine without a versioned data pipeline, issuer-term verification and legal/compliance review.

## Suggested production architecture

- PostgreSQL catalogue with effective-dated card versions and source provenance;
- archived issuer terms/PDFs in object storage;
- deterministic, versioned reward-rules evaluator;
- source-diff and human review workflow;
- affiliate offers kept separate from organic ranking;
- consented identity/eligibility services added only after anonymous comparison is useful.
