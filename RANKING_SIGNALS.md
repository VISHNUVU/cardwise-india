# CardWise India ranking signals

**Version:** 2026-07-20
**Scope:** deterministic product-fit ranking for 267 catalogue cards; detailed rupee-value ranking for seven normalized card models.

## Counting convention

A **decision input** is one independently entered field. Radio/select choices within one field count as one input, not one per option. Of 29 decision inputs, 28 can affect economic fit, product affinity, ordering, or a safety route. Monthly income is deliberately isolated as eligibility context and cannot alter ranking.

## 28 ranking signals + 1 eligibility context

### A. Spending — 12

1. Online shopping
2. Groceries
3. Dining
4. Travel
5. Fuel
6. Utilities and bills
7. Insurance
8. Rent and education
9. Healthcare
10. Railway and local transit
11. Movies and entertainment
12. Other spending

Derived without inflating the count:

- Total monthly and annual spend
- Largest spending category
- Category mix used by the seven normalized economic models

### B. Core profile and preferences — 9

13. Main goal
14. Monthly income band — eligibility context only; excluded from both ranking engines
15. Credit-history band
16. Card journey: first, additional, or replacement
17. Annual-fee comfort
18. Lounge preference
19. International-spending band
20. Credit-card-on-UPI preference
21. Preferred network

### C. Optional fine-tuning — 8

22. Repayment behavior
23. Reward-complexity tolerance
24. Preferred redemption method
25. Spend-based fee-waiver acceptance
26. Steady versus seasonal spending
27. Expected monthly credit-card UPI amount
28. Preferred merchant ecosystem
29. Existing lounge-benefit coverage

## Up to 14 card-side matching dimensions

The market-wide product-fit engine matches the profile against supported product facts and clearly editorial catalogue-affinity tags. Editorial tags can create discovery affinity but never contractual economics:

1. Spending/use-case categories
2. Main-goal category
3. Supported annual fee
4. Supported secured or FD-backed status
5. Lounge availability
6. RuPay / credit-on-UPI signal
7. Low/zero-forex signal
8. Supported network
9. Structured ongoing official-source cashback evidence
10. Editorial reward-complexity affinity
11. Editorial redemption-type affinity
12. Recorded cashback-cap presence
13. Co-brand or merchant-ecosystem identity
14. Evidence coverage and detailed-model availability — confidence/tie-break only

Evidence completeness is used only as a tie-break and confidence label. It does not turn an unknown benefit into a positive product fact.

## Signal taxonomy — counts are not additive

These layers overlap, so they must not be summed into an inflated “total signals” claim:

| Layer | Count | Convention |
|---|---:|---|
| Direct user decision inputs | 29 | 28 ranking/safety inputs plus one separate income context |
| Derived user-profile values | 4 | Monthly total, annual total, dominant category and 12-category spend mix |
| Card-side matching dimensions | Up to 14 | The dimensions listed above; availability varies by card |
| User/card interaction families | 13 | Spend mix, goal, fee, first-card, lounge-gap, UPI, forex, network, cashback, complexity, redemption, seasonality/cap and ecosystem |
| Evidence/confidence modifiers | 3 | Material supported-fact count, detailed-model availability and completeness tie-break |
| Detailed-economic input families | 7 | Category/base rates, reward cap, annual fee, waiver threshold, lounge allowance, lounge-use assumption and the user's 12-category amounts |

Confidence modifiers never add product-fit points. Detailed-economic inputs operate only inside the seven normalized models; they do not imply normalized economics for all 267 cards.

## Detailed economic score

Only seven cards have normalized browser models. Income, credit history and issuer underwriting are not components of this score:

| Component | Weight |
|---|---:|
| Ongoing net annual value | 45% |
| Dominant-category fit | 25% |
| Preferences: fee, lounge, complexity, redemption, UPI and ecosystem | 15% |
| Main-goal alignment | 15% |

Detailed ranking uses a stable card-ID tie-break. Credit history and card journey can add only a positive supported secured/FD-backed discovery interaction in the 267-card catalogue; they cannot affect the seven-card economic order.

## Market-wide scoring safeguards

