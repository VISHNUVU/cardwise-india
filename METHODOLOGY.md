# Trustworthy methodology and UX for an Indian credit-card finder

**Design goal:** recommend cards whose published terms fit a user's stated behaviour, while clearly separating (a) estimated economic fit, (b) published eligibility, and (c) an issuer's undisclosed underwriting decision. Never label a result “approved”, “pre-approved”, “guaranteed”, or “best” without the evidence and scope needed to support that claim.

## 1. Trust contract shown before onboarding

A short, plain-language panel should say:

- “We estimate value from the spending and redemption choices you enter.”
- “We compare **N cards from M issuers**, last checked **date/time**. This is not the whole Indian market.” Link to an issuer/card coverage list and inclusion method.
- “Some links may pay us. Payment never changes the calculation or order.” If commercial placement exists, isolate it in a clearly labelled **Sponsored** module that cannot resemble or displace organic results.
- “Only the issuer decides whether to approve you. Checking recommendations here does not apply for a card or guarantee approval.”
- “You can continue without a phone number, PAN, exact employer, or credit-bureau pull.”

Why this matters: RBI's Credit Card Directions require card issuers to provide a one-page Key Fact Statement with an application and, if an application is rejected, to provide the specific reason in writing. They also define APR and MITC and require MITC at onboarding and when conditions change. The finder should link the current issuer KFS/MITC and never simulate the issuer's decision.[1]

## 2. Onboarding: minimum first, precision later

Use a 4-step progressive form, with **Save and exit**, **Back**, “Why we ask”, a visible step count, and “Not sure / Skip” wherever the answer is not needed for a hard filter. Do not collect contact details to reveal results.

### Step 1 — What do you want?

1. Primary goal (choose up to two, then rank): simple cashback; online shopping; groceries/dining; fuel; travel/air miles; lounge access; UPI/RuPay; build credit; business expenses; balance transfer/low borrowing cost.
2. Will you normally pay the **total amount due in full** every month? Always / usually / sometimes / no / not sure.
3. Maximum acceptable annual/renewal fee: ₹0 / ₹500 / ₹1,000 / ₹2,500 / ₹5,000+ / enter amount. Ask separately whether a spend-based waiver is acceptable.
4. Complexity tolerance: automatic cashback only / simple points / willing to use portals and transfer partners.

**Safety branch:** if the user expects to revolve a balance, make APR and fees the primary comparison, suppress “earn more by spending” language, and explain that reward value may be outweighed by borrowing cost. Offer “cards are not recommended for financing routine spending” and alternatives such as a debit card or comparing lower-cost credit. Do not use a rewards score as the main rank.

### Step 2 — Spending profile

Ask monthly amounts, accepting ranges and zero, for:

- online retail (optionally Amazon/Flipkart/other, because co-brand and merchant rules differ);
- groceries/supermarkets; dining/food delivery;
- fuel;
- travel: flights, hotels, rail, local transit;
- utilities, mobile, insurance, education, rent and government payments;
- pharmacy/healthcare;
- other online and other offline retail;
- international spend in a typical year;
- UPI credit-card spend and preferred card network, if any.

Ask whether spend is steady or concentrated in certain months; caps and milestones often reset monthly, quarterly, or annually. Provide an “estimate for me” mode using broad bands, but label output precision accordingly. Explain that issuer rewards normally depend on merchant category code (MCC), not merely the shop name.

### Step 3 — Benefits the user will actually use

- Domestic and international trips per year; airports/cities; expected lounge visits; guest access need.
- Preferred redemption: statement credit, vouchers, flights/hotels, airline/hotel transfer, “not sure”.
- For each non-cash perk, ask likely annual uses or a maximum personal willingness-to-pay. Never value “luxury benefits” at issuer retail price by default.
- Existing cards and issuer relationships (optional), with annual fees and renewal month. This enables an **incremental value** view rather than pretending duplicate lounge or insurance benefits add full value.

