## 1. Recommended information architecture

Use three complementary entry points rather than one long questionnaire:

1. **Search**
   - Card, issuer, network, co-brand, or benefit search.
   - Examples: “SBI Cashback,” “RuPay UPI,” “Tata Neu,” “low forex,” “airport lounge.”
2. **Browse catalogue**
   - Immediate results with a small set of high-value filter chips.
   - Suitable for users who already know what they want.
3. **Find cards for me**
   - A progressive recommender based on spending, requirements, and eligibility.
   - Show preliminary results before requesting phone, PAN, bureau consent, or login.

A persistent fourth mode should be **Compare**, supporting 2–4 cards.

### Result-page hierarchy

Above results:

- Search box
- Result count
- Active-filter chips
- Sort control
- Mobile **Filters (n)** button
- Plain-language ranking explanation

Each result card should answer, in order:

1. Why this card matches
2. Estimated annual value or principal benefit
3. Joining and annual fee
4. Important condition, cap, or exclusion
5. Eligibility confidence
6. Data verification status
7. Compare and details actions
8. Apply action, with partner/sponsored disclosure where applicable

---

## 2. Progressive filtering model

Do not expose every filter at once.

### Level 1: High-value quick filters

Keep these visible as chips or compact controls:

- Lifetime free / no annual fee
- Cashback
- RuPay UPI rewards
- Lounge access
- Travel and low forex
- Fuel
- Grocery and everyday spending
- Premium cards
- Secured / FD-backed
- Issuer
- Annual fee
- Eligibility
- More filters

These should reflect demand and may change based on the query. For example, a search for “lounge” can surface **No spend requirement** and **International lounge** as contextual chips.

### Level 2: Filter groups

Open an **All filters** sheet organized by user intent, not database structure:

1. Best for
2. Fees and ownership cost
3. Rewards
4. Travel and lounge
5. UPI and card network
6. Eligibility and credit profile
7. Issuer and card type
8. Trust and availability

Show the active count on every collapsed group.

### Level 3: Advanced details

Reveal technical controls only after the user expands **Advanced**:

- Reward cap
- Minimum redemption
- Transfer partners
- MCC exclusions
- Lounge spend gate
- Renewal waiver threshold
- Forex reward offset
- Add-on lounge entitlement
- Data-verification age

---

## 3. Implementable filter fields

The catalogue should distinguish:

- **Hard filters:** explicit requirements; non-matches are excluded.
- **Preferences:** influence ranking without hiding alternatives.
- **Display-only facts:** shown for trust but not normally filtered.
- **Derived fields:** calculated from structured terms.

### A. Identity, issuer, and availability

| Field | Type | Filter semantics |
|---|---|---|
| `issuer_id` | enum/multi-select | Hard match if selected |
| `card_name` | text | Searchable with aliases |
| `card_variant` | text/enum | Distinguish regular, Select, Signature, Metal, etc. |
| `network` | enum[] | Visa, Mastercard, RuPay, Amex, Diners Club |
| `network_variant` | enum[] | Platinum, Signature, Infinite, World, World Elite, Select |
| `card_type` | enum[] | Cashback, rewards, travel, airline, hotel, fuel, lifestyle, premium, business |
| `co_brand_partner` | entity[] | Airline, hotel, retailer, fuel, fintech, e-commerce partner |
| `is_cobranded` | boolean | Hard only if explicitly selected |
| `is_accepting_applications` | boolean | Default-exclude discontinued or paused cards |
| `application_channel` | enum[] | Issuer online, branch, invite-only, upgrade-only, marketplace |
| `serviceable_pincodes` | rule/reference | Apply only after PIN code is provided |
| `resident_requirements` | enum/rule | Resident Indian, NRI, specific geography |
| `launch_status` | enum | Active, waitlist, paused, discontinued |

**Important:** Keep discontinued products searchable for existing-card research, but exclude them from “Apply now” recommendations.

