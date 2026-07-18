#!/usr/bin/env python3
"""Build source-backed sparse enrichments for seven issuer catalogues.

This script expects official catalogue HTML captured under /tmp/cardwise_official and
official terms captured/extracted under /tmp/cardwise_terms. It intentionally leaves
unsupported values null instead of inferring terms.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED = "2026-07-18"
TARGETS = {
    "AU Small Finance Bank",
    "IndusInd Bank",
    "Kotak Mahindra Bank",
    "YES BANK",
    "RBL Bank",
    "HSBC India",
    "Standard Chartered India",
}
CATALOG_INDEX = {
    "HSBC India": 25,
    "IndusInd Bank": 26,
    "Kotak Mahindra Bank": 27,
    "RBL Bank": 28,
    "Standard Chartered India": 29,
    "YES BANK": 30,
}
TERMS = {
    "IndusInd Bank": [
        "https://www.indusind.bank.in/in/en/personal/schedule-of-charges.html",
        "https://www.indusind.bank.in/in/en/personal/terms-and-conditions.html",
    ],
    "Kotak Mahindra Bank": [
        "https://www.kotak.bank.in/en/personal-banking/cards/credit-cards/mitc-and-ca.html",
        "https://www.kotak.bank.in/en/personal-banking/cards/credit-cards/kfs.html",
    ],
    "RBL Bank": [
        "https://webassets.rbl.bank.in/document/Credit%20Cards/RBL-MITC-final.pdf",
        "https://webassets.rbl.bank.in/document/Credit%20Cards/CardsScheduleCharges.pdf",
    ],
    "HSBC India": ["https://www.hsbc.co.in/help/rates-and-fees/"],
    "Standard Chartered India": [],
    "YES BANK": [],
    "AU Small Finance Bank": [],
}
SC_TERMS = {
    "Rewards Credit Card": "https://av.sc.com/in/content/docs/in-rewardscard-product-terms-and-conditions.pdf",
    "Standard Chartered EaseMyTrip Credit Card": "https://av.sc.com/in/content/docs/in-easemytrip-product-terms-and-conditions.pdf",
    "Smart Credit Card": "https://av.sc.com/in/content/docs/in-smartcard-product-terms-and-conditions.pdf",
    "Ultimate Credit Card": "https://av.sc.com/in/content/docs/in-ultimate-credit-card-tnc.pdf",
    "Platinum Rewards Card": "https://av.sc.com/in/content/docs/in-sc-platinum-rewards-credit-card-tcs.pdf",
}
HSBC_PRODUCT_URLS = {
    "HSBC Taj Credit Card": "https://www.hsbc.co.in/credit-cards/products/taj/",
    "HSBC TravelOne Credit Card": "https://www.hsbc.co.in/credit-cards/products/travelone/",
    "HSBC Live+ Credit Card": "https://www.hsbc.co.in/credit-cards/products/live-plus/",
    "HSBC Premier Credit Card": "https://www.hsbc.co.in/credit-cards/products/premier/",
    "HSBC Visa Platinum Credit Card": "https://www.hsbc.co.in/credit-cards/products/visa-platinum/",
    "HSBC RuPay Platinum Credit Card": "https://www.hsbc.co.in/credit-cards/products/rupay-platinum-credit-card/",
    "HSBC RuPay Cashback Credit Card": "https://www.hsbc.co.in/credit-cards/products/rupay-cashback-credit-card/",
}


def clean(raw: str) -> str:
    raw = raw.replace("\\n", "\n").replace("\\r", "\n").replace("\\t", " ")
    raw = raw.replace('\\"', '"').replace("\\/", "/")
    raw = html.unescape(raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n\s*\n+", "\n", raw)
    return raw


def variants(name: str) -> list[str]:
    vals = [name]
    vals.append(re.sub(r"^(HSBC|IndusInd Bank|Standard Chartered|YES|RBL Bank)\s+", "", name, flags=re.I))
    vals.append(re.sub(r"\s+Credit Card$|\s+Card$", "", name, flags=re.I))
    if "Visa/Mastercard" in name:
        vals.append(name.replace("Visa/Mastercard", "Visa/Master"))
    return list(dict.fromkeys(v for v in vals if len(v) > 4))


def product_block(text: str, name: str, all_names: list[str]) -> list[str]:
    candidates = []
    for v in variants(name):
        for match in re.finditer(re.escape(v), text, re.I):
            lines = [x.strip(" -•\t") for x in text[match.start():match.start() + 2200].splitlines()]
            lines = [x for x in lines if x]
            block = []
            for idx, line in enumerate(lines):
                if idx > 0 and any(line.casefold() == ov.casefold() for other in all_names if other != name for ov in variants(other)):
                    break
                block.append(line)
                if idx >= 2 and line.casefold() in {"add to compare", "know more", "find out more"}:
                    break
            joined = " ".join(block).lower()
            score = 10 * ("key features and benefits" in joined)
            score += 4 * ("joining fee" in joined) + 4 * ("annual fee" in joined)
            score += sum(k in joined for k in ("reward", "cashback", "lounge", "forex", "fuel"))
            score += 3 * bool(block and any(block[0].casefold() == v.casefold() for v in variants(name)))
            candidates.append((score, -len(block), block))
    if not candidates:
        return []
    return max(candidates, key=lambda x: (x[0], x[1]))[2]


def supported_statements(block: list[str]) -> list[str]:
    keys = ("joining fee", "annual fee", "reward", "cashback", "air mile", "avios", "smile", "lounge", "forex", "foreign currency", "fuel", "waiver", "eligible", "eligibility", "invite-only", "government sector", "priority bank")
    skip = {"key features and benefits", "apply now", "know more", "add to compare", "compare"}
    out = []
    for line in block:
        line = re.sub(r"\s+", " ", line).strip()
        if not (8 <= len(line) <= 500) or line.casefold() in skip:
            continue
        if any(k in line.casefold() for k in keys) and line not in out:
            out.append(line)
    return out[:16]


def value(v, status="official_source"):
    return {"value": v, "status": status if v is not None else "unknown"}


def parse_money(pattern: str, text: str):
    match = re.search(pattern, text, re.I)
    if not match:
        return None
    token = match.group(1).replace(",", "").strip().lower()
    if token in {"nil", "0"}:
        return 0
    try:
        return int(float(token))
    except ValueError:
        return None


def parse_percentage(text: str, keyword: str):
    patterns = [
        rf"(\d+(?:\.\d+)?)%[^.\n]{{0,80}}{keyword}",
        rf"{keyword}[^.\n]{{0,80}}?(\d+(?:\.\d+)?)%",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return float(match.group(1))
    return None


def evidence(label, url, locator, supports, statements=None, access="accessible"):
    item = {
        "label": label,
        "url": url,
        "checkedAt": CHECKED,
        "access": access,
        "locator": locator,
        "supports": supports,
    }
    if statements:
        item["statements"] = statements
    return item


def apply_special(profile):
    issuer = profile["issuer"]
    name = profile["cardName"]
    f = profile["facts"]
    ev = profile["sources"]
    if issuer == "HSBC India":
        common_eligibility = [
            "Age 18-65 if salaried or 25-65 if self-employed",
            "Minimum annual income INR 600,000 if salaried or INR 1,200,000 if self-employed",
            "Indian resident and resident in one of the cities listed on the product page",
        ]
        hsbc = {
            "HSBC Taj Credit Card": {
                "fees": (110000, 110000, None),
                "rewards": {"earn": ["1.5 RP per INR 100 on standard purchases", "5 RP per INR 100 at listed participating IHCL brands"], "redemption": "1.5 RP = INR 1 in the HSBC Taj Credit Card Wallet"},
                "lounge": {"access": "Unlimited airport lounge access globally; product page also states Chambers/Taj Club visit limits", "spendGate": None},
                "network": "Visa Infinite",
                "eligibility": ["Age 25-75", "Indian resident, or an NRI who already has an HSBC India bank account", "Minimum annual income INR 3,600,000 salaried or INR 4,500,000 self-employed", "Residence in one of the cities listed on the product page"],
            },
            "HSBC TravelOne Credit Card": {
                "fees": (4999, 4999, "Annual fee waived if annual spend exceeds INR 800,000"),
                "rewards": {"earn": ["4 RP per INR 100 on flights, travel aggregators and foreign-currency spend", "2 RP per INR 100 on other eligible spend with no cap stated on the page", "10,000 bonus RP on annual spend above INR 1,200,000"]},
                "lounge": {"access": "6 domestic and 4 international airport lounge visits per year", "spendGate": None},
                "eligibility": common_eligibility,
            },
            "HSBC Live+ Credit Card": {
                "fees": (999, 999, "Annual fee waived if annual spend exceeds INR 200,000"),
                "rewards": {"cashback": ["10% on dining, food delivery and grocery spend, capped at INR 1,000 per month", "1.5% unlimited cashback on most other spend; exclusions apply"]},
                "lounge": {"access": "4 complimentary domestic visits per year, one per quarter", "spendGate": None},
                "network": "Visa Signature",
                "eligibility": common_eligibility,
            },
            "HSBC Premier Credit Card": {
                "fees": (12000, 20000, "Renewal fee waived while HSBC Premier eligibility criteria are met"),
                "rewards": {"earn": ["3 RP per INR 100", "Up to 12X RP on hotels, flights and car rentals through Travel with Points"], "redemption": "1 RP = INR 1 at Apple and selected airline partners; product page also lists 1:1 transfer partners"},
                "lounge": {"access": "Unlimited domestic and international access for cardholders plus 8 international guest visits", "spendGate": None},
                "fuel": "1% fuel surcharge waiver on INR 400-INR 4,000 transactions",
                "network": "Mastercard",
                "eligibility": ["Existing HSBC Premier customer", "Meet at least one published Premier relationship, salary or mortgage criterion; see source for the current thresholds"],
            },
            "HSBC Visa Platinum Credit Card": {
                "fees": (0, 0, None),
                "rewards": {"earn": ["2 RP per INR 150", "Up to 6X RP on hotels, flights and car rentals through Travel with Points"]},
                "fuel": "Fuel surcharge waiver up to INR 250 per month on INR 400-INR 4,000 fuel payments; separate contactless fuel cashback capped by spend/quarter",
                "network": "Visa",
                "eligibility": common_eligibility,
            },
            "HSBC RuPay Platinum Credit Card": {
                "fees": (0, 0, None),
                "rewards": {"earn": ["2 RP per INR 150", "Reward points on eligible UPI payments"]},
                "fuel": "Product page advertises annual fuel-surcharge savings up to INR 3,000; transaction rules are in the linked waiver terms",
                "network": "RuPay (international acceptance via JCB)",
                "eligibility": common_eligibility,
            },
            "HSBC RuPay Cashback Credit Card": {
                "fees": (499, 499, "Annual fee waived if annual spend exceeds INR 200,000"),
                "rewards": {"cashback": ["10% on dining, food delivery and grocery spend", "1% on other eligible spend", "Total cashback up to INR 400 per month"]},
                "lounge": {"access": "Up to 2 domestic visits per quarter and 2 international visits per year", "spendGate": None},
                "forex": 0.0,
                "forexNote": "0% promotional forex markup stated through 31 July 2026; re-check after that date",
                "network": "RuPay (international acceptance via JCB)",
                "eligibility": common_eligibility,
            },
        }[name]
        joining, annual, waiver = hsbc["fees"]
        f["fees"]["joiningFeeInr"] = value(joining)
        f["fees"]["annualFeeInr"] = value(annual)
        f["fees"]["waiverRule"] = value(waiver)
        f["rewards"] = value(hsbc.get("rewards"))
        f["capsAndExclusions"] = value(hsbc.get("caps"))
        f["lounge"] = value(hsbc.get("lounge"))
        f["forexMarkupPercent"] = value(hsbc.get("forex"))
        f["forexNotes"] = value(hsbc.get("forexNote"))
        f["fuel"] = value(hsbc.get("fuel"))
        f["network"] = value(hsbc.get("network", f["network"]["value"]))
        f["eligibility"] = value(hsbc.get("eligibility"))
        ev[0] = evidence("Official HSBC product page", HSBC_PRODUCT_URLS[name], "Fees, benefits and eligibility sections", ["fees", "rewards/cashback", "lounge", "fuel/forex where stated", "network", "published eligibility"])
    if issuer == "RBL Bank":
        fees = {
            "Icon Credit Card": (5000, 5000, None),
            "World Safari Credit Card": (3000, 3000, None),
            "Platinum Maxima Credit Card": (2000, 2000, None),
            "Platinum Maxima Plus Credit Card": (2500, 2500, None),
            "Shoprite Credit Card": (500, 500, "Renewal fee waived on eligible annual spends of INR 1.5 lakh or more."),
            "Cookies Credit Card": (None, None, "Schedule distinguishes issue date: INR 500 annual fee if issued before 10 May 2021; INR 100 monthly fee, waived on eligible previous-month spends of INR 5,000 or more, if issued after 10 May 2021."),
        }
        if name in fees:
            joining, annual, waiver = fees[name]
            f["fees"]["joiningFeeInr"] = value(joining)
            f["fees"]["annualFeeInr"] = value(annual)
            f["fees"]["waiverRule"] = value(waiver)
            ev.append(evidence("RBL Bank Schedule of Charges", TERMS[issuer][1], "Membership Fee Details, pages 1-2", ["joining/first-year fee", "renewal fee", "fee waiver"], [x for x in [f"First-year fee: INR {joining}" if joining is not None else None, f"Second-year fee: INR {annual}" if annual is not None else None, waiver] if x]))
    if issuer == "Standard Chartered India":
        url = SC_TERMS.get(name)
        if url:
            ev.append(evidence("Official product terms", url, "Product-specific terms", ["fees", "rewards/cashback", "caps/exclusions", "lounge/fuel where stated"]))
        if name == "Rewards Credit Card":
            f["fees"]["joiningFeeInr"] = value(0)
            f["fees"]["waiverRule"] = value("Renewal fee and waiver threshold are referenced but amounts are deferred to the Important Information/Most Important Document.")
            f["rewards"] = value({"earn": ["4 base reward points per INR 150 on retail, except insurance/government payments", "1 base reward point per INR 150 on insurance and government payments", "4 bonus reward points per INR 150 on eligible retail spend above INR 20,000 per statement cycle"], "redemption": ["1 RP = INR 0.25 for catalogue products/vouchers/services", "1 RP = INR 0.20 against card statement balance"]})
            f["capsAndExclusions"] = value(["Bonus rewards capped at 2,000 points per statement cycle", "No rewards on fuel, returned/disputed/unauthorised/charged-back transactions, finance charges/fees, or cash advances", "Statement redemption requires at least 1,000 RP and multiples of 100"])
            f["lounge"] = value({"domestic": "1 complimentary visit per calendar quarter for eligible primary and supplementary Rewards cardholders", "spendGate": None})
            f["fuel"] = value("1% surcharge reversal for INR 400-INR 2,000 fuel transactions; capped at INR 400 per statement cycle")
        elif name == "Standard Chartered EaseMyTrip Credit Card":
            f["rewards"] = value({"earn": ["10 RP per INR 100 on standalone airline/hotel merchants", "2 RP per INR 100 on other eligible retail spend, including EaseMyTrip bookings"], "rewardCap": "No monthly cap stated in product terms"})
            f["capsAndExclusions"] = value(["Returned/disputed/unauthorised transactions, finance charges, account fees, cash withdrawals and charged-back transactions excluded", "EaseMyTrip discounts limited to once per month per card in each listed booking category", "Reward points expire after 2 years"])
            f["lounge"] = value({"domestic": "2 complimentary domestic visits per calendar year from 15 October 2024", "international": "Product terms say international Priority Pass access became chargeable from 15 October 2024", "spendGate": None})
        elif name == "Smart Credit Card":
            f["rewards"] = value({"cashback": ["2% on online spend", "1% on other eligible spend"]})
            f["capsAndExclusions"] = value(["Online cashback capped at INR 1,000 per statement cycle", "Offline cashback capped at INR 500 per statement cycle", "Caps apply at client level across primary and supplementary cards from 21 August 2024", "Fuel, specified ineligible Billdesk/StanChart Bill Pay billers, returned/disputed/unauthorised/charged-back transactions, finance charges/fees and cash advances excluded", "Minimum cashback redemption INR 2,500 from 1 May 2024; increments of INR 1,000"])
        elif name == "Ultimate Credit Card":
            f["fees"]["joiningFeeInr"] = value(5000)
            f["rewards"] = value({"earn": ["5 RP per INR 150 on eligible categories", "3 RP per INR 150 on utilities, supermarkets, insurance, property management, schools and government payments"], "redemption": "1 RP = INR 1 on the R360 catalogue"})
            f["capsAndExclusions"] = value(["No rewards on fuel, returned/disputed/unauthorised/charged-back transactions, finance charges/fees or ATM transactions", "Duty-free cashback capped at INR 1,000 per statement cycle"])
            f["lounge"] = value({"domestic": "4 complimentary domestic lounge visits per calendar quarter on eligible Visa/Mastercard variants", "priorityPass": "1 complimentary visit per month subject to the product-terms conditions; other visits chargeable", "spendGate": "Product terms reference meeting stated conditions; no numeric spend threshold extracted"})
            f["fuel"] = value("1% fuel surcharge waiver, capped at INR 1,000 per statement cycle; fuel earns no rewards")


def main():
    catalogue = json.loads((ROOT / "CARD_CATALOGUE_2026-07-18.json").read_text())
    profile_doc = json.loads((ROOT / "CARD_PROFILES_2026-07-18.json").read_text())
    id_map = {(p["identity"]["issuer"], p["identity"]["name"]): p["id"] for p in profile_doc["profiles"]}
    cards = [c for c in catalogue["cards"] if c["issuer"] in TARGETS]
    names_by_issuer = {issuer: [c["card_name"] for c in cards if c["issuer"] == issuer] for issuer in TARGETS}
    source_text = {}
    for issuer, idx in CATALOG_INDEX.items():
        path = Path(f"/tmp/cardwise_official/{idx:03}.txt")
        source_text[issuer] = clean(path.read_text(errors="ignore")) if path.exists() else ""

    output = []
    for card in cards:
        issuer, name = card["issuer"], card["card_name"]
        block = product_block(source_text.get(issuer, ""), name, names_by_issuer[issuer])
        # These catalogue layouts interleave unrelated cards/navigation. Suppress
        # auto-extraction where a clean per-product block was not observed; curated
        # official product terms are applied below where available.
        suppress_auto = issuer in {"HSBC India", "RBL Bank", "Standard Chartered India"} or (
            issuer == "Kotak Mahindra Bank" and name in {"Kotak Air Credit Card", "White Credit Card", "IndiGo Kotak Premium Credit Card"}
        )
        if suppress_auto:
            block = []
        statements = supported_statements(block)
        text = "\n".join(block)
        joining = parse_money(r"Joining Fees?\s*:\s*(?:INR|₹)?\s*([\d,.]+|Nil)", text)
        annual = parse_money(r"Annual Fee\s*:\s*(?:INR|₹)?\s*([\d,.]+|Nil)", text)
        reward_lines = [s for s in statements if any(k in s.casefold() for k in ("reward", "cashback", "air mile", "avios", "smile"))]
        cap_lines = [s for s in statements if any(k in s.casefold() for k in ("cap", "eligible", "spend", "upto", "up to", "waiv"))]
        lounge_lines = [s for s in statements if "lounge" in s.casefold()]
        fuel_lines = [s for s in statements if "fuel" in s.casefold()]
        forex_lines = [s for s in statements if "forex" in s.casefold() or "foreign currency" in s.casefold()]
        eligibility_lines = [s for s in statements if any(k in s.casefold() for k in ("eligibility", "eligible", "invite-only", "government sector", "priority bank"))]
        forex_pct = parse_percentage(" ".join(forex_lines), "(?:forex|foreign currency)(?: mark-?up)?") if forex_lines else None
        facts = {
            "fees": {
                "joiningFeeInr": value(joining),
                "annualFeeInr": value(annual),
                "waiverRule": value(next((s for s in cap_lines if "annual fee" in s.casefold() and "waiv" in s.casefold()), None)),
                "gstIncluded": value(None),
            },
            "rewards": value(reward_lines or None),
            "capsAndExclusions": value(cap_lines or None),
            "lounge": value({"statements": lounge_lines, "spendGate": next((s for s in lounge_lines if "spend" in s.casefold()), None)} if lounge_lines else None),
            "forexMarkupPercent": value(forex_pct),
            "forexNotes": value(forex_lines or None),
            "fuel": value(fuel_lines or None),
            "network": value(card["network"], "official_catalogue"),
            "secured": value(card["secured"], "official_catalogue"),
            "cobranded": value(card["cobranded"], "official_catalogue"),
            "eligibility": value(eligibility_lines or None),
        }
        sources = [evidence("Official issuer/product surface", card["official_url"], "Product listing or product page", ["product identity", "catalogue presence"] + (["displayed fees/rewards/benefits"] if statements else []), statements or None, "blocked_by_cloudflare" if issuer == "AU Small Finance Bank" else "accessible")]
        if card["catalog_url"] != card["official_url"]:
            sources.append(evidence("Official issuer catalogue", card["catalog_url"], "Credit-card catalogue", ["catalogue presence"], access="blocked_by_cloudflare" if issuer == "AU Small Finance Bank" else "accessible"))
        profile = {
            "id": id_map.get((issuer, name)),
            "issuer": issuer,
            "cardName": name,
            "checkedAt": CHECKED,
            "catalogueStatus": card["status"],
            "facts": facts,
            "sources": sources,
            "researchStatus": "official_terms_enriched" if statements else "catalogue_only_unknown_terms",
        }
        apply_special(profile)
        economic_values = [
            profile["facts"]["fees"]["joiningFeeInr"]["value"],
            profile["facts"]["fees"]["annualFeeInr"]["value"],
            profile["facts"]["rewards"]["value"],
            profile["facts"]["lounge"]["value"],
            profile["facts"]["forexMarkupPercent"]["value"],
            profile["facts"]["fuel"]["value"],
            profile["facts"]["eligibility"]["value"],
        ]
        profile["researchStatus"] = "official_terms_enriched" if any(x is not None for x in economic_values) else "catalogue_only_unknown_terms"
        output.append(profile)

    metadata = {
        "title": "CardWise target-issuer official-source enrichment",
        "jurisdiction": "India",
        "checkedAt": CHECKED,
        "issuerCount": len(TARGETS),
        "profileCount": len(output),
        "issuers": sorted(TARGETS),
        "unknownPolicy": "Every unsupported field is explicit null with status=unknown. No terms are inferred from card names, editorial categories, or third-party aggregators.",
        "sourcePolicy": "Official issuer catalogues, product pages, schedules, MITC/KFS and product terms only.",
        "accessNotes": "AU Bank pages returned Cloudflare verification/HTTP 403 during this check, so AU product economics remain null except catalogue facts already captured. Other issuer catalogue surfaces and listed official terms were accessible.",
    }
    doc = {"metadata": metadata, "issuerTermsSources": TERMS, "profiles": output}
    out = ROOT / "CARD_ENRICHMENT_TARGET_ISSUERS_2026-07-18.json"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {out} with {len(output)} profiles")


if __name__ == "__main__":
    main()