### Step 4 — Published eligibility check (optional but useful)

- Age band and Indian resident/NRI status.
- Employment type: salaried / self-employed / student / retired / other.
- Gross monthly or annual income **band**, not exact salary; let users choose “prefer not to say”.
- Work/home pincode or serviceable city (only where the issuer publishes geographic restrictions).
- Credit-history band: no history / poor / fair / good / excellent / unknown. If score is requested, accept a user-entered band; do not call it a bureau check.
- Recent card applications or issuer/card already held, only if a published issuer rule makes this relevant.

Do not ask caste, religion, gender, marital status, health, contacts, full date of birth, PAN, Aadhaar, exact employer, or bank-login credentials for recommendation. If an issuer genuinely publishes a product-specific condition, show the rule rather than silently infer or proxy it. Separate consent is required for analytics, saved profiles, marketing, and any later application hand-off; consent withdrawal must be as easy as consent.[5]

## 3. Product data model and governance

Store versioned, source-backed card rules. Every field should have `value`, `effective_from`, `checked_at`, `source_url`, `source_type` (MITC/KFS/product page/T&C), `confidence`, and reviewer. Required objects:

- fees (joining, renewal, add-on, redemption, forex markup, cash advance, late fee, taxes);
- fee waiver threshold and eligible-spend definition;
- reward rule segments: MCC/merchant/channel/network, earn rate, unit, rounding unit, cap amount and reset period, minimum transaction, excluded transaction types;
- redemption options: conversion value, fee, minimum block, expiry, transfer ratio and transfer limits;
- milestones and welcome benefits with window, conditions, and one-time status;
- perks with limits, access conditions and effective dates;
- published eligibility by occupation, income, age, geography, residency, existing relationship;
- application URL and official MITC/KFS/T&C links.

Run automated link/change checks daily and human review on detected changes; show stale warnings after a defined SLA (for example, 30 days for product pages, immediately on a broken official source). Do not rank a card with materially incomplete fee/reward data; place it in “Not ranked—terms incomplete”. Preserve a calculation/version ID so a result can be reproduced.

A current issuer page illustrates why the full rule model is needed: the Cashback SBI Card advertises 5% online and 1% offline cashback, while also showing a ₹999 + taxes annual/renewal fee and renewal-fee reversal at ₹2 lakh annual spend. A trustworthy calculator must incorporate the fee, waiver condition, caps and exclusions from the linked terms, not repeat the headline rate.[2]

## 4. Deterministic rewards and cost engine

Simulate each of 12 months (or user-provided months), rather than multiplying one headline rate by annual spend.

For card `k`, month `m`, category/channel/MCC bucket `c`:

```text
eligible_spend[k,m,c] = max(0, user_spend[m,c] - excluded_spend[k,m,c])
raw_units[k,m,c]      = floor(eligible_spend / earn_rounding_block) * units_per_block
capped_units[k,m,r]   = apply_rule_cap(sum(raw_units covered by rule r), r.cap, r.reset_period)
```

Where cashback is direct, `unit_value = ₹1`. For points:

```text
cash_value_of_points = redeemable_units * selected_redemption_value_per_unit
                       - redemption_fees
```

Use the user's selected redemption path. If unknown, display a **conservative default and range**: the lower broadly available cash/voucher value as the main estimate, plus a separately labelled travel-transfer scenario. Do not rank on a theoretical maximum transfer value that requires scarce award inventory, a premium cabin, or a portal unless the user selected and can use it.

### Annual net value

