## Audit outcome

The safest design is a **two-tier catalogue**:

1. **Discovery catalogue:** broad card coverage with only source-backed, filterable facts.
2. **Detailed reward models:** a small, explicitly allow-listed subset whose reward, fee-waiver, eligibility, cap, and lounge rules are complete enough to calculate.

**Never send catalogue-only cards through `evaluate()`.** A live check confirmed that an incomplete card currently throws:

```text
TypeError: Cannot read properties of undefined (reading 'online')
```

The existing eight-card UI otherwise rendered successfully, with unique IDs and no missing fields under the current flat schema.

---

# Implementation checklist

## 1. Split the embedded data

### Recommended files

To retain the current no-build static architecture:

- `data/catalogue.js`
- `data/reward-models.js`
- `index.html`
- `qa_test.py`

Load both data files before the application script. JavaScript files are safer than runtime JSON fetching for this prototype because they avoid asynchronous startup and `file://`/CORS issues.

### `data/catalogue.js`

Create one record for every discovered card:

```js
window.CARD_CATALOGUE = [
  {
    id: "sbi-cashback",           // immutable canonical ID
    issuerId: "sbi-card",
    issuer: "SBI Card",
    name: "CASHBACK SBI Card",
    status: "active",             // active | paused | discontinued | unknown
    networks: ["visa"],           // canonical lowercase enums
    cardType: "cashback",
    secured: false,
    cobranded: false,
    categories: ["online"],
    features: ["cashback"],
    annualFee: {
      amount: 999,
      currency: "INR",
      verified: true
    },
    sourceUrl: "...",
    checkedAt: "YYYY-MM-DD",
    detailLevel: "modeled"        // modeled | catalogue-only | stale
  }
];
```

Use `null`, not `0` or `false`, for unknown facts. For example, `annualFee.amount: null` means unknown; `0` means verified lifetime-free/no annual fee.

### `data/reward-models.js`

Move only calculation-specific data for the current eight cards here, keyed by catalogue ID:

```js
window.REWARD_MODELS = {
  "sbi-cashback": {
    modelVersion: "2026-07-18.1",
    baseRate: 0.01,
    categoryRates: {
      online: 0.05,
      travel: 0.05,
      dining: 0.02,
      fuel: 0,
      grocery: 0.01,
      general: 0.01
    },
    rewardCap: {
      amount: 5000,
      period: "month"
    },
    feeWaiver: {
      threshold: 200000,
      period: "year",
      eligibleSpendRule: "all-modeled-spend"
    },
    eligibility: {
      minMonthlyIncome: 25000,
      creditProfiles: ["fair", "good"],
      evidence: "indicative"
    },
    lounge: {
      visits: 0,
      period: "year",
      spendGate: null
    },
    note: "...",
    sourceUrl: "...",
    checkedAt: "YYYY-MM-DD"
  }
};
```

Do not carry forward ambiguous fields such as bare `cap`, `waiver`, or `lounges`. Their period and conditions must be explicit before migration.

### Data validation at startup

Add a validator that fails closed:

- Catalogue IDs must be unique.
- Every reward-model key must resolve to exactly one catalogue card.
- A modeled card must have all required calculation fields.
- Every rate must be finite and non-negative.
- Cap and waiver periods must be supported enums.
- Dates must be parseable.
- Source URLs must be HTTPS issuer sources where available.
- A `detailLevel: "modeled"` card without a valid model should be downgraded to `catalogue-only`, logged, and omitted from ranking.

Do not silently fill missing reward fields with zero; that would turn “unknown” into “no benefit.”

---

## 2. Separate application collections

Replace the current single `cards` collection around `index.html:49–58` with:

```js
const catalogue = window.CARD_CATALOGUE;
const rewardModels = window.REWARD_MODELS;

const catalogueById = new Map(catalogue.map(card => [card.id, card]));

const rankableCards = Object.entries(rewardModels)
  .map(([cardId, model]) => ({
    card: catalogueById.get(cardId),
    model
  }))
  .filter(validateRankableEntry);
```

Recommended state shape:

```js
const state = {
  ranked: [],             // evaluated modeled cards only
  discoveryResults: [],   // catalogue records after discovery filters
  selectedIds: [],
  discoveryFilters: {}
};
```

This makes it structurally difficult for a catalogue-only card to enter the calculator.

---

## 3. Refactor calculation boundaries

Change:

```js
evaluate(card, profile)
```

to:

```js
evaluate(card, model, profile)
```

The function should immediately reject invalid models:

```js
if (!card || !model || !isValidRewardModel(model)) {
  throw new TypeError(`Card ${card?.id ?? "unknown"} is not reward-modelled`);
}
```