- Scores remain bounded to 10–95.
- Missing values neither earn bonuses nor become assumed zero fees, unlimited caps, supported networks, or approval compatibility.
- Every card displays two or three reasons backed by scoring conditions or an explicit unknown/neutral limitation.
- Annual fee ranking now uses 53 profile-level supported fee facts rather than only six catalogue-level fee rows.
- Cashback/reward preference uses only the 14 structured ongoing records across seven cards for a positive interaction. Sixty-nine ongoing excerpts awaiting product-association review remain display-only and neutral. Welcome offers never become ongoing earn rates.
- Seasonal spending receives a small caution adjustment only when a profile has a recorded cashback cap.
- Evidence completeness breaks exact score ties; it is also shown separately as `Detailed maths`, `More evidence`, or `Limited evidence`. Model availability and completeness add no fit points.
- Product fit remains separate from approval odds.

## Repayment safety branch

Repayment behavior is not treated as another rewards opportunity. If a user may carry a balance:

- the interface warns that a rewards ranking may be unsuitable;
- normalized cards are explicitly marked “Not ranked for borrowing cost” and use stable, non-reward ordering;
- the market catalogue leaves personalized reward ordering and uses issuer/name ordering;
- CardWise states that APR and finance-charge data are not normalized;
- no low-interest claim is made without supported APR evidence.

This follows the RBI's explanation that not clearing the total amount due can cause loss of the interest-free period and interest may be levied from the transaction date on the outstanding amount.

## Research basis

- Reserve Bank of India, **FAQs on Master Direction – Credit Card and Debit Card – Issuance and Conduct Directions, 2022**, dated 7 March 2024, accessed 20 July 2026: <https://www.rbi.org.in/commonperson/English/Scripts/FAQs.aspx?Id=3580>
- RBI, **Card Issuance and Conduct Directions**, for APR/MITC separation: <https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300>
- RBI network-choice circular: <https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12619>
- NPCI, **RuPay Credit Card on UPI**: <https://www.npci.org.in/product/rupay/credit-card-on-upi>
- Live product-flow review: [SBI Simplyfier](https://www.sbicard.com/en/personal/credit-cards/simplyfier.page), [SBI catalogue](https://www.sbicard.com/en/personal/credit-cards.page), [Axis catalogue](https://www.axis.bank.in/cards/credit-card), [BankBazaar](https://www.bankbazaar.com/credit-card.html), and [Paisabazaar](https://www.paisabazaar.com/credit-card/top-10-credit-cards-in-india/), accessed 20 July 2026.
- `METHODOLOGY.md`, especially the onboarding, spending-profile, redemption, fee-waiver, repayment-safety, evidence-governance and deterministic-calculation sections.
- `FILTER_DESIGN.md`, especially high-value user intents, rewards, fees, travel, UPI, eligibility, and trust dimensions.
- `CARD_PROFILES_2026-07-18.json`, used to audit which fee, cashback, cap, network, secured-status and evidence-completeness facts are actually available.

## Known limitations

- Only seven cards receive personalized ongoing rupee-value calculations.
- First-year value is not separately modeled.
- APR, finance charges, transfer ratios, fee-waiver thresholds and category caps are not normalized across the full catalogue.
- Seasonal-spend and cap compatibility is therefore conservative and qualitative outside supported cap evidence.
- Published eligibility evidence remains incomplete and is not converted into approval probability.
- Merchant names are not substitutes for MCC eligibility; issuer terms control.

## Research decisions

### Adopted now

- Full 12-category spend mix rather than only one dominant category for catalogue affinity
- Repayment behavior and a no-ranking borrowing-safety route
- UPI amount/preference, network, redemption, complexity and merchant ecosystem
- Existing lounge coverage to avoid double-counting that preference
- All 53 supported annual fees; unknown fees remain neutral
- Positive-only secured/FD-backed, lounge, UPI, forex and network facts; editorial starter tags remain neutral
- Structured ongoing cashback separated from welcome and review-pending excerpts

### Deferred until contractual economics are normalized

- Numeric fee-waiver, milestone, lounge-gate and monthly/quarterly cap attainability
- Existing-card portfolio and incremental value
- Airport/airline/hotel pattern, realistic perk utilization and holding horizon
- First-year value, point-transfer valuations, expiry, redemption fees and complexity cost
- APR/finance-charge ranking

### Rejected as organic ranking inputs

- Affiliate payout, sponsored placement, popularity and opaque ratings
- Approval probability from broad income or credit bands
- Welcome-benefit face value without requirements and redemption haircut
- Unknown terms treated as zero, free, unsupported, or unfavorable