```text
base_rewards      = sum_months_and_rules(cash_value)
milestone_value   = sum(achieved_milestone_value)
welcome_value_y1  = value only if conditions are met and user is new/eligible
perk_value        = sum(min(expected_uses, annual_limit)
                        * user_willingness_to_pay_per_use
                        * availability_haircut)
renewal_fee_paid  = 0 if waiver threshold is met under issuer's eligible-spend rules
                    else renewal_fee * (1 + applicable_tax_rate)
expected_costs    = renewal_fee_paid + redemption_fees + expected_surcharges
                    + portal_price_premium + other unavoidable costs
NAV_ongoing       = base_rewards + milestone_value + perk_value - expected_costs
NAV_year1         = NAV_ongoing + welcome_value_y1 - joining_fee_with_tax
```

Always show **Year 1** and **Ongoing year** separately. Also calculate:

```text
net_reward_rate = NAV_ongoing / total_annual_spend
break_even_spend = lowest simulated spend at which NAV_ongoing >= 0
```

For an existing wallet, compute `incremental_NAV = NAV(new wallet) - NAV(existing wallet)` using a deterministic spend allocator. Allocate each bucket to the eligible owned/candidate card with highest marginal value, respecting caps and milestones; report the allocation assumptions.

### Honest valuation rules

- Cashback: face value only when automatically credited and not expiring.
- Voucher: face value × user's likelihood of using that merchant before expiry; never exceed planned spend.
- Lounge: user's willingness-to-pay, capped at plausible visits; zero for duplicate visits already covered by another card. Account for spend conditions and guest fees.
- Insurance: default ₹0 unless coverage is understood and user assigns value; show it as coverage, not “savings”.
- Forex: count only markup saved against the user's selected comparison card and actual foreign spend; include network/issuer markup and taxes where applicable.
- Fuel surcharge waiver: apply transaction range, cap, exclusions and taxes; do not treat it as fuel cashback.
- Milestones: no pro-rating. Value at zero until the threshold is met; show distance to threshold without encouraging unnecessary spend.
- Uncertain merchant classification: calculate low/base/high scenarios and identify the affected spend.

## 5. Exclusions and deterministic ranking

### Hard exclusions (never silently discarded)

A card is **ineligible under published criteria** only when a current official source and user answer directly conflict: age/residency, salaried vs self-employed product availability, published minimum income, service geography, secured-deposit requirement, card/network requirement, or an issuer's explicit existing-card restriction. Also honour user hard constraints: fee ceiling, no co-brand, RuPay/UPI requirement, no portal, no foreign-markup card, etc.

Keep an “Excluded cards (N)” drawer with the exact reason, user answer, issuer rule, source and “edit answer”. Distinguish:

- `PUBLISHED_MISMATCH` — do not recommend;
- `MISSING_USER_DATA` — retain but mark “cannot assess”;
- `MISSING_ISSUER_RULE` — retain but mark “issuer criteria not published/verified”;
- `USER_PREFERENCE` — excluded by a user-selected constraint, reversible.

Never infer ineligibility from postcode demographics, device, language, surname, gender or other proxies. A thin/no-file user should see secured/credit-building options if in catalog, not be treated as “bad credit”.

### Primary ranking

Do not hide economic value inside an arbitrary star rating. Default order is:

1. cards without a published eligibility mismatch;
2. descending `risk_adjusted_NAV_ongoing`;
3. descending `NAV_year1`;
4. lower complexity, then lower fee, then stable card ID as deterministic tie-breakers.

```text
uncertainty_cost = max(0, NAV_base - NAV_joint_conservative_scenario)
risk_adjusted_NAV_ongoing = NAV_ongoing - uncertainty_cost
```

This makes uncertainty visible in rupees. It does **not** punish a person for unknown creditworthiness.

If a 0–100 “fit” score is desired for scanning, make it secondary and reproducible:

```text
value_fit      = clamp(0,100, 50 + 50 * NAV_ongoing /
                       max(5000, 0.05 * annual_spend))
goal_fit       = weighted fraction of user-selected goals satisfied (0..100)
simplicity_fit = 100 - published friction points (0..100)
fee_fit        = 100 if fee=0 or waived at projected spend;
                 0 if user_fee_ceiling=0 and fee_with_tax>0;
                 otherwise 100 * max(0, 1 - fee_with_tax/user_fee_ceiling)
fit_score      = round(0.60*value_fit + 0.20*goal_fit
                       + 0.10*simplicity_fit + 0.10*fee_fit)
```

