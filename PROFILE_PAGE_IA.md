# CardWise profile-page information architecture

**Jurisdiction:** India  
**Design as of:** 2026-07-18  
**Goal:** help a user learn whether a card deserves deeper consideration without implying approval, hiding exclusions, or converting uncertain points into fake cashback.

## 1. Page contract

Use two related templates:

- `/providers/:providerSlug` — teaches portfolio shape, issuer/program relationships, broad fit, and routes to products.
- `/cards/:cardSlug` — teaches one exact, versioned card contract and is the only page allowed to show calculated annual value.

For OneCard/FPL and other multi-party products, render a persistent identity line:

> **Card programme:** OneCard by FPL Technologies · **Issuing bank:** {bank} · Terms and charges are set by the applicable issuing bank.

Never merge products only because their display name or programme is shared. `cardVariantId + termsVersionId + issuerBankId` is the page identity.

## 2. Exact card-profile render order

### A. Sticky identity header

Desktop: 12-column grid, card art in columns 1–3 and identity/content in 4–9; action rail in 10–12. Mobile: one column.

Required content:

1. issuer + product name + network/variant;
2. status badge: `Modeled`, `Terms reviewed`, `Partial terms`, `Needs review`, or `Withdrawn`;
3. one-sentence neutral overview;
4. `Last checked {date}` plus `What this means` popover;
5. actions: `Compare`, `Save`, `Visit official site`;
6. sponsored disclosure adjacent to the outbound action, if applicable.

Do **not** put an estimated reward rate, star rating, “best” badge, or approval odds in the hero.

### B. “At a glance” decision strip

Five equal cards on desktop; horizontal-free 2-column grid on mobile:

- Annual fee: Year 1 / renewal, taxes explicit;
- Reward shape: e.g. `points`, `cashback`, `miles`, `mixed`; never flatten points to cash without a selected valuation;
- Best-known strength: sourced, max 70 characters;
- Biggest catch: most material cap/gate/exclusion, sourced;
- Published eligibility: `Meets checked`, `May meet`, `Does not meet`, or `Not fully published`.

Each tile links to the full section; the “biggest catch” tile is never visually de-emphasized.

### C. Overview

Answer in this order:

1. What is this card?
2. Who issues it and who operates any programme/co-brand?
3. What is the primary value proposition?
4. Is it a standard, secured/FD-backed, business, affinity, invite-only, or co-branded product?
5. Is it currently open to new applications?

Use 80–140 words plus a relationship diagram when more than one entity is involved.

### D. Cost

Use a two-tab control: `Year 1` and `Ongoing`. Default to `Ongoing` after a return visit; otherwise show both summary rows without hiding either.

Required rows:

- joining/first-year fee + taxes;
- renewal fee + taxes;
- fee-waiver threshold and excluded spend for waiver;
- APR/finance-charge range or `Assigned/not published`;
- late-payment fee formula/slabs;
- cash advance fee and interest start rule;
- foreign-currency markup + taxes;
- over-limit, replacement, rent/education/utility or other material service fees;
- reward-redemption fee;
- secured-card deposit amount/lien rule, when applicable.

Copy rules:

- Say `No annual fee` only when a current official source says so.
- Say `Lifetime free` only when both joining and renewal fee are contractually zero; do not infer it from a campaign.
- If APR is dynamic, display `Your assigned APR can vary` and prioritize borrowing cost over rewards for users who expect to carry a balance.

### E. Rewards

Render a rules table, not one “reward rate” number.

Columns:

| Spend/category | Earn rule | Eligible channel/merchant | Cap + reset | Rounding/min transaction | Value scenario | Source |
|---|---|---|---|---|---|---|

Then show:

1. base earn;
2. accelerated categories/merchants;
3. monthly/statement/annual caps;
4. milestone rewards;
5. redemption options and point expiry;
6. conservative value scenario and, optionally, a clearly separate high-value scenario;
7. a worked example with calculation trace.

Trace format:

> INR {spend} × {eligible share} → {points before cap} → {cap applied} → {points credited} × INR {selected value/point} = INR {estimated redemption value}.

A contractual earn rule and an editorial point valuation must be separate records and labels.

### F. Benefits

Group benefit cards by user job:

- Travel: lounges, forex, hotel/airline, insurance;
- Everyday: dining, grocery, fuel, movies, utilities;
- Milestones and fee waivers;
- Service and controls: app controls, concierge, fraud/lost-card provisions;
- Partner/affinity benefits.

Every benefit card must show: quantity, period, spend gate, registration/booking channel, guest rule, cap, validity, and source. Unknown fields display `Not stated in reviewed source`, not zero.

### G. Exclusions & catches

This is a first-class section immediately after benefits, never only inside an accordion.

Order by likely financial impact:

