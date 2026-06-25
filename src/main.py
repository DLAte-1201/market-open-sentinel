from __future__ import annotations

import os
from collections.abc import Iterable

from .fetch_fred import fetch_fred_indicator
from .fetch_yfinance import fetch_yfinance_indicator
from .indicators import IndicatorDefinition, IndicatorResult, load_watchlist
from .notify import send_discord_message
from .report import build_report
from .rules import add_status, determine_market_state


def main() -> None:
    _load_dotenv_if_available()

    indicators = load_watchlist()
    results = fetch_all(indicators)
    results["yield_spread_10y2y"] = build_yield_spread_result(results)

    market_state = determine_market_state(results)
    message = build_report(results, market_state)

    _print_collection_warnings(results.values())
    send_discord_message(message, os.getenv("DISCORD_WEBHOOK_URL"))


def fetch_all(indicators: Iterable[IndicatorDefinition]) -> dict[str, IndicatorResult]:
    fred_api_key = os.getenv("FRED_API_KEY")
    results: dict[str, IndicatorResult] = {}

    for indicator in indicators:
        if indicator.source == "yfinance":
            result = fetch_yfinance_indicator(indicator)
        elif indicator.source == "fred":
            result = fetch_fred_indicator(indicator, fred_api_key)
        else:
            result = IndicatorResult.unavailable(
                indicator,
                f"unsupported data source: {indicator.source}",
            )
        results[indicator.key] = add_status(result)

    return results


def build_yield_spread_result(results: dict[str, IndicatorResult]) -> IndicatorResult:
    spread_definition = IndicatorDefinition(
        key="yield_spread_10y2y",
        name="10Y-2Y 스프레드",
        source="derived",
        category="rate_spread",
        section="rates_fx",
        unit="bp",
        change_type="bp",
        decimals=0,
        thresholds={"up": 5.0, "down": -5.0},
    )

    ten_year = results.get("us10y")
    two_year = results.get("us2y")
    if (
        ten_year is None
        or two_year is None
        or ten_year.value is None
        or two_year.value is None
        or ten_year.previous_value is None
        or two_year.previous_value is None
    ):
        return add_status(IndicatorResult.unavailable(spread_definition, "rate data is unavailable"))

    current_spread_bp = (ten_year.value - two_year.value) * 100
    previous_spread_bp = (ten_year.previous_value - two_year.previous_value) * 100
    spread_change_bp = current_spread_bp - previous_spread_bp

    return add_status(
        IndicatorResult.from_values(
            indicator=spread_definition,
            value=current_spread_bp,
            previous_value=previous_spread_bp,
            change=spread_change_bp,
        )
    )


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _print_collection_warnings(results: Iterable[IndicatorResult]) -> None:
    for result in results:
        if result.error:
            print(f"[WARN] {result.name}: {result.error}")


if __name__ == "__main__":
    main()
