#!/usr/bin/env python3
"""Extract conservative cashback percentages from CardWise official-source research.

Only explicit percentage/cashback relationships are published. Missing evidence is
represented as unverified, never as a zero-percent offer.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_JSON = ROOT / "CARD_PROFILES_2026-07-18.json"
PROFILE_JS = ROOT / "card-profile-data.js"

PERCENT_BEFORE = re.compile(
    r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*%\s*[^\d%]{0,24}?cashback", re.I
)
PERCENT_AFTER = re.compile(
    r"cashback[^\d%]{0,24}?(\d{1,3}(?:\.\d+)?)\s*%", re.I
)
ANY_PERCENT = re.compile(r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*%", re.I)
MODELED_CARDS = {
    "CASHBACK SBI Card",
    "Amazon Pay ICICI Bank Credit Card",
    "HSBC Live+ Credit Card",
    "Axis Bank Atlas Credit Card",
    "Regalia Gold Credit Card",
    "Tata Neu Plus HDFC Bank Credit Card",
    "FIRST WOW! Credit Card",
}

CATEGORY_KEYWORDS = {
    "amazon": "Amazon", "flipkart": "Flipkart", "myntra": "Myntra",
    "swiggy": "Swiggy", "zomato": "Zomato", "grocery": "Groceries",
    "groceries": "Groceries", "dining": "Dining", "food delivery": "Food delivery",
    "fuel": "Fuel", "utility": "Utilities", "utilities": "Utilities",
    "upi": "UPI", "travel": "Travel", "movie": "Movies", "pvr": "PVR",
    "samsung": "Samsung", "airtel": "Airtel", "hpcl": "HPCL",
    "online": "Online spending", "offline": "Offline spending",
}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)


def excerpt_around(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind(";", 0, start), text.rfind("|", 0, start)) + 1
    endings = [p for p in (text.find(".", end), text.find(";", end), text.find("|", end)) if p >= 0]
    right = min(endings) + 1 if endings else min(len(text), end + 220)
    return clean(text[left:right])[:520]


def source_fallback(profile) -> str:
    preferred = profile["identity"].get("officialUrl")
    if preferred and preferred.startswith("https://"):
        return preferred
    for evidence in profile.get("evidence", []):
        if evidence.get("url", "").startswith("https://"):
            return evidence["url"]
    return ""


def condition_fields(description: str):
    lower = description.lower()
    categories = []
    for needle, label in CATEGORY_KEYWORDS.items():
        if needle in lower and label not in categories:
            categories.append(label)
    channels = []
    if "online" in lower:
        channels.append("online")
    if "offline" in lower or "pos" in lower or "swiped" in lower:
        channels.append("offline_or_pos")
    if "upi" in lower:
        channels.append("upi")
    if " app" in lower or "application" in lower:
        channels.append("issuer_or_partner_app")
    cap_text = description if re.search(r"\b(cap|capped|maximum|max\.?\s|up to\s+(?:₹|inr))", lower) else None
    minimum_text = description if re.search(r"\b(minimum|min\.?\s+transaction|spends?\s*(?:>|above|of))", lower) else None
    exclusions_text = description if re.search(r"\b(except|exclude|excluded|not applicable|ineligible)", lower) else None
    if re.search(r"\b(first|joining|activation|welcome)\b", lower):
        offer_type = "welcome_or_activation_offer"
    elif re.search(r"\b(valid (?:till|until)|offer period|limited time|campaign)\b", lower):
        offer_type = "time_limited_or_undated_promotion"
    else:
        offer_type = "ongoing_card_benefit"
    validity_match = re.search(
        r"(?:within\s+(?:the\s+)?first\s+\d+\s+days?|valid\s+(?:till|until)\s+[^,.;]+)",
        description,
        re.I,
    )
    return {
        "merchantOrCategory": categories,
        "channels": channels,
        "capText": cap_text,
        "minimumSpendText": minimum_text,
        "exclusionsText": exclusions_text,
        "offerType": offer_type,
        "validityText": validity_match.group(0) if validity_match else None,
    }


def supported(value, status="supported_on_official_source"):
    return {"value": value, "status": status if value is not None else "not_verified"}


def decision_details(profile):
    terms = profile["contractualTerms"]
    cost = terms["cost"]
    annual_fee = cost.get("annualFeeInr")
    if annual_fee is None:
        annual_fee = profile["knownFacts"]["annualFeeInr"].get("value")
    cashback = profile["cashbackOffers"]
    has_reward_research = bool(profile.get("officialResearch", {}).get("groups", {}).get("reward_rates") or terms["rewards"].get("baseEarnRule"))
    if cashback["offers"]:
        conversion_status = "direct_cashback_no_conversion_needed"
    elif has_reward_research or "Rewards" in profile.get("discoveryCategories", []):
        conversion_status = "not_calculated_missing_official_redemption_value"
    else:
        conversion_status = "not_available"
    modeled = profile["identity"]["name"] in MODELED_CARDS
    return {
        "feesAndWaiver": {
            "joiningFeeInr": supported(cost.get("joiningFeeInr")),
            "annualFeeInr": supported(annual_fee),
            "renewalFeeWaiver": supported(cost.get("renewalFeeWaiver")),
            "gstIncluded": supported(None),
        },
        "rewardEconomics": {
            "directCashbackAvailable": bool(cashback["offers"]),
            "rewardPointsPerSpendUnit": supported(None),
            "officialPointValueInr": supported(None),
            "calculatedEquivalentPercent": supported(None),
            "conversionStatus": conversion_status,
        },
        "annualValue": {
            "yearOne": {
                "value": None,
                "status": "not_separately_modeled",
                "reason": "Welcome-benefit cash value is not normalized; it is not invented.",
            },
            "ongoing": {
                "value": None,
                "status": "personalized_browser_model_available" if modeled else "not_modeled",
                "reason": "Calculated from the user's browser spending inputs." if modeled else "Reward economics are not normalized for personalized calculation.",
            },
        },
    }


def research_texts(profile):
    fallback = source_fallback(profile)
    research = profile.get("officialResearch", {})

    def walk(node, path=()):
        if isinstance(node, dict):
            status = str(node.get("status", ""))
            evidence = node.get("evidence")
            if isinstance(evidence, list):
                for item in evidence:
                    text = item.get("excerpt")
                    if text:
                        yield clean(text), item.get("sourceUrl") or fallback, status, path
            if "value" in node and status and "unknown" not in status:
                for text in strings(node["value"]):
                    yield clean(text), fallback, status, path + ("value",)
            if "normalized" in node and status and "unknown" not in status:
                for text in strings(node["normalized"]):
                    yield clean(text), fallback, status, path + ("normalized",)
            for key, value in node.items():
                if key not in {"evidence", "value", "normalized"}:
                    yield from walk(value, path + (key,))
        elif isinstance(node, list):
            for value in node:
                yield from walk(value, path)

    yield from walk(research.get("groups", {}))


def extract_profile(profile):
    offers = []
    for text, source_url, source_status, path in research_texts(profile):
        if not text:
            continue
        cashback_path = any("cashback" in str(part).lower() for part in path)
        matches = []
        if cashback_path:
            matches.extend(ANY_PERCENT.finditer(text))
        else:
            matches.extend(PERCENT_BEFORE.finditer(text))
            matches.extend(PERCENT_AFTER.finditer(text))

        for match in matches:
            percentage = float(match.group(1))
            if not 0 < percentage <= 100:
                continue
            local = text[max(0, match.start() - 35): min(len(text), match.end() + 45)].lower()
            # A surcharge percentage next to a cashback heading/cap is not a cashback rate.
            after_percentage = text[match.end(): min(len(text), match.end() + 45)].lower()
            if "surcharge" in after_percentage:
                continue
            if "surcharge" in local and "cashback" not in match.group(0).lower():
                continue
            excerpt = text if cashback_path and len(text) <= 520 else excerpt_around(text, match.start(), match.end())
            if "cashback" not in excerpt.lower() and not cashback_path:
                continue
            offer = {
                "percentage": int(percentage) if percentage.is_integer() else percentage,
                "description": excerpt,
                "sourceUrl": source_url,
                "checkedAt": profile.get("asOf"),
                "evidenceStatus": (
                    "official_source_structured"
                    if source_status == "official_source"
                    else "official_excerpt_requires_product_association_review"
                ),
            }
            offer.update(condition_fields(excerpt))
            offers.append(offer)

    unique = []
    seen = set()
    for offer in offers:
        normalized = re.sub(r"\W+", "", offer["description"].lower())[:220]
        key = (offer["percentage"], normalized, offer["sourceUrl"])
        if key not in seen:
            seen.add(key)
            unique.append(offer)

    unique.sort(key=lambda item: (-float(item["percentage"]), item["description"].lower()))
    unique = unique[:12]
    return {
        "status": "official_percentage_evidence_found" if unique else "no_cashback_percentage_verified",
        "highestPercentage": max((float(item["percentage"]) for item in unique), default=None),
        "offers": unique,
        "meaning": (
            "Percentages are transcribed from reviewed official-source research. Caps, merchants, channels, dates and exclusions in each description still control."
            if unique
            else "No explicit card-level cashback percentage was verified in the reviewed official sources; this does not prove the card has no cashback benefit."
        ),
    }


def main():
    document = json.loads(PROFILE_JSON.read_text())
    profiles = document["profiles"]
    for profile in profiles:
        profile["cashbackOffers"] = extract_profile(profile)
        profile["decisionDetails"] = decision_details(profile)

    with_offers = [p for p in profiles if p["cashbackOffers"]["offers"]]
    offer_count = sum(len(p["cashbackOffers"]["offers"]) for p in profiles)
    document["metadata"]["cashback_offer_coverage"] = {
        "profiles_total": len(profiles),
        "profiles_with_explicit_percentage_evidence": len(with_offers),
        "offers_extracted": offer_count,
        "policy": "No explicit official evidence means unverified, not zero percent. Candidate excerpts do not become executable reward rules without human review.",
    }
    PROFILE_JSON.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    PROFILE_JS.write_text(
        "/* Generated educational profiles. Unknown facts are explicit; see JSON for methodology. */\n"
        + "window.cardProfiles="
        + json.dumps({p["id"]: p for p in profiles}, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    print(f"PASS: {len(profiles)} profiles; {len(with_offers)} with explicit cashback percentages; {offer_count} extracted offer records")


if __name__ == "__main__":
    main()