### B. Fees and ownership cost

Store amounts both **before GST** and as a derived **including GST** value.

| Field | Type | Filter semantics |
|---|---|---|
| `joining_fee_inr` | number |
| `annual_fee_inr` | number |
| `annual_fee_gst_inclusive` | derived number |
| `is_lifetime_free` | boolean | Must represent an unconditional LTF offer |
| `first_year_free` | boolean | Never label this as LTF |
| `fee_waiver_available` | boolean |
| `fee_waiver_spend_inr` | number |
| `fee_waiver_period` | enum | Anniversary year, calendar year, statement year |
| `supplementary_card_fee_inr` | number |
| `cash_advance_fee` | structured amount/rate |
| `finance_charge_apr` | number/range |
| `rent_transaction_fee` | structured rate/minimum |
| `utility_surcharge` | structured |
| `fuel_surcharge_waiver` | structured |
| `forex_markup_percent` | number |
| `dynamic_currency_conversion_warning` | boolean/display |
| `closure_or_redemption_conditions` | structured/text |

Useful controls:

- Annual fee: ₹0, ≤₹500, ≤₹1,000, ≤₹2,500, custom
- Lifetime free only
- First-year free
- Fee waiver available
- Waiver threshold maximum
- Joining benefit offsets fee
- Show total ongoing cost including GST

Never collapse “free,” “first-year free,” and “waived after spend” into a single no-fee category.

### C. Rewards and cashback

Use a normalized category taxonomy and preserve issuer-specific rules.

#### Core fields

| Field | Type |
|---|---|
| `reward_currency` | enum/text |
| `base_reward_rate` | structured rate |
| `cashback_rate` | structured rate |
| `reward_categories` | rule[] |
| `reward_cap_period` | enum |
| `reward_cap_value` | number |
| `reward_cap_unit` | points/INR/spend |
| `minimum_redemption` | number |
| `redemption_fee_inr` | number |
| `point_expiry_months` | number/null |
| `point_value_options` | redemption option[] |
| `statement_credit_value` | number |
| `transfer_partners` | entity[] |
| `transfer_ratio` | structured |
| `milestone_rewards` | rule[] |
| `excluded_mccs` | MCC/rule[] |
| `excluded_transaction_types` | enum[] |
| `reward_posting_delay` | structured/display |
| `reversal_terms` | structured/display |

#### India-specific spending categories

Support separate inputs and filters for:

- UPI merchant payments
- Online grocery
- Offline grocery and supermarkets
- Dining
- Food delivery
- General online shopping
- General offline retail
- Amazon
- Flipkart
- Tata Neu ecosystem
- Fuel, including preferred fuel brand
- Utility bills
- Mobile/DTH recharge
- Insurance
- Rent
- Education
- Government and tax payments
- Railway/IRCTC
- Pharmacy and healthcare
- Domestic flights
- Hotels
- International travel
- Foreign-currency spending
- Entertainment, movies, and ticketing
- Quick commerce
- Cabs and local transit
- Wallet loads

A rule should be able to express:

```text
category + channel + merchant/co-brand + MCC + rate +
monthly/quarterly cap + minimum transaction + exclusions +
effective date
```

Example:

```json
{
  "category": "grocery",
  "channel": "online",
  "merchant_scope": ["eligible_merchant_list"],
  "reward_type": "cashback",
  "rate_percent": 5,
  "cap_inr": 500,
  "cap_period": "statement_month",
  "excluded_transaction_types": ["wallet_load", "emi"]
}
```

### D. UPI and network

| Field | Type | Semantics |
|---|---|---|
| `supports_upi_linking` | boolean | Usually derived from eligible RuPay variant |
| `upi_variant_available` | boolean |
| `upi_merchant_rewards` | boolean |
| `upi_reward_rate` | structured rate |
| `upi_reward_cap` | structured |
| `upi_min_transaction` | number |
| `upi_exclusions` | rule[] |
| `upi_p2p_eligible` | boolean | Usually false; show explicitly |
| `upi_app_restrictions` | entity[]/text |
| `virtual_card_supported` | boolean |
| `contactless_supported` | boolean |
| `tokenisation_wallets` | enum[] |