Publish every weight and friction rule. Let the user change goal weights and rerun instantly. **Do not multiply fit by approval likelihood**; suitability and underwriting are different questions. Do not add commercial commission, click-through rate or issuer campaign priority to organic scoring.

## 6. Eligibility confidence without fake approval odds

Use evidence labels, not uncalibrated percentages:

- **Meets checked published criteria** — all published rules in the data set pass, and all required answers are present.
- **May meet published criteria** — no mismatch, but one or more user answers are missing or near a threshold.
- **Issuer criteria not fully published** — no mismatch found, but underwriting/criteria are unavailable.
- **Does not meet a published criterion** — exact conflict shown.

Alongside, show **data confidence: High / Medium / Low**, based only on source completeness and freshness. Copy: “This is not an approval probability. The issuer may check income documents, credit history, existing exposure and internal policy.”

Only introduce an approval probability after collecting consented, representative outcome data and completing calibration/fairness governance. Then: train on application outcomes rather than clicks; separate each issuer/product/version/time period; avoid protected attributes and proxies; measure calibration (not just AUC), false-positive/negative rates and drift; publish sample window; show a range; provide adverse-result explanations; and never call a soft estimate “pre-approved”. Until then, categorical evidence is more trustworthy.

## 7. Explainability contract

Every result card must answer five questions without opening fine print:

1. **Why it fits:** “Estimated ₹X ongoing value because ₹A of your online spend earns …”.
2. **What it costs:** joining and renewal fee including applicable taxes; waiver threshold and whether projected spend reaches it.
3. **What could change the estimate:** caps, excluded categories, MCC ambiguity, portal/redemption assumptions, point expiry, devaluation risk.
4. **Eligibility evidence:** one of the labels above, with checked/unknown rules.
5. **Commercial relationship:** “We may receive ₹/commission if you apply; ranking unchanged” or “No paid relationship”.

An expanded “Show the maths” table should show each spend bucket, eligible amount, rule/rate, cap, units, unit value, annual value, fees and source. Add **Recalculate**, **Use conservative assumptions**, **Compare official terms**, **Copy calculation ID**, and **Report outdated information**.

Never state “you will earn ₹X”; say “estimated under these assumptions”. For points, show both points and ₹ conversion. Label issuer marketing claims as such.

## 8. Wireframe-level UI flow

### A. Landing / trust panel

```text
Find cards that fit how you already spend
[Compare without phone number]
Coverage: N cards · M issuers · updated DATE        [How we make money]
Not an approval check. Issuers decide approval.     [Methodology]
```

### B. Four onboarding screens

```text
Step 2 of 4: Monthly spending                   [Save & exit]
Online shopping  [₹____]  (i) Why we ask
Groceries        [₹____]
...
[Not sure — use ranges]                         [Back] [Continue]
```

Sticky controls must not obscure keyboard focus. No preselected marketing consent; no phone-number gate.

### C. Results header

```text
Your results: 18 ranked · 7 need more information · 4 excluded
Based on ₹8.4L annual spend · full payment · cashback redemption
[Edit answers] [Assumptions] [Coverage] [Sort: Ongoing net value]
```

If estimates are imprecise, use a range rather than false precision.

### D. Organic result card

```text
#1 Card name                          Meets checked published criteria
Estimated ongoing value: ₹X/year     Year 1: ₹Y     Net rate: Z%
Fee: ₹F + taxes · projected waiver: Yes/No
Why: +₹A online, +₹B groceries, −₹F fee
Watch-outs: monthly cap ₹C · utilities excluded · portal needed
Data checked DATE · Official terms ↗
[Show maths] [Compare] [Apply on issuer site ↗]
We may receive commission; rank unchanged. [Details]
```

