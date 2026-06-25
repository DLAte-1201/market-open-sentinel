import unittest

from src.indicators import IndicatorResult
from src.rules import determine_market_state, get_status_emoji


def make_result(
    key: str,
    change: float | None,
    category: str = "risk_asset",
    change_type: str = "percent",
) -> IndicatorResult:
    return IndicatorResult(
        key=key,
        name=key,
        source="test",
        category=category,
        section="test",
        unit="%",
        change_type=change_type,
        value=100.0,
        previous_value=100.0,
        change=change,
    )


class RulesTest(unittest.TestCase):
    def test_rate_up_5bp_or_more_is_yellow(self):
        self.assertEqual(get_status_emoji("rate", 5.0), "🟡")

    def test_equity_down_1_percent_or_more_is_red(self):
        self.assertEqual(get_status_emoji("risk_asset", -1.0), "🔴")

    def test_oil_up_2_percent_or_more_is_orange(self):
        self.assertEqual(get_status_emoji("oil", 2.0), "🟠")

    def test_risk_on_classification_works(self):
        results = {
            "nasdaq100_futures": make_result("nasdaq100_futures", 0.4),
            "nasdaq": make_result("nasdaq", 0.2),
            "btc": make_result("btc", 0.8),
            "eth": make_result("eth", 0.1),
            "us10y": make_result("us10y", 2.0, category="rate", change_type="bp"),
            "dxy": make_result("dxy", 0.1, category="dollar"),
        }

        self.assertEqual(determine_market_state(results), "리스크온")

    def test_risk_off_classification_works(self):
        results = {
            "nasdaq100_futures": make_result("nasdaq100_futures", -0.4),
            "nasdaq": make_result("nasdaq", -0.2),
            "btc": make_result("btc", -0.8),
            "eth": make_result("eth", -0.1),
            "us10y": make_result("us10y", 3.0, category="rate", change_type="bp"),
            "dxy": make_result("dxy", 0.2, category="dollar"),
        }

        self.assertEqual(determine_market_state(results), "리스크오프")


if __name__ == "__main__":
    unittest.main()