Do not use “UPI card” as a synonym for “earns rewards on all UPI.” Distinguish:

1. RuPay card can be linked to UPI.
2. Merchant UPI transactions are eligible.
3. Those transactions earn rewards.
4. Rate and cap make the rewards meaningful.

### E. Lounge and travel

| Field | Type |
|---|---|
| `domestic_lounge_visits` | number/unlimited |
| `domestic_lounge_period` | month/quarter/year |
| `international_lounge_visits` | number/unlimited |
| `international_lounge_program` | enum/text |
| `lounge_spend_gate_inr` | number |
| `lounge_spend_gate_period` | enum |
| `lounge_gate_lookback` | structured |
| `lounge_guest_access` | structured |
| `add_on_lounge_access` | structured |
| `railway_lounge_access` | structured |
| `airport_list_or_program` | reference |
| `forex_markup_percent` | number |
| `international_reward_rate` | structured |
| `travel_portal_requirement` | boolean/entity |
| `airline_transfer_partners` | entity[] |
| `hotel_transfer_partners` | entity[] |
| `travel_insurance` | benefit[] |
| `concierge` | boolean |
| `priority_pass_fee_terms` | structured |

User-facing lounge controls:

- Domestic lounge
- International lounge
- Number of visits needed per quarter/year
- **No spend requirement**
- Maximum acceptable spend gate
- Guest access
- Add-on card access
- Railway lounge

A lounge visit should not count as “available” for hard filtering if the user’s projected eligible spend cannot satisfy its gate, unless they choose to ignore the requirement.

### F. Eligibility and approval profile

Separate product attractiveness from approval probability.

| Field | Type |
|---|---|
| `employment_types` | enum[] |
| `minimum_income_monthly_inr` | number/rule |
| `income_basis` | gross/net/ITR/issuer-specific |
| `minimum_age` | number |
| `maximum_age` | number |
| `credit_history_requirement` | enum |
| `suggested_credit_score_min` | number/range with source confidence |
| `new_to_credit_supported` | boolean/unknown |
| `issuer_relationship_required` | boolean |
| `relationship_types` | enum[] |
| `existing_card_required` | boolean/rule |
| `minimum_existing_limit_inr` | number |
| `application_mode` | enum |
| `upgrade_only` | boolean |
| `invite_only` | boolean |
| `secured` | boolean |
| `fd_minimum_inr` | number |
| `credit_limit_to_fd_ratio` | range |
| `fd_tenure_requirements` | structured |
| `bureau_enquiry_expected` | boolean/unknown |
| `eligibility_source` | issuer/marketplace/editorial/inferred |
| `eligibility_last_verified_at` | date |

Profile inputs:

- Salaried, self-employed, student, retired, other
- Monthly income or annual ITR
- New to credit / thin file / established history
- Approximate credit score band, optional
- Existing relationship with issuers
- Existing card and limit, optional
- PIN code, only when needed for serviceability
- Willing to open an FD
- Minimum desired limit

Avoid declaring “pre-approved” or “high approval odds” without issuer-backed data. Use calibrated labels:

- Likely eligible
- Possibly eligible
- Eligibility unclear
- Known requirement not met

### G. Secured and credit-building cards

| Field | Type |
|---|---|
| `secured` | boolean |
| `fd_issuer` | entity |
| `fd_minimum_inr` | number |
| `fd_interest_earned` | boolean/rate reference |
| `fd_lien_terms` | structured |
| `limit_percent_of_fd` | number/range |
| `credit_bureau_reporting` | bureau[]/unknown |
| `graduation_path_available` | boolean/unknown |
| `foreclosure_effect` | structured |
| `add_money_or_membership_fee` | structured |
| `new_to_credit_suitability` | enum |
| `credit_builder_claim_source` | reference |