The dominant action should initially be **Show maths/Compare**, not Apply. An external-application interstitial should summarize fee, APR, key exclusions, confidence label and “Issuer decides approval”, with equal-weight **Back** and **Continue to issuer** actions.

### E. Comparison

Use a user-chosen 2–4 card comparison with rows for year-1/ongoing NAV, fees/taxes, category value, caps, exclusions, APR, forex, lounge conditions, redemption friction, published eligibility and source freshness. Freeze row labels, not promotional CTAs. Provide “Only differences” and export/print.

### F. No-match state

Explain which constraints caused no match; offer to relax one explicitly. Never quietly loosen a fee ceiling or income criterion. Include “A credit card may not be suitable” where applicable.

## 9. Accessibility and localisation

Target **WCAG 2.2 AA**.[4]

- Semantic headings, landmarks, labels and native controls; complete keyboard operation; visible, unobscured focus; skip link; logical focus after validation and accordions.
- Minimum 24×24 CSS px pointer targets (or conforming spacing exception), no drag-only compare/reorder, and persistent help. WCAG 2.2 specifically adds Focus Not Obscured, Target Size (Minimum), Consistent Help, Redundant Entry and Accessible Authentication.[4]
- Text contrast at least 4.5:1 for normal text and 3:1 for large text; non-text UI/focus indicators at least 3:1. Do not encode rank, eligibility or positive/negative value by colour alone; pair icon + text.
- Errors in text next to the field and in a summary; preserve values; suggest correction. Currency inputs accept Indian grouping, plain digits and screen-reader-friendly labels (for example, “rupees per month”).
- Avoid carousels, auto-advancing content, countdowns and hover-only disclosures. Respect zoom/reflow, text spacing, reduced motion, dark/high-contrast modes.
- Use plain English and Hindi at launch, with localisation-ready copy for other Indian languages. Keep card names and official legal terms intact; explain jargon such as APR, MCC and MITC in the selected language. Do not use flags as language icons.
- Results and “show the maths” must work with screen readers. Announce recalculated result counts through a polite live region, not every keystroke.
- Do not require a cognitive-function test, copy/paste blocking, or memory puzzle for authentication; avoid redundant re-entry.[4]

## 10. Disclaimers that inform rather than absolve

Put short, contextual disclosures where decisions occur; a footer-only legal wall is insufficient.

**Results:** “Estimates use the spending and redemption assumptions shown. Merchant category codes, caps, exclusions and issuer changes can alter rewards. Terms checked DATE.”

**Eligibility:** “We check only criteria available to us. This is not an approval or pre-approval. The issuer makes the final decision after its own checks.”

**Application:** “You are leaving for the issuer's site. Review the issuer's KFS, MITC and current terms, including APR, fees and exclusions, before applying.”

**Coverage/commercial:** “We cover N cards from M issuers, not the whole market. We may receive compensation for some applications. Compensation does not enter the organic ranking formula.” List paid relationships and cards/issuers not covered.

**Financial conduct:** “Paying only the minimum amount due can lead to interest and a longer repayment period. Rewards should not be a reason to borrow or spend more.”

Disclaimers must not contradict headlines. “Guaranteed approval*” cannot be cured by an asterisk.

## 11. Anti-dark-pattern rules and measurable safeguards

India's CCPA Guidelines for Prevention and Regulation of Dark Patterns, 2023 identify practices including false urgency, basket sneaking, confirm shaming, forced action, subscription traps, interface interference and disguised advertisements.[3] Translate that into product rules:

