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
            offers.append({
                "percentage": int(percentage) if percentage.is_integer() else percentage,
                "description": excerpt,
                "sourceUrl": source_url,
                "checkedAt": profile.get("asOf"),
                "evidenceStatus": (
                    "official_source_structured"
                    if source_status == "official_source"
                    else "official_excerpt_requires_product_association_review"
                ),
            })

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
