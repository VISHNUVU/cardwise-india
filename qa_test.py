import os
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "artifacts"
OUT.mkdir(exist_ok=True)
BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:4173")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(BASE_URL, wait_until="networkidle")

    assert page.title().startswith("CardWise")
    assert page.locator(".credit-card").count() == 7
    assert page.evaluate("cards.every(card => !('minIncome' in card) && !('credit' in card))")
    ranking_selectors = [
        "#onlineSpend", "#grocerySpend", "#diningSpend", "#travelSpend", "#fuelSpend", "#utilitySpend",
        "#insuranceSpend", "#rentEducationSpend", "#healthcareSpend", "#transitSpend", "#entertainmentSpend", "#generalSpend",
        "[name=goal]", "[name=credit]", "[name=stage]", "#fee", "[name=lounge]", "#forexSpend", "[name=upiPreference]", "#networkPreference",
        "[name=payment]", "#complexityPreference", "#redemptionPreference", "[name=waiverOkay]", "#spendPattern", "#upiMonthlySpend", "#ecosystemPreference", "[name=existingLounge]",
    ]
    assert len(ranking_selectors) == 28 and all(page.locator(selector).count() for selector in ranking_selectors)
    assert page.locator("#income").count() == 1 and "#income" not in ranking_selectors
    assert "Ongoing est." in page.locator(".credit-card .value").first.text_content()
    assert "Year 1 not separately modeled" in page.locator(".credit-card .value").first.text_content()
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")

    initial = page.locator(".credit-card h3").first.text_content()
    default_scores = page.evaluate("Object.fromEntries(window.cardCatalogue.map(card => [card.id, window.cardwiseProductFit(card).score]))")
    secured_ids = set(page.evaluate("Object.entries(window.cardProfiles).filter(([, profile]) => profile.knownFacts.secured.value === true).map(([id]) => id)"))
    page.get_by_label("New to credit", exact=True).check()
    page.get_by_role("button", name="Recommend cards").click()
    new_credit_scores = page.evaluate("Object.fromEntries(window.cardCatalogue.map(card => [card.id, window.cardwiseProductFit(card).score]))")
    credit_deltas = {card_id: new_credit_scores[card_id] - score for card_id, score in default_scores.items() if new_credit_scores[card_id] != score}
    assert set(credit_deltas) <= secured_ids
    assert credit_deltas and all(delta > 0 for delta in credit_deltas.values())
    page.get_by_label("Good (750+)", exact=True).check()
    page.get_by_label("My first card", exact=True).check()
    page.get_by_role("button", name="Recommend cards").click()
    first_card_scores = page.evaluate("Object.fromEntries(window.cardCatalogue.map(card => [card.id, window.cardwiseProductFit(card).score]))")
    stage_deltas = {card_id: first_card_scores[card_id] - score for card_id, score in default_scores.items() if first_card_scores[card_id] != score}
    assert set(stage_deltas) <= secured_ids
    assert stage_deltas and all(delta > 0 for delta in stage_deltas.values())
    page.get_by_label("New to credit", exact=True).check()
    page.get_by_label("Add another card", exact=True).check()
    page.locator("#fee").select_option("0")
    page.get_by_role("button", name="Recommend cards").click()
    changed = page.locator(".credit-card h3").first.text_content()
    assert changed == initial, (initial, changed)  # credit context must not alter economic order
    assert "fd-backed" in page.locator(".catalog-card .catalog-reasons").first.text_content().lower()

    # The same questionnaire ranks the complete discovery catalogue using
    # supported facts and explicitly editorial affinity, without inventing economics.
    assert page.locator("#catalogSort").input_value() == "personalized"
    assert page.locator(".catalog-card .catalog-fit").count() == 18
    assert page.locator(".catalog-card .catalog-fit-score").first.is_visible()
    assert "/100 product fit" in page.locator(".catalog-card .catalog-fit-score").first.text_content()
    assert page.locator(".catalog-card .catalog-reasons li").count() >= 2
    assert "new-to-credit" in page.locator(".catalog-card .catalog-reasons").first.text_content().lower()
    assert page.locator("#recommendationDisclosure").is_visible()
    assert "not approval odds" in page.locator("#recommendationDisclosure").text_content().lower()
    broad_scores = page.evaluate("""() => window.cardCatalogue.map(card => window.cardwiseProductFit(card))""")
    assert len(broad_scores) == 267
    assert all(10 <= item["score"] <= 95 for item in broad_scores)
    assert all(len(item["reasons"]) >= 2 for item in broad_scores)
    assert {item["confidence"] for item in broad_scores} <= {"Detailed maths", "More evidence", "Limited evidence"}
    assert len({item["score"] for item in broad_scores}) >= 8
    assert sum(item["score"] == 95 for item in broad_scores) < 10

    # Detailed form drives category-level economics and broader product fit.
    assert page.locator(".spend-input").count() == 12
    assert page.locator("#fineTune").is_visible()
    page.locator("#fineTune").click()
    for field in ["onlineSpend", "grocerySpend", "diningSpend", "travelSpend", "fuelSpend", "utilitySpend", "generalSpend", "insuranceSpend", "rentEducationSpend", "healthcareSpend", "transitSpend", "entertainmentSpend"]:
        page.locator(f"#{field}").fill("0")
    page.get_by_role("button", name="Recommend cards").click()
    zero_spend_reasons = page.evaluate("window.cardCatalogue.flatMap(card => window.cardwiseProductFit(card).reasons)")
    assert not any("strong everyday" in reason.lower() or "largest spending category" in reason.lower() for reason in zero_spend_reasons)
    page.locator("#travelSpend").fill("40000")
    page.get_by_label("Travel rewards", exact=True).check()
    page.get_by_label("Good (750+)", exact=True).check()
    page.locator("#fee").select_option("10000")
    page.get_by_label("Useful", exact=True).check()
    page.locator("#forexSpend").select_option("high")
    page.locator("#networkPreference").select_option("Visa")
    page.get_by_label("Add another card", exact=True).check()
    page.get_by_label("Always pay in full", exact=True).check()
    page.locator("#complexityPreference").select_option("optimizer")
    page.locator("#redemptionPreference").select_option("travel")
    page.get_by_label("Spend-based waiver is acceptable", exact=True).check()
    page.locator("#spendPattern").select_option("seasonal")
    page.locator("#upiMonthlySpend").fill("3000")
    page.locator("#ecosystemPreference").select_option("none")
    page.get_by_label("I already have lounge access", exact=True).check()
    page.get_by_role("button", name="Recommend cards").click()
    detailed_profile = page.evaluate("window.cardwiseCurrentProfile")
    assert detailed_profile["spend"] == 40000
    assert detailed_profile["spending"]["travel"] == 40000
    assert detailed_profile["goal"] == "travel"
    assert detailed_profile["payment"] == "full"
    assert detailed_profile["complexity"] == "optimizer"
    assert detailed_profile["redemption"] == "travel"
    assert detailed_profile["waiverOkay"] == 1
    assert detailed_profile["spendPattern"] == "seasonal"
    assert detailed_profile["upiSpend"] == 3000
    assert detailed_profile["existingLounge"] == 1
    assert page.locator(".credit-card h3").first.text_content() == "ATLAS Credit Card"
    assert "travel rewards" in page.locator("#summary").text_content().lower()
    assert "travel" in page.locator(".catalog-card .catalog-reasons").first.text_content().lower()
    assert "28 ranking signals + 1 eligibility context" in page.locator("#signalSummary").text_content().lower()

    atlas_name_before = page.locator(".credit-card h3").first.text_content()
    atlas_score_before = page.locator(".credit-card .score").first.text_content()
    market_scores_before = page.evaluate("Object.fromEntries(window.cardCatalogue.map(card => [card.id, window.cardwiseProductFit(card).score]))")
    page.locator("#income").select_option("200000")
    page.get_by_role("button", name="Recommend cards").click()
    assert page.locator(".credit-card h3").first.text_content() == atlas_name_before
    assert page.locator(".credit-card .score").first.text_content() == atlas_score_before
    assert page.evaluate("Object.fromEntries(window.cardCatalogue.map(card => [card.id, window.cardwiseProductFit(card).score]))") == market_scores_before

    tata_before = page.evaluate("window.cardwiseProductFit(window.cardCatalogue.find(card => card.name === 'Tata Neu Plus HDFC Bank Credit Card'))")
    page.locator("#ecosystemPreference").select_option("tata")
    page.get_by_role("button", name="Recommend cards").click()
    tata_after = page.evaluate("window.cardwiseProductFit(window.cardCatalogue.find(card => card.name === 'Tata Neu Plus HDFC Bank Credit Card'))")
    assert tata_after["score"] > tata_before["score"]
    assert any("ecosystem" in reason.lower() for reason in tata_after["reasons"])
    page.locator("#ecosystemPreference").select_option("none")

    page.get_by_label("May carry a balance", exact=True).check()
    page.get_by_role("button", name="Recommend cards").click()
    assert page.locator("#borrowingSafety").is_visible()
    assert page.locator("#marketBorrowingSafety").is_visible()
    assert page.locator("#catalogTitle").text_content() == "Cards not ranked for borrowing cost"
    assert "rewards ranking may be unsuitable" in page.locator("#borrowingSafety").text_content().lower()
    assert "not ranked for borrowing cost" in page.locator(".credit-card .score").first.text_content().lower()
    assert page.locator("#sort").is_disabled()
    assert page.locator("#catalogSort").is_disabled()
    assert page.locator(".credit-card .tags").count() == 0
    assert page.locator(".catalog-card .catalog-tags").count() == 0
    page.locator(".compare-btn").nth(0).click()
    page.locator(".compare-btn").nth(1).click()
    page.get_by_role("button", name="Compare now").click()
    assert page.locator(".compare-table tbody tr").count() == 4
    assert page.locator("#compareContent").get_by_text("Estimated yearly rewards", exact=True).count() == 0
    carry_comparison_text = page.locator("#compareContent").inner_text()
    reward_notes = page.evaluate("cards.map(card => card.note)")
    assert all(note not in carry_comparison_text for note in reward_notes)
    assert "Verify current APR, finance charges and repayment rules" in carry_comparison_text
    page.get_by_role("button", name="Close comparison").click()
    page.locator("#clearCompare").click()
    page.locator(".profile-btn").first.click()
    assert "not ranked for borrowing cost" in page.locator("#profileContent").text_content().lower()
    assert page.locator("#profileContent .profile-recommendation").count() == 0
    assert page.locator("#profileContent .cashback-offer").count() == 0
    assert page.locator("#profileContent").get_by_text("Reward economics", exact=True).count() == 0
    assert page.locator("#profileContent").get_by_text("Year-one vs ongoing value", exact=True).count() == 0
    page.locator("#closeProfile").click()
    page.get_by_label("Always pay in full", exact=True).check()
    page.get_by_role("button", name="Recommend cards").click()
    assert not page.locator("#sort").is_disabled()
    assert not page.locator("#catalogSort").is_disabled()
    assert page.locator("#catalogTitle").text_content() == "Recommended cards across the market"

    # Comparison remains available after returning to the paid-in-full route.
    page.locator(".compare-btn").nth(0).click()
    page.locator(".compare-btn").nth(1).click()
    assert page.locator("#tray").evaluate("el => el.classList.contains('show')")
    page.get_by_role("button", name="Compare now").click()
    assert page.locator("#modal").evaluate("el => el.classList.contains('open')")
    assert page.locator(".compare-table tbody tr").count() == 10
    assert page.locator(".compare-table").get_by_text("Year-one value", exact=True).is_visible()
    page.get_by_role("button", name="Close comparison").click()
    page.locator("#clearCompare").click()
    assert not page.locator("#tray").evaluate("el => el.classList.contains('show')")

    # Broad catalogue and useful filters.
    assert page.locator("#coverageTotal").text_content() == "267 cards"
    assert "16 issuers with cards" in page.locator("#coverageIssuers").text_content()
    assert "17 reviewed" in page.locator("#coverageIssuers").text_content()
    assert "230 card-level enriched" in page.locator("#coverageIssuers").text_content()
    assert "52 with explicit cashback %" in page.locator("#coverageIssuers").text_content()
    assert page.locator(".catalog-card").count() == 18
    assert page.locator(".profile-btn").count() == 18
    page.locator("#catalogSearch").fill("Amazon Pay ICICI Bank Credit Card")
    assert page.locator(".catalog-card").count() == 1
    first_catalog_name = page.locator(".catalog-card h3").first.text_content()
    page.locator(".profile-btn").first.click()
    assert page.locator("#profileModal").evaluate("el => el.classList.contains('open')")
    share_hash = page.evaluate("location.hash")
    assert share_hash.startswith("#card=")
    assert page.locator("#shareCard").is_visible()
    assert page.locator("#profileTitle").text_content() == first_catalog_name
    assert page.locator("#profileContent .profile-recommendation").is_visible()
    assert "/100 product fit" in page.locator("#profileContent .profile-recommendation").text_content()
    assert "not approval odds" in page.locator("#profileContent .profile-recommendation").text_content().lower()
    assert page.locator("#profileContent .profile-section").first.locator(".fact").count() == 6
    assert page.locator("#profileContent .profile-section").count() >= 7
    assert page.locator("#profileContent").get_by_text("Cashback offers & percentages", exact=True).is_visible()
    assert page.locator("#profileContent .cashback-offer").count() >= 1
    assert "5%" in page.locator("#profileContent .cashback-rate").all_text_contents()
    assert page.locator("#profileContent .cashback-offer a[href^='https://']").count() >= 1
    assert page.locator("#profileContent .cashback-conditions").count() >= 1
    assert page.locator("#profileContent").get_by_text("Fees & waiver", exact=True).is_visible()
    assert page.locator("#profileContent").get_by_text("Reward economics", exact=True).is_visible()
    assert page.locator("#profileContent").get_by_text("Year-one vs ongoing value", exact=True).is_visible()
    assert page.locator("#profileContent").get_by_text("Reward points are not converted into cashback percentages", exact=False).is_visible()
    assert page.locator("#profileContent .research-fact").count() >= 1
    assert page.locator("#profileContent .evidence-link").count() >= 2
    assert page.locator("body").evaluate("el => el.style.overflow") == "hidden"
    page.locator("#profileModal .modal-panel").evaluate("el => el.scrollTop = el.scrollHeight")
    close_box = page.locator("#closeProfile").bounding_box()
    assert close_box and 0 <= close_box["y"] < 100
    assert page.locator("#profileContent .evidence-link").last.is_visible()
    page.locator("#profileModal .modal-panel").evaluate("el => el.scrollTop = 0")
    page.screenshot(path=str(OUT / "mobile-profile.png"), full_page=False)
    page.locator("#profileContent").get_by_text("Cashback offers & percentages", exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / "mobile-cashback-profile.png"), full_page=False)
    page.locator("#profileContent").get_by_text("Year-one vs ongoing value", exact=True).scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / "mobile-decision-details.png"), full_page=False)
    page.locator("#profileModal .modal-panel").evaluate("el => el.scrollTop = 0")
    page.locator("#closeProfile").click()
    assert page.evaluate("location.hash") == ""
    assert page.locator("body").evaluate("el => el.style.overflow") == ""
    assert not page.locator("#profileModal").evaluate("el => el.classList.contains('open')")
    page.locator("#catalogSearch").fill("")
    page.goto(BASE_URL + share_hash, wait_until="networkidle")
    page.reload(wait_until="networkidle")
    assert page.locator("#profileModal").evaluate("el => el.classList.contains('open')")
    assert page.locator("#profileTitle").text_content() == first_catalog_name
    page.locator("#closeProfile").click()
    page.locator("#issuerFilter").select_option(label="BOBCARD")
    assert "26 matching cards" in page.locator("#catalogCount").text_content()
    page.locator(".profile-btn").first.click()
    assert page.locator("#profileContent").get_by_text("BOBCARD provider context", exact=True).is_visible()
    assert page.locator("#profileContent .freshness-alert").count() == 1
    assert page.locator("#profileContent .cashback-offer").count() == 0
    assert page.locator("#profileContent").get_by_text("No cashback percentage verified", exact=True).is_visible()
    page.locator("#closeProfile").click()
    page.locator("#issuerFilter").select_option(label="HDFC Bank")
    assert "22 matching cards" in page.locator("#catalogCount").text_content()
    page.locator("#issuerFilter").select_option("")
    page.locator("#networkFilter").select_option("RuPay")
    assert page.locator(".catalog-card").count() > 0
    page.locator("#networkFilter").select_option("")
    page.locator("#catalogSearch").fill("railway")
    assert "matching cards" in page.locator("#catalogCount").text_content()
    assert page.locator(".catalog-card").count() >= 2
    page.locator("#catalogSearch").fill("")
    page.locator(".advanced").evaluate("el => el.open = true")
    page.locator("#upiFilter").check()
    assert page.locator(".catalog-card").count() > 0
    assert "matching cards" in page.locator("#catalogCount").text_content()
    page.locator("#upiFilter").uncheck()
    page.locator("#feeKnownFilter").check()
    assert "53 matching cards" in page.locator("#catalogCount").text_content()
    assert page.locator(".catalog-card").count() == 18
    page.locator("#catalogFilters").evaluate("form => form.reset()")
    page.wait_for_timeout(50)
    page.locator("#cashbackOnlyFilter").check()
    assert "52 matching cards" in page.locator("#catalogCount").text_content()
    page.locator("#cashbackMinFilter").select_option("10")
    assert "12 matching cards" in page.locator("#catalogCount").text_content()
    page.locator("#catalogSort").select_option("cashback")
    page.locator(".profile-btn").first.click()
    assert page.locator("#profileContent .cashback-rate").first.text_content() == "100%"
    page.locator("#closeProfile").click()
    page.locator("#catalogFilters").evaluate("form => form.reset()")
    page.wait_for_timeout(50)
    assert page.locator(".catalog-card").count() == 18
    page.locator("#loadMore").click()
    assert page.locator(".catalog-card").count() == 36

    page.screenshot(path=str(OUT / "mobile-page.png"), full_page=True)

    assert not errors, errors
    print("Playwright mobile QA: PASS")
    print(f"Economic order remains eligibility-independent: {initial}; market discovery surfaces FD-backed evidence")
    print("No horizontal overflow; comparison modal has 10 rows; JS errors: 0")
    browser.close()