1. categories/MCCs that do not earn;
2. cap and reset behavior;
3. transactions excluded from milestones or fee waivers;
4. lounge spend gates and visit limits;
5. merchant/channel restrictions;
6. EMI, wallet, rent, fuel, utility, insurance, education, cash and government-payment treatment;
7. point expiry, conversion minimums and redemption fees;
8. benefit enrolment or coupon inventory limits;
9. acceptance/serviceability caveats;
10. partner eligibility constraints.

Use plain-language “Why it matters” alongside the legal statement. Example:

> **Fuel earns no points.** If fuel is a major part of your spend, do not apply the headline earn rate to it.

### H. Eligibility

Separate three concepts visually:

1. **Published checks** — age, residency, city/serviceability, income, account relationship, profession/membership, deposit requirement.
2. **Documents/process** — PAN, address/income proof, KYC; show only what the issuer requests.
3. **Issuer decision** — `Approval and limit remain subject to issuer underwriting; CardWise does not know unpublished criteria.`

Never show a percentage approval probability unless it comes from a validated, consented outcome model with methodology. Never call a user pre-approved from public criteria.

### I. Ideal user / Poor fit

Show two symmetric panels with 3–5 testable bullets each. Derive these from rules, not marketing personas.

Good bullet:

> `Pays in full and spends at least INR X in the eligible categories needed to recover the renewal fee.`

Bad bullet:

> `Perfect for savvy millennials.`

A `poor fit` panel is mandatory and equal in color weight and type size to `ideal user`.

### J. Source evidence

Use an always-visible source ledger, not citation numbers with no context.

Each row:

- claim group;
- source title;
- issuer/provider badge;
- source type: product page, MITC, schedule, reward terms, benefit terms, change notice;
- exact URL;
- exact locator (section/page/quote hash);
- issuer-effective date, if stated;
- CardWise observation date;
- reviewer status;
- `View source` and `Report mismatch`.

Priority: MITC/schedule and specific reward/benefit terms over generic marketing. When sources conflict, show `Conflict under review` and suppress the disputed calculated value.

### K. Freshness and history

End with a freshness panel and keep the compact date in the sticky header.

Required states:

- `Current source observed` — checked inside SLA;
- `Partial terms` — product presence is current but some economics are unreviewed;
- `Change announced` — show announced and effective dates;
- `Urgent re-verification` — a change is effective or sources conflict;
- `Stale` — SLA missed or repeated fetch failure;
- `Withdrawn` — retained for historical reference, no application CTA.

Panel fields:

- last full review;
- last automated source check;
- next review due;
- terms effective from;
- changed since previous version;
- link to change history;
- source failures/conflicts.

For BOBCARD, the 2026-07-15 revision notice should trigger `Urgent re-verification` until the changed card-level terms are approved.

## 3. Provider-profile differences

Provider pages use the same nine learning labels, but do **not** imply one portfolio-wide fee or rate.

1. **Overview:** issuer/program identity, portfolio shape, observed active count and scope.
2. **Cost:** fee bands only from current displayed products; otherwise `Varies by card`. Link to exact cards.
3. **Rewards:** enumerate reward systems/shapes, not one average rate.
4. **Benefits:** portfolio capabilities with `available on selected cards` labels.
5. **Exclusions:** explain that product terms control; surface provider-wide change alerts.
6. **Eligibility:** show segments (standard, secured, business, affinity) and only universal published criteria.
7. **Ideal user:** reasons to explore the portfolio.
8. **Poor fit:** structural mismatches, not card-specific verdicts.
9. **Source evidence + freshness:** catalogue, legal hub, current notices, count methodology.

Every observed product name is a link to a card profile or a `Discovered — detailed terms pending review` page. This preserves the 267-card discovery catalogue without inventing economics.

## 4. Implementation data contract