Only the recommendation pipeline should call `evaluate()`:

```js
state.ranked = rankableCards.map(({card, model}) =>
  evaluate(card, model, profile)
);
```

Catalogue filtering and catalogue rendering must never call it.

Add deterministic tie-breakers to every sort:

1. requested metric;
2. card name;
3. stable card ID.

---

## 4. Separate discovery and recommendation UI

Do not mix a catalogue-only card into “Your ranked matches” with fake or blank scores.

### Recommended result sections

- **Personalized recommendations**
  - Only modeled cards.
  - Existing fit, estimated value, reason, and detailed comparison UI.
  - Header: “8 cards with detailed reward models.”

- **Browse the catalogue**
  - All active catalogue cards.
  - Facts and filters only.
  - Catalogue-only badge: “Reward estimate not yet modeled.”
  - No `/100 fit` or estimated annual value.
  - CTA: “View official terms,” not “Recommended” or “Apply.”

- Optional coverage summary:
  - `N cards discovered`
  - `M issuers`
  - `8 cards modeled`
  - `Last catalogue update`
  - Avoid claiming “all Indian cards” unless completeness can actually be substantiated.

### Useful discovery filters

Use normalized enum fields rather than free-form `tags`:

- text search;
- issuer;
- annual fee:
  - verified lifetime-free;
  - up to ₹500/₹1,000/₹2,500/₹5,000;
  - fee unknown;
- primary category;
- network: RuPay/Visa/Mastercard/Amex;
- RuPay/UPI support;
- lounge access: yes/no/unknown;
- secured vs unsecured;
- co-branded vs general;
- active/discontinued;
- “Detailed reward model available.”

Treat discovery filters as factual browsing constraints. Do not let them silently modify recommendation preferences or eligibility.

---

## 5. Make comparison capability-aware

Current `openComparison()` at `index.html:72` assumes every selected ID can be found and evaluated:

```js
evaluate(cards.find(c => c.id === id), p)
```

That will crash for removed, renamed, stale, or catalogue-only cards.

Implement either:

### Safest initial option

- Enable detailed comparison only for modeled cards.
- Catalogue-only cards get “Official terms” rather than “Add to compare.”

### More flexible option

Support two explicit comparison modes:

- **Basic catalogue comparison:** issuer, fee, network, card type, categories, source freshness.
- **Detailed modeled comparison:** rewards, net value, waiver, lounge, and eligibility.

For mixed selections, show “Not modeled” in calculated rows; never substitute zero.

Before opening comparison:

- resolve every ID through `catalogueById`;
- discard stale IDs;
- resolve models separately;
- disable calculated rows where a model is unavailable;
- preserve selected order instead of filtering in catalogue order.

---

## 6. Rendering and safety changes

The current renderer at `index.html:69` injects all card fields through `innerHTML`. This is tolerable only while data is hand-authored. A large imported catalogue introduces an XSS risk.

Checklist:

- Render imported names, issuers, tags, and notes with `textContent`.
- Validate outbound URLs with `new URL()` and allow only `https:`.
- Do not directly inject imported colors into `style`; use a controlled palette.
- Normalize tags/categories before rendering.
- Add pagination or incremental rendering for a large catalogue.
- Use event delegation on the result container instead of attaching a listener to every button after every render.
- Preserve filter and compare state when recommendation inputs change.

---

# Likely bugs and data-quality issues

## High priority

1. **Incomplete catalogue records crash evaluation.**  
   Confirmed through the running page.

2. **`cap` has no period.**  
   `evaluate()` applies it once to annual rewards. Some products have monthly caps, so annual value can be materially wrong.

3. **Fee-waiver spend is oversimplified.**  
   All annual spend counts toward `waiver`, even when issuer terms exclude rent, wallet, fuel, government, or other transactions.

4. **“Only lifetime-free” is not enforced.**  
   At `index.html:65`, a paid card receives perfect fee fit when its projected fee is waived. A spend-based waiver is not the same as a lifetime-free card.

5. **Unknown eligibility can become full fit.**  
   Several cards include `"unknown"` in `credit`; `includes()` then assigns `creditFit = 1`. “Not sure” should mean cannot assess, not perfect compatibility.

6. **Published eligibility and economic suitability are blended.**  
   A weak income/credit signal merely lowers the score. It is not distinguished as published mismatch, missing information, or unpublished issuer criteria.

7. **Fee excludes GST.**  
   Current net-value estimates subtract the headline annual fee only.

8. **Single-source provenance is insufficient.**  
   One product URL cannot establish fee, reward cap, exclusions, waiver, lounge, and eligibility. There is no checked date or stale status.

