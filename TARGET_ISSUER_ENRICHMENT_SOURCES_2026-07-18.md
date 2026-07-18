# Target-issuer enrichment source notes

**Jurisdiction:** India  
**Checked:** 2026-07-18  
**Scope:** 103 cards in the existing 267-card CardWise official catalogue, across AU Small Finance Bank, IndusInd Bank, Kotak Mahindra Bank, YES BANK, RBL Bank, HSBC India and Standard Chartered India.

## Deliverable and semantics

- Machine-readable facts are in [`CARD_ENRICHMENT_TARGET_ISSUERS_2026-07-18.json`](CARD_ENRICHMENT_TARGET_ISSUERS_2026-07-18.json).
- Every requested fact is represented. Unsupported values are `{"value": null, "status": "unknown"}`; values were not inferred from card names or editorial tags.
- Each profile records the checked date, source URL, access result, locator, supported fields, network, secured/co-brand status, fees, rewards, caps/exclusions, lounge/spend gate, forex, fuel and published eligibility.
- `researchStatus=official_terms_enriched` means at least one economic or eligibility field was supported by the checked issuer material. It does **not** mean every term is complete.

## Coverage

| Issuer | Catalogue profiles | Profiles with supported economic/eligibility enrichment | Notes |
|---|---:|---:|---|
| AU Small Finance Bank | 25 | 0 | Product/catalogue URLs hit Cloudflare verification and HTTP 403 during this run. Existing catalogue identity, co-brand, network and secured facts were preserved; economics remain explicit unknown. |
| HSBC India | 7 | 7 | Individual official product pages supported fees, rewards/cashback, lounge, fuel/forex where stated, network and published eligibility. |
| IndusInd Bank | 22 | 22 | Official credit-card catalogue exposed product benefit summaries; unshown fees, detailed exclusions and eligibility remain unknown. |
| Kotak Mahindra Bank | 24 | 20 | Official catalogue exposed many fees, earn summaries, fee waivers, lounge and forex statements. Ambiguous/interleaved products were deliberately left unknown. |
| YES BANK | 9 | 0 | Official catalogue was accessible but implemented as Oracle site-page references without stable product/terms links in the retrieved surface; no economics were inferred. |
| RBL Bank | 7 | 5 | Official Schedule of Charges supported fees for Icon, World Safari, Platinum Maxima, Platinum Maxima Plus, Shoprite and issue-date-dependent Cookies terms. Cookies is not counted as a single numeric fee because the schedule distinguishes cohorts. |
| Standard Chartered India | 9 | 4 | Product terms supported Rewards, EaseMyTrip, Smart and Ultimate. Remaining catalogue cards retain explicit unknowns unless a catalogue identity/network fact was already supported. |

## Official source registry

### AU Small Finance Bank

- Catalogue: https://www.au.bank.in/personal-banking/credit-cards
- Individual official product URLs are retained per profile. Access was blocked by Cloudflare during this check; this is recorded rather than bypassed with third-party claims.

### IndusInd Bank

- Catalogue/product summaries: https://www.indusind.bank.in/in/en/personal/cards/credit-card.html
- Schedule of charges: https://www.indusind.bank.in/in/en/personal/schedule-of-charges.html
- Terms: https://www.indusind.bank.in/in/en/personal/terms-and-conditions.html

### Kotak Mahindra Bank

- Catalogue/product summaries: https://www.kotak.bank.in/en/personal-banking/cards/credit-cards.html
- Credit-card MITC/cardmember agreement: https://www.kotak.bank.in/en/personal-banking/cards/credit-cards/mitc-and-ca.html
- Key Fact Statements: https://www.kotak.bank.in/en/personal-banking/cards/credit-cards/kfs.html

### YES BANK

- Catalogue: https://www.yes.bank.in/personal-banking/yes-individual/cards/credit-cards

### RBL Bank

- Catalogue: https://www.rbl.bank.in/personal-banking/cards/credit-cards
- MITC: https://webassets.rbl.bank.in/document/Credit%20Cards/RBL-MITC-final.pdf
- Schedule of Charges: https://webassets.rbl.bank.in/document/Credit%20Cards/CardsScheduleCharges.pdf

### HSBC India

- Catalogue: https://www.hsbc.co.in/credit-cards/
- Rates and fees hub: https://www.hsbc.co.in/help/rates-and-fees/
- Product pages are recorded separately per profile, including Taj, TravelOne, Live+, Premier, Visa Platinum, RuPay Platinum and RuPay Cashback.
- Time-sensitive item: the RuPay Cashback product page states 0% promotional forex markup only through **2026-07-31**; the profile flags this for re-check.

### Standard Chartered India

- Catalogue: https://www.sc.bank.in/credit-cards/
- Rewards terms: https://av.sc.com/in/content/docs/in-rewardscard-product-terms-and-conditions.pdf
- EaseMyTrip terms: https://av.sc.com/in/content/docs/in-easemytrip-product-terms-and-conditions.pdf
- Smart terms: https://av.sc.com/in/content/docs/in-smartcard-product-terms-and-conditions.pdf
- Ultimate terms: https://av.sc.com/in/content/docs/in-ultimate-credit-card-tnc.pdf
- Platinum Rewards terms: https://av.sc.com/in/content/docs/in-sc-platinum-rewards-credit-card-tcs.pdf

## Important cautions

- Displayed reward statements are contractual descriptions, not CardWise point valuations.
- MCC classification, supplementary-card aggregation, posting/reversal timing, GST, card variant/network, promotional windows and issuer underwriting can materially change outcomes.
- A null fee does not mean lifetime-free; it means no supported numeric fee was extracted from the checked official material.
- Published eligibility is an application criterion, not an approval prediction.
