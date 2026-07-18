#!/usr/bin/env python3
"""Deterministic integrity checks for CardWise catalogue/profile snapshots."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT / "CARD_CATALOGUE_2026-07-18.json"
PROFILES = ROOT / "CARD_PROFILES_2026-07-18.json"


def slug(value: str) -> str:
    value = value.lower().replace("+", "-plus")
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value))


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    catalogue_doc = json.loads(CATALOGUE.read_text())
    profile_doc = json.loads(PROFILES.read_text())
    cards = catalogue_doc["cards"]
    profiles = profile_doc["profiles"]

    expected_ids = {slug(f"{c['issuer']} {c['card_name']}") for c in cards}
    profile_ids = [p["id"] for p in profiles]
    if len(expected_ids) != len(cards):
        fail("catalogue canonical-ID collision")
    if len(set(profile_ids)) != len(profile_ids):
        fail("duplicate profile ID")
    if set(profile_ids) != expected_ids:
        missing = sorted(expected_ids - set(profile_ids))
        extra = sorted(set(profile_ids) - expected_ids)
        fail(f"profile/catalogue ID mismatch; missing={missing[:3]} extra={extra[:3]}")

    card_by_id = {slug(f"{c['issuer']} {c['card_name']}"): c for c in cards}
    required_term_groups = {"cost", "rewards", "benefits", "eligibility", "availability"}
    required_profile_keys = {
        "identity", "overview", "knownFacts", "learningGuide",
        "missingMaterialFacts", "contractualTerms", "evidence", "profileCompleteness"
    }

    evidence_links = 0
    questions = 0
    known_fees = 0
    card_enriched = 0
    provider_context = 0
    for profile in profiles:
        pid = profile["id"]
        card = card_by_id[pid]
        missing_keys = required_profile_keys - set(profile)
        if missing_keys:
            fail(f"{pid}: missing profile keys {sorted(missing_keys)}")
        if set(profile["contractualTerms"]) != required_term_groups:
            fail(f"{pid}: contractual term groups differ from schema")
        if profile["identity"]["issuer"] != card["issuer"] or profile["identity"]["name"] != card["card_name"]:
            fail(f"{pid}: identity does not match catalogue")
        profile_fee = profile["knownFacts"]["annualFeeInr"]["value"]
        if card.get("annual_fee_inr") is not None and profile_fee != card.get("annual_fee_inr"):
            fail(f"{pid}: annual fee differs from official catalogue snapshot")
        if profile_fee is not None and profile["knownFacts"]["annualFeeInr"]["status"] not in {"official_catalogue", "supported_on_official_source"}:
            fail(f"{pid}: enriched annual fee lacks supported status")
        if profile["contractualTerms"]["cost"]["annualFeeInr"] != profile_fee:
            fail(f"{pid}: contractual annual fee is inconsistent")
        if profile["contractualTerms"]["eligibility"]["minimumIncomeInr"] is not None:
            fail(f"{pid}: unsupported minimum income populated")
        score = profile["profileCompleteness"]["score"]
        if not isinstance(score, int) or not 0 <= score <= 100:
            fail(f"{pid}: invalid completeness score")
        if len(profile["learningGuide"]["questionsBeforeApplying"]) < 6:
            fail(f"{pid}: insufficient learning questions")
        for item in profile["evidence"]:
            evidence_links += 1
            if not item["url"].startswith("https://"):
                fail(f"{pid}: non-HTTPS evidence URL")
        if "officialResearch" in profile:
            card_enriched += 1
            if profile["officialResearch"].get("supportedGroupCount", 0) < 0:
                fail(f"{pid}: invalid supported-group count")
        if "providerContextId" in profile:
            provider_context += 1
        questions += len(profile["learningGuide"]["questionsBeforeApplying"])
        known_fees += profile_fee is not None

    expected_count = catalogue_doc["metadata"]["row_count"]
    if len(cards) != expected_count or len(profiles) != expected_count:
        fail(f"count mismatch catalogue={len(cards)} profiles={len(profiles)} metadata={expected_count}")
    enrichment = profile_doc["metadata"].get("enrichment", {})
    if card_enriched != enrichment.get("card_level_profile_count") or card_enriched != 230:
        fail(f"card-level enrichment mismatch: {card_enriched}")
    if provider_context != enrichment.get("provider_context_profile_count") or provider_context != 37:
        fail(f"provider-context enrichment mismatch: {provider_context}")

    print(
        "PASS:",
        f"{len(profiles)} profiles;",
        f"{card_enriched} card-level enrichments;",
        f"{provider_context} provider-context profiles;",
        f"{evidence_links} evidence links;",
        f"{questions} learning questions;",
        f"{known_fees} official fees;",
        "0 ID mismatches; 0 unsupported income values",
    )


if __name__ == "__main__":
    main()