9. **Unknown and none are conflated.**  
   `lounges: 0`, `waiver: 0`, and similar values can mean either verified absence or missing data.

10. **Imported data would be injected unsafely.**  
    Names, tags, notes, colors, and URLs flow into `innerHTML`.

## Medium priority

11. **Comparison can evaluate `undefined`.**  
    A stale selected ID causes `cards.find()` to return nothing.

12. **Sorts lack explicit tie-breakers.**  
    Catalogue updates could make equal-score order depend on input order.

13. **Income bands are represented as exact amounts.**  
    “₹30,000–₹75,000” becomes `50000`, which can falsely pass or fail a published threshold.

14. **The 45% category-spend assumption is hidden inside code.**  
    Every profile assigns exactly 45% to the selected category, regardless of actual spending.

15. **Tag strings are doing too many jobs.**  
    Display labels, category classification, secured status, and network-like features should be separate typed fields.

16. **Annual fee sorting uses effective fee.**  
    A ₹5,000 card with a projected waiver can sort alongside a verified no-fee card, which may surprise users.

17. **Current RBL source is a generic catalogue page.**  
    The live data check found it is not product-specific.

18. **Accessibility gaps remain in the modal.**  
    It does not trap focus or return focus to the invoking control on close.

## Schema issue to fix before production use

In `schema.sql:77`, the overlap constraint uses a closed date range:

```sql
daterange(effective_from, coalesce(effective_to, 'infinity'::date), '[]')
```

Adjacent versions can overlap on the boundary. Prefer exclusive `effective_to` with `[)` semantics, or clearly define an inclusive end date and calculate the range accordingly.

---

# Test checklist

## Data-contract tests

- Catalogue IDs are unique and immutable.
- Reward-model keys all resolve to catalogue cards.
- Catalogue-only cards are accepted without reward fields.
- Modeled cards missing a required field fail validation and are not ranked.
- Unknown values remain `null`, not zero.
- Enum fields reject typos and uncontrolled tag variants.
- Source URL and `checkedAt` are present for publishable facts.
- No discontinued or stale model appears in recommendations.
- Duplicate issuer/name variants do not create duplicate canonical products.

## Calculator unit tests

- Catalogue-only input cannot reach `evaluate()`.
- Monthly, quarterly, and annual caps reset correctly.
- Fee waiver respects eligible-spend exclusions.
- GST is included where applicable.
- Exact threshold boundaries are tested.
- Zero-fee and spend-waived cards remain distinguishable.
- Unknown credit/income produces “cannot assess,” not full eligibility.
- Zero category rate remains zero; it must not fall back to base rate.
- Deterministic tie-breakers produce stable ordering.
- Missing model fields fail closed without breaking the rest of the page.
- Year-one and ongoing values are separated when relevant.

## Filter tests

- Search is case-insensitive and issuer/name aware.
- Multiple filters combine with documented AND/OR behavior.
- Fee-unknown cards appear only when that state is allowed.
- “Lifetime-free” excludes cards that merely have spend waivers.
- RuPay, secured, co-brand, lounge, category, and issuer filters work independently and together.
- Clearing filters restores the full discovery count.
- Filters never change the modeled-card calculation.

## UI/browser tests

Update `qa_test.py` so it no longer asserts that every `.credit-card` count equals eight.

Instead assert:

- personalized result count equals the number of valid reward models;
- discovery result count equals the catalogue fixture count;
- catalogue-only cards have no score or estimated yearly value;
- catalogue-only cards cannot enter detailed comparison;
- ranking still changes for the fuel profile;
- filtering changes discovery results without changing recommendation calculations;
- selected modeled cards survive filtering and rerendering;
- stale selected IDs do not crash comparison;
- compare limit remains enforced;
- no horizontal overflow with a long issuer/card name;
- no JavaScript errors with missing optional catalogue fields;
- keyboard focus returns after modal close;
- large-catalogue fixture renders acceptably with pagination/incremental loading.

## Regression fixtures

Keep a small fixed fixture containing:

- the current eight modeled cards;
- one valid catalogue-only card;
- one card with unknown fee;
- one discontinued card;
- one stale model;
- one secured RuPay card;
- one deliberately invalid reward model;
- duplicate-ID fixture expected to fail validation.

---

## Files and verification

- **Files modified or created:** none.
- **Verification performed:** inspected `index.html`, `qa_test.py`, `schema.sql`, and architecture/methodology docs; opened the existing running app and inspected live state.
- **Issue encountered:** starting another local server failed because port `4173` was already occupied; the existing server was reachable and used for verification.