```ts
type EvidenceStatus =
  | 'modeled'
  | 'terms-reviewed'
  | 'partial-terms'
  | 'needs-review'
  | 'urgent-reverification'
  | 'stale'
  | 'withdrawn';

type Amount = { minor: number; currency: 'INR'; taxesExtra?: boolean };

type EvidenceRef = {
  id: string;
  sourceType: 'product-page' | 'mitc' | 'schedule' | 'reward-terms' |
    'benefit-terms' | 'change-notice' | 'catalogue';
  url: string;
  title: string;
  locator?: string;
  quotedTextHash?: string;
  effectiveFrom?: string;
  observedAt: string;
  reviewedAt?: string;
  reviewerStatus: 'approved' | 'candidate' | 'conflict' | 'unreachable';
};

type Sourced<T> = {
  value: T | null;
  unknownReason?: 'not-stated' | 'not-reviewed' | 'issuer-specific' | 'conflict';
  evidenceIds: string[];
};

type CardProfile = {
  cardVariantId: string;
  termsVersionId: string;
  providerId: string;
  issuerBankId: string;
  programmeOperatorId?: string;
  network?: Sourced<'Amex' | 'Visa' | 'Mastercard' | 'RuPay' | 'Other'>;
  status: EvidenceStatus;
  applicationStatus: Sourced<'open' | 'invite-only' | 'servicing-only' | 'withdrawn'>;
  overview: { neutralSummary: Sourced<string>; productType: Sourced<string> };
  cost: {
    joiningFee: Sourced<Amount>;
    renewalFee: Sourced<Amount>;
    feeWaiverRules: Rule[];
    apr: Sourced<{ minBps?: number; maxBps?: number; dynamic: boolean }>;
    serviceFees: FeeRule[];
  };
  rewards: {
    earnRules: EarnRule[];
    exclusions: ExclusionRule[];
    milestones: MilestoneRule[];
    redemptions: RedemptionRule[];
    editorialValuations: ValuationScenario[];
  };
  benefits: BenefitRule[];
  eligibility: EligibilityRule[];
  fit: { ideal: FitRule[]; poor: FitRule[] };
  freshness: {
    lastFullReview?: string;
    lastSourceCheck: string;
    nextReviewDue: string;
    effectiveFrom?: string;
    status: EvidenceStatus;
  };
  evidence: EvidenceRef[];
};
```

`Rule`, `FeeRule`, `EarnRule`, `BenefitRule`, `EligibilityRule`, and `FitRule` must carry `evidenceIds`, effective/observed time, conditions, cap, period, exclusions and priority. Do not serialize formatted rupee strings as canonical data.

## 5. Component map

```text
<CardProfilePage>
  <IdentityHeader />
  <DecisionStrip />
  <SectionNav />
  <OverviewSection />
  <CostSection yearTabs />
  <RewardRulesTable calculationTrace />
  <BenefitGroups />
  <ExclusionsSection alwaysExpanded />
  <EligibilitySection publishedVsIssuerDecision />
  <FitPanels symmetric />
  <EvidenceLedger />
  <FreshnessPanel changeHistory />
  <CompareTray clearAction />
</CardProfilePage>
```

Desktop section navigation may be sticky. Mobile uses a native-style `Jump to section` select; do not use a horizontally scrolling tab bar for ten sections.

## 6. UI copy and state rules

- `0` means sourced zero; `Unknown` means absent/unreviewed. Never coerce null to zero.
- Prefer `Earns 3 points per INR 100` to `3% back` unless the cash conversion is contractual.
- Prefer `Up to 4 visits, after INR X spend in Y period` to `Free lounges`.
- Prefer `May meet published criteria` to `High approval chance`.
- Prefer `Terms last checked 18 Jul 2026` to `Updated recently`.
- External CTA: `Visit official site`; avoid `Claim now`, fake countdowns, or application gates.
- When a source is stale/conflicted, suppress calculations and show the reason inline.
- If a user says they carry a balance, promote APR/borrowing-cost content above rewards and insert: `Rewards rarely offset finance charges.`

## 7. Responsive and accessibility acceptance criteria

- WCAG 2.2 AA contrast and keyboard operation.
- Logical H1 → H2 → H3 hierarchy matching the nine learning sections.
- Source links have descriptive labels; status is not color-only.
- Tables become labelled definition-card rows below 720 px, preserving every field.
- No horizontal page overflow at 320 px.
- Touch targets at least 44 × 44 CSS px.
- Sticky compare/action UI has an adjacent dismiss/clear control and never covers freshness or evidence.
- `aria-live="polite"` for comparison state, not for page-load marketing.
- Print/share view includes source URLs, last-checked date and exclusions.

## 8. Analytics that preserve trust

Track section views, source opens, mismatch reports, compare adds/removes, and official-site exits. Do not use payout or CTR fields in organic ranking. Preserve `termsVersionId` and source snapshot shown at outbound click time so the experience is auditable.

## 9. QA gates before publication

1. Every monetary/reward/eligibility/benefit claim has at least one approved official evidence reference.
2. Product identity includes issuing bank and programme operator where distinct.
3. First-year and ongoing fees are both visible.
4. At least one material catch is in the decision strip.
5. Exclusions are visible without opening a modal.
6. Unknown is never rendered as zero, `No fee`, `No cap`, or `All spends`.
7. Points are not presented as cashback without a sourced valuation scenario.
8. Published eligibility is not represented as approval.
9. Effective and observed dates are distinct.
10. BOBCARD records affected by the 2026-07-15 notice fail publication until reviewed.
11. OneCard records fail publication if `issuerBankId` or issuer-specific terms link is missing.
12. Federal Bank network variants are not promised from an illustrative catalogue display.