Never rank secured cards solely by rewards; FD lock-in, effective limit, fees, bureau reporting, and exit conditions matter more.

### H. Verification and trust filters

| Field | Type |
|---|---|
| `terms_source_url` | URL |
| `source_type` | issuer MITC/issuer page/network/partner/editorial |
| `effective_from` | date |
| `last_verified_at` | datetime |
| `verification_status` | verified/partially verified/unverified/conflicting |
| `terms_version` | string |
| `change_log` | reference |
| `calculation_confidence` | high/medium/low |
| `catalogue_availability_status` | active/paused/discontinued/unknown |
| `commercial_relationship` | partner/non-partner/sponsored/unknown |
| `affiliate_disclosure_url` | URL/null |
| `user_report_count` | number |
| `structured_user_evidence_status` | corroborated/unverified/disputed |

Useful filters:

- Issuer-verified terms only
- Verified in the last 30/90/180 days
- Currently accepting applications
- Exclude invite-only or upgrade-only
- Show non-partner cards
- Hide products with conflicting terms

---

## 4. Search semantics

Search should cover:

- Card and issuer names
- Previous names and aliases
- Network and variant
- Co-brand partner
- Benefit names
- Common intent phrases
- Indian colloquialisms and abbreviations

Examples of query interpretation:

| Query | Interpretation |
|---|---|
| `LTF` | `is_lifetime_free = true` |
| `zero fee` | Prefer LTF; explain first-year-free separately |
| `UPI rewards` | RuPay variant + eligible merchant UPI rewards |
| `low forex` | Sort by effective foreign-spend value, not markup alone |
| `lounge without spend` | Lounge entitlement with no spend gate |
| `new to credit` | Prefer supported or secured cards; do not promise approval |
| `Amazon cashback` | Amazon category/merchant rewards, not merely card-name match |
| `fuel BPCL` | Fuel category + BPCL partner preference |
| `free lounge card under 1000` | Annual fee constraint plus lounge requirement |
| `SBI cashback` | Exact-card intent ranked above generic SBI cashback cards |

### Search behavior

- Exact card/entity matches first.
- Then intent matches.
- Then benefit and editorial matches.
- Typo tolerance and transliteration support.
- Synonym dictionary: `forex`, `FX`, `international spend`; `LTF`, `lifetime free`; `lounge`, `airport access`.
- Search must not silently turn interpreted terms into hard filters. Show them as removable chips.
- Queries with conflicting intent should trigger a clarification chip, not an empty result.

---

## 5. Recommender inputs

Use a short first pass and optional refinement.

### Initial questions

1. What do you spend most on?
2. Rough monthly spend by selected categories
3. Fee preference
4. Must-have benefits
5. Employment and income band
6. Credit-history band
7. Existing issuer relationships, optional

Show useful results after this stage.

### Optional refinements

- Exact merchant split
- Domestic/international travel
- UPI spend
- Reward redemption preference
- Lounge visit requirement
- Existing cards
- Willingness to meet milestone or waiver thresholds
- Transfer-partner preference
- PIN code
- FD willingness

Do not require exact salary, phone, PAN, or bureau consent for an initial recommendation.

---

## 6. Ranking and filter semantics

### A. Keep three scores separate

Every card should have:

1. **Economic-fit score**
   - Expected annual rewards and benefits minus fees and expected charges.
2. **Eligibility-fit score**
   - Alignment with known issuer requirements.
3. **Data-confidence score**
   - Freshness, source quality, and completeness.

Do not secretly lower economic rank because approval is uncertain. Present both dimensions:

> Highest estimated value, but eligibility is uncertain.

### B. Hard-filter behavior

Hard-exclude only when:

