# Verification report

## Automated checks

Executed against `http://127.0.0.1:4173` on 20 July 2026.

- HTML parsed successfully with Python `html.parser`.
- Local HTTP response succeeded.
- Browser console: zero JavaScript errors.
- Desktop visual inspection: no clipping or overflow; clear Configure + Compare composition.
- Playwright mobile viewport: 390 × 844.
- Seven current allow-listed recommendation cards rendered.
- Detailed form exposes 29 decision inputs: twelve spending fields, nine core fields and eight optional controls. Twenty-eight can influence ranking/safety; income is separate eligibility context.
- A ₹40,000 travel-only profile with travel rewards, optimizer complexity, travel redemption, international use and Visa preferences produces ATLAS Credit Card as the first detailed-math recommendation and passes the same profile into the 267-card product-fit ranking.
- Tata merchant-ecosystem preference increases the supported Tata Neu Plus product-fit score and emits an ecosystem-specific reason.
- Changing monthly income leaves both detailed economic order and catalogue product-affinity scores unchanged.
- The seven detailed models contain no hard-coded income threshold or credit-band eligibility fields.
- Exhaustive 267-card isolation checks require credit-history/card-stage changes to affect only supported FD-backed cards, and only positively.
- An all-zero spending profile emits an explicit “category affinity is not scored” limitation and never claims a largest-category or strong-everyday interaction.
- `May carry a balance` reveals the borrowing-cost safety warning, labels detailed cards “Not ranked for borrowing cost,” and disables personalized reward ordering in the market catalogue.
- The same safety route suppresses reward rows in comparison and reward scores, tags, cashback sections, reward economics and annual-value estimates in Learn profiles.
- All 267 catalogue cards produce deterministic product-fit scores in the bounded range 10–95, with at least two visible reasons and one of three evidence-confidence labels.
- Default-profile score-distribution QA requires at least eight distinct scores and fewer than ten cards at the 95-point ceiling; the focused audit observed 37 distinct scores across a 14–69 default-profile range.
- The questionnaire re-sorts the market-wide catalogue as well as the seven detailed-math cards; new-to-credit and first-card context changes only cards with supported FD-backed facts, always positively.
- Catalogue and profile disclosures state that product fit is not approval odds and that unknown terms do not count as benefits.
- No horizontal page overflow.
- New-to-credit plus zero-fee preference leaves the seven-card economic order unchanged while surfacing an FD-backed card and rationale in market-wide discovery.
- Two cards could be added to comparison.
- Comparison modal opened and rendered ten comparison rows, including a separate Year-one value row.
- Direct issuer verification links are present on every result card and inside comparison.
- Catalogue data integrity: 267 official-source rows, 16 issuers with verified rows, 17 issuer surfaces reviewed, zero duplicate IDs and zero missing required fields.
- Catalogue initially renders 18 cards and expands to 36 with “Show more”.
- Issuer, text-search, RuPay network, UPI, explicit-cashback-only and minimum-10%-cashback filters were exercised successfully.
- Explicit-cashback filtering returns 52 profiles; the minimum-10% filter returns 12. Highest-verified-cashback sorting places a 100% evidence record first without implying that it is uncapped or permanent.
- HDFC issuer filtering returned the expected 22 products.
- Catalogue official-fee-only filtering now uses the deeper profile evidence and returns 53 source-supported annual fees rather than only the six fees present in the original catalogue snapshot.
- Profile coverage: 267 profiles resolve to 267 catalogue IDs with zero missing profiles.
- Official-source enrichment: 230 canonical card profiles plus 37 provider-context profiles.
- Source ledger: 3,296 HTTPS evidence entries and 53 source-supported annual fees.
- Enriched profile UI renders official-term findings with an explicit human-review warning; provider-context profiles preserve the distinction between portfolio information and card contracts.
- Every one of the 267 profiles renders a cashback section. Validation finds 52 profiles with 136 explicit percentage-bearing official-source records; profiles without evidence render “No cashback percentage verified.”
- Every cashback record has a percentage in `(0, 100]`, structured condition fields, an HTTPS official source, a source description and an allowed evidence-review state. Reward points are not relabeled as cashback.
- Mobile QA verifies a known 5% profile, an unknown-state BOBCARD profile, official-source links, the non-conversion disclosure and one-column cashback cards.
- BOBCARD provider profiles surface the urgent re-verification state triggered by the July 2026 change notice.
- Every initially rendered catalogue card exposes a Learn action.
- Mobile profile modal opens with the matching card title, six known-fact tiles, cashback conditions, Fees & waiver, Reward economics, Year-one vs ongoing value, and at least two official evidence links.
- Opening a Learn profile writes a canonical `#card=<id>` URL, reloading that URL reopens the profile, Copy link remains visible, and closing the profile clears the hash.
- Profile close restores the catalogue and clears the modal state; the header/close control remains sticky while profile content scrolls.
- Comparison selection can be cleared from the fixed tray before browsing the catalogue.

Run again with:

```bash
python3 qa_test.py
```

## Mobile visual review

The full mobile flow is readable and unclipped. Result and catalogue cards correctly collapse to one column. Main filters become full-width controls; advanced boolean filters remain touch-sized chips. The fixed comparison tray now includes a nearby Clear action, preventing it from obstructing a long catalogue after comparison. The two-card comparison table fits at 390px without horizontal clipping; it is dense but readable. A three-card production comparison should switch to horizontal scrolling or a stacked factor view.

## Design slop audit

**Initial score: 0/10.**

- No generic tech gradient.
- Accent is a deliberate trust/financial green rather than default indigo.
- No generic three-feature marketing grid.
- No accent rails, blur/glass, monument stats or icon toppers.
- Composition is not center-stacked.
- Typography is deliberately Fraunces + DM Sans, not a default system/Inter choice.
- Surface is correctly Compare-first with Configure as the supporting surface.

No compositional repair was required. A trust defect found during QA—issuer links appearing only inside the comparison modal—was repaired by adding direct issuer verification links to every result row.

## Remaining prototype limitations

- Automated WCAG audit tooling was not added; semantic labels, focus styles, reduced-motion support and keyboard modal dismissal were manually/structurally checked.
- The discovery catalogue is broad but not guaranteed exhaustive or continuously fresh. Null means unknown rather than false or zero; only seven catalogue rows currently link to detailed reward economics.
- Three-card comparison at narrow mobile widths needs a dedicated stacked or horizontally scrollable treatment before launch.