- No fake scarcity (“3 approvals left”), countdowns, fabricated popularity, or “apply now or lose this card”.
- No result gate requiring mobile/email, app install, bureau consent, notifications, data-sharing or marketing opt-in (**forced action**).
- No pre-ticked insurance, paid membership, balance transfer or marketing; no add-on introduced after selection (**basket sneaking**).
- No guilt copy (“No thanks, I hate free rewards”) or red warning for declining (**confirm shaming**).
- Organic and Sponsored modules have distinct borders, labels and accessible names; sponsored cards never receive organic rank numbers (**disguised ads/interface interference**).
- Reject/Back/Skip/Withdraw is as visible and easy as Accept/Continue. No repeated prompt after decline in the same journey.
- Never preselect the highest fee, most data-sharing, or issuer-favoured option. Defaults should be conservative and reversible.
- Do not manufacture loss aversion around milestones or waivers; say “you are below the threshold”, not “spend ₹X now to save ₹Y”.
- Do not silently reorder after a commission change. Log ranking inputs/outputs and run a daily invariant test that commission fields have no path into scoring.
- Do not use click or application conversion as a direct ranking feature. Optimise product metrics for completed comparisons, assumption edits, outdated-term reports, low complaint rates and user comprehension—not application volume alone.
- Provide deletion/export of saved data and a privacy dashboard. No third-party pixels before consent where consent is required.

Governance: quarterly dark-pattern review by product, legal, accessibility and an independent consumer advocate; pre-release accessibility testing with disabled users; outcome audits by income band, language, geography and thin-file status; public methodology/changelog; correction SLA; conflict-of-interest register; and an appeal/report mechanism.

## 12. Acceptance tests

1. The same inputs + catalog version always produce the same ordered list and calculation ID.
2. Changing commission to any value leaves organic rank unchanged.
3. A fee waiver excludes transaction types exactly as issuer terms specify.
4. Monthly caps are not annualised incorrectly; milestone rewards are not pro-rated.
5. Year 1 and ongoing values differ when welcome/joining benefits apply.
6. A skipped income answer yields “cannot assess”, not rejection or a hidden filter.
7. A published income mismatch appears in Excluded with source and edit path.
8. Unknown points redemption uses conservative value and displays a range.
9. Existing-card benefits are not double-counted in incremental value.
10. Keyboard and screen-reader users can complete onboarding, inspect maths, compare and leave without application or contact capture.
11. Declining marketing has no effect on results or access.
12. Broken/stale official terms remove the card from ranked results and show why.
13. A user who carries a balance sees borrowing cost/APR prominence, not a spend-maximisation prompt.
14. Every Apply click shows issuer destination, fee, APR/terms link and non-guarantee statement.

## Sources

1. Reserve Bank of India, **Master Direction – Credit Card and Debit Card – Issuance and Conduct Directions, 2022 (updated 7 Mar 2024)**: definitions of APR/MITC; customer-acquisition KFS, rejection reason and MITC obligations. https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300
2. SBI Card, **Cashback SBI Card** official product page (accessed 18 Jul 2026): headline online/offline cashback, annual/renewal fee, waiver threshold, and official-terms links. https://www.sbicard.com/en/personal/credit-cards/cashback-sbi-card.html
3. Central Consumer Protection Authority, **Guidelines for Prevention and Regulation of Dark Patterns, 2023** (30 Nov 2023), official Department of Consumer Affairs PDF. https://consumeraffairs.nic.in/sites/default/files/file-uploads/latestnews/Guidelines%20for%20Prevention%20and%20Regulation%20of%20Dark%20Patterns%2C%202023.pdf
4. W3C Web Accessibility Initiative, **What's New in WCAG 2.2**; WCAG 2.2 became a W3C Recommendation on 5 Oct 2023 and adds nine success criteria. https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
5. Government of India, **Digital Personal Data Protection Act, 2023**, especially notice/consent, withdrawal and data-principal rights. India Code: https://www.indiacode.nic.in/handle/123456789/20751

> Operational note: issuer terms change frequently. The facts above are examples, not a frozen card catalog. Production should store and display each fact's effective date and latest successful verification timestamp.