- The user explicitly marks a condition as **must have**, and
- Catalogue data confirms the card does not satisfy it.

For unknown values:

- Do not treat unknown as false.
- Place results in a **May match—details unverified** section.
- Exclude unknowns only for filters such as **Issuer-verified only**.

Examples:

```text
network = RuPay AND requirement_strength = must
→ exclude confirmed non-RuPay cards

new_to_credit = true AND card.new_to_credit_supported = unknown
→ retain with uncertainty penalty, not hard-exclude

annual_fee <= 1000
→ compare ongoing annual fee including GST if UI says “total fee”
```

### C. Economic-value calculation

Calculate personalized value using:

```text
Expected annual value
= category rewards after caps and exclusions
+ attainable milestones
+ conservatively valued usable benefits
+ joining benefit, if year-one view
− annual/joining fee including GST
− expected category surcharges
− estimated forex cost
− redemption fees
```

Rules:

- Calculate **year one** and **ongoing year** separately.
- Count a fee waiver only if projected eligible spend reaches its threshold.
- Respect monthly, quarterly, and annual caps.
- Apply merchant/channel/MCC exclusions.
- Do not assign full face value to vouchers the user did not say they would use.
- Lounge access should be valued only when the user expects to use it and can meet the spend gate.
- Let users override point values and lounge/voucher valuations.
- Show the calculation assumptions.

### D. Suggested ranking formula

Use weighted normalized components:

```text
rank_score =
  economic_fit
  + use_case_fit
  + stated_preference_fit
  + eligibility_fit
  + data_confidence
  − complexity_penalty
  − unmet_soft_preference_penalty
```

Weights should vary by mode:

- **Best value:** economic fit dominates.
- **Most likely eligible:** eligibility fit dominates.
- **Lowest cost:** fees and attainable waiver dominate.
- **Simplest rewards:** penalize portals, caps, transfer complexity, and redemption fees.
- **Travel:** forex, transfers, travel rewards, and usable lounge benefits dominate.
- **Credit building:** FD terms, reporting confidence, and cost dominate.

Sponsored status, affiliate availability, and issuer commission must have **zero effect** on organic rank. Sponsored placements can appear only in clearly labelled, visually separate slots.

### E. Stable tie-breaking

For near-equal scores:

1. Higher verification confidence
2. Lower ongoing fee
3. Simpler redemption
4. Fewer material exclusions
5. More recent issuer verification
6. Alphabetical order as the final deterministic fallback

---

## 7. Result explanations

Every recommendation should expose:

- **Why it matches:** “Strong fit for ₹12,000/month online spend.”
- **Estimated outcome:** “Approx. ₹X ongoing annual value after fee.”
- **Most important limitation:** “Cashback capped at ₹Y per statement month.”
- **Eligibility:** “Income requirement appears met; approval not guaranteed.”
- **Trust:** “Terms checked against issuer MITC on [date].”
- **Alternative:** “Choose Card B if you prefer no fee or cannot meet the waiver.”

Avoid generic badges such as “Best card” without a stated scenario.

---

## 8. Mobile behavior

### Catalogue

- Keep search, result count, **Filters (n)**, and sort sticky.
- Open filters in a full-height bottom sheet or full-screen route.
- Retain draft selections when users close and reopen the sheet.
- Use a sticky footer:
  - `Clear`
  - `Show 48 cards`
- Update result count as filters change, but do not close the sheet automatically.
- Active filters appear as horizontally scrollable, individually removable chips.
- Preserve scroll position when returning from card details.

### Filter controls

- Chips for small mutually understandable sets.
- Checkboxes for issuer, network, and multi-select use cases.
- Radio buttons only for mutually exclusive choices.
- Numeric inputs plus presets for fee, income, and spend thresholds.
- Avoid precise dual-handle sliders as the sole control; they are difficult on mobile and inaccessible.
- Put selected items first within long lists.
- Add issuer and co-brand search inside their groups.

