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
    assert "Ongoing est." in page.locator(".credit-card .value").first.text_content()
    assert "Year 1 not separately modeled" in page.locator(".credit-card .value").first.text_content()
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")

    initial = page.locator(".credit-card h3").first.text_content()
    page.get_by_label("New to credit", exact=True).check()
    page.locator("#fee").select_option("0")
    page.get_by_role("button", name="Refresh recommendations").click()
    changed = page.locator(".credit-card h3").first.text_content()
    assert changed == "FIRST WOW! (secured)", (initial, changed)

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
    first_catalog_name = page.locator(".catalog-card h3").first.text_content()
    page.locator(".profile-btn").first.click()
    assert page.locator("#profileModal").evaluate("el => el.classList.contains('open')")
    share_hash = page.evaluate("location.hash")
    assert share_hash.startswith("#card=")
    assert page.locator("#shareCard").is_visible()
    assert page.locator("#profileTitle").text_content() == first_catalog_name
    assert page.locator("#profileContent .fact").count() == 6
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
    page.goto(BASE_URL + share_hash, wait_until="networkidle")
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
    assert "6 matching cards" in page.locator("#catalogCount").text_content()
    assert page.locator(".catalog-card").count() == 6
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
    print(f"Ranking changed for new-to-credit profile: {initial} -> {changed}")
    print("No horizontal overflow; comparison modal has 10 rows; JS errors: 0")
    browser.close()
