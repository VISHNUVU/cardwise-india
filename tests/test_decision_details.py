import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "CARD_PROFILES_2026-07-18.json"


class DecisionDetailContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(PROFILES.read_text())
        cls.profiles = cls.document["profiles"]
        cls.by_name = {p["identity"]["name"]: p for p in cls.profiles}

    def test_every_cashback_offer_has_condition_fields(self):
        required = {
            "merchantOrCategory", "channels", "capText", "minimumSpendText",
            "exclusionsText", "offerType", "validityText"
        }
        offers = [o for p in self.profiles for o in p["cashbackOffers"]["offers"]]
        self.assertGreater(offers.__len__(), 0)
        for offer in offers:
            self.assertFalse(required - set(offer), offer)
            self.assertIsInstance(offer["merchantOrCategory"], list)
            self.assertIsInstance(offer["channels"], list)
            self.assertIn(offer["offerType"], {"ongoing_card_benefit", "welcome_or_activation_offer", "time_limited_or_undated_promotion"})

    def test_every_profile_has_unknown_safe_decision_details(self):
        for profile in self.profiles:
            details = profile["decisionDetails"]
            self.assertEqual(set(details), {"feesAndWaiver", "rewardEconomics", "annualValue"})
            self.assertIn("annualFeeInr", details["feesAndWaiver"])
            self.assertIn("renewalFeeWaiver", details["feesAndWaiver"])
            self.assertIn("calculatedEquivalentPercent", details["rewardEconomics"])
            self.assertIn("conversionStatus", details["rewardEconomics"])
            self.assertIn("yearOne", details["annualValue"])
            self.assertIn("ongoing", details["annualValue"])

    def test_supported_hsbc_fee_and_waiver_are_preserved(self):
        details = self.by_name["HSBC Live+ Credit Card"]["decisionDetails"]["feesAndWaiver"]
        self.assertEqual(details["annualFeeInr"]["value"], 999)
        self.assertIn("200,000", details["renewalFeeWaiver"]["value"])

    def test_reward_points_are_not_converted_without_supported_value(self):
        regalia = self.by_name["Regalia Gold Credit Card"]["decisionDetails"]["rewardEconomics"]
        self.assertIsNone(regalia["calculatedEquivalentPercent"]["value"])
        self.assertEqual(regalia["conversionStatus"], "not_calculated_missing_official_redemption_value")

    def test_year_one_is_not_invented_when_welcome_value_is_unknown(self):
        amazon = self.by_name["Amazon Pay ICICI Bank Credit Card"]["decisionDetails"]["annualValue"]
        self.assertIsNone(amazon["yearOne"]["value"])
        self.assertEqual(amazon["yearOne"]["status"], "not_separately_modeled")
        self.assertEqual(amazon["ongoing"]["status"], "personalized_browser_model_available")


if __name__ == "__main__":
    unittest.main()