### Compare

On mobile, show decision-critical rows first:

1. Net annual value
2. Annual fee and waiver
3. Primary reward rate and cap
4. Lounge qualification
5. Forex markup
6. Eligibility
7. Verification date

Allow expansion for full details. Freeze card names and row labels during horizontal scrolling.

---

## 9. Accessibility requirements

- Every filter must have a programmatic label and description.
- Do not communicate selected, unavailable, verified, or sponsored state using color alone.
- Minimum 44×44 px touch targets.
- Visible keyboard focus and logical focus order.
- On applying filters, announce:
  - Result count
  - Changed filter
  - Any automatic relaxation
- Use native controls where possible.
- Associate validation and fee-unit text with inputs via accessible descriptions.
- Explain abbreviations such as LTF, MCC, FD, MITC, and forex on first use.
- Support text zoom without truncating fee, cap, or warning information.
- Charts or reward bars require equivalent textual values.
- Avoid moving carousel-style recommendation cards.
- Keep Apply, Compare, and Details labels explicit; do not use unlabeled icons.

---

## 10. No-results recovery

Never return a dead-end empty state.

### Behavior

1. State which constraints conflict.
2. Suggest the smallest relaxation.
3. Show how many cards each relaxation would recover.
4. Let the user apply one relaxation at a time.
5. Keep all original filters visible and restorable.

Example:

> No cards match **Lifetime free + international lounge + no lounge spend requirement**.

Suggested recovery:

- Allow annual fee up to ₹1,000 — 3 cards
- Allow a lounge spend gate up to ₹20,000/quarter — 5 cards
- Include cards with unverified add-on lounge terms — 2 cards

### Relaxation priority

Relax soft preferences before hard requirements:

1. Co-brand or issuer preference
2. Reward-rate preference
3. Network preference, unless UPI linking is required
4. Fee-waiver preference
5. Annual fee ceiling
6. Lounge frequency or gate
7. Eligibility confidence
8. Must-have feature only with explicit user confirmation

Never silently relax:

- Secured vs unsecured
- Maximum fee
- Required RuPay/UPI support
- Current application availability
- Verification-only preference

Provide a final fallback:

- Show near matches
- Save the search
- Alert when matching cards appear
- Browse secured or beginner alternatives
- Explain that eligibility data may be incomplete

---

## 11. Trust and governance

### Card-level trust panel

Show:

- Primary issuer source
- MITC/terms link
- Effective date
- Last checked date
- What is verified vs inferred
- Version history
- Known conflicting terms
- Application availability
- Commercial relationship disclosure
- User-report status, clearly separated from issuer-confirmed terms

### Catalogue rules

- Every rate and benefit rule requires an effective date.
- Never overwrite historical terms; create a new version.
- Separate base product terms from temporary acquisition offers.
- Detect duplicate variants and mismatched card images/names.
- Automatically flag expired source pages and old verification dates.
- Maintain explicit `unknown`, not just `true/false`.
- Do not elevate partner cards or suppress non-partner cards.
- Label invite-only, upgrade-only, branch-only, and discontinued cards before users begin an application.
- Present community reports as evidence requiring corroboration, not confirmed policy.

---

## 12. Recommended default experience

For the existing prototype, the highest-impact next release would add:

1. Search with intent and alias parsing
2. Quick filters for LTF, RuPay UPI, cashback, lounge, low forex, and secured cards
3. Issuer, network, co-brand, and active-application filters
4. Structured annual fee and fee-waiver semantics
5. Spend-category inputs with caps and exclusions
6. Lounge spend-gate filtering
7. Separate economic, eligibility, and confidence scores
8. Year-one versus ongoing net-value calculations
9. Issuer-source and last-verified indicators
10. No-results relaxation with recovered-result counts

This gives advanced users meaningful control while keeping the default catalogue usable for someone who only knows, for example, “I want a low-fee card that rewards UPI and groceries.”