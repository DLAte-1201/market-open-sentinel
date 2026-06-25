from __future__ import annotations

from collections.abc import Mapping

from .indicators import IndicatorResult


ASSET_CATEGORIES = {"risk_asset", "metal"}
DOLLAR_CATEGORIES = {"currency", "dollar"}
RATE_CATEGORIES = {"rate", "rate_spread"}


def get_status_emoji(
    category: str,
    change: float | None,
    thresholds: Mapping[str, float] | None = None,
) -> str:
    if change is None:
        return "⚪"

    up, down = _thresholds_for(category, thresholds or {})
    if change >= up:
        if category == "oil":
            return "🟠"
        if category in RATE_CATEGORIES or category in DOLLAR_CATEGORIES:
            return "🟡"
        return "🟢"
    if change <= down:
        if category == "oil":
            return "🔵"
        if category in RATE_CATEGORIES or category in DOLLAR_CATEGORIES:
            return "🔵"
        return "🔴"
    return "⚪"


def add_status(result: IndicatorResult) -> IndicatorResult:
    return result.with_status(
        get_status_emoji(
            category=result.category,
            change=result.change,
            thresholds=result.thresholds,
        )
    )


def determine_market_state(results: Mapping[str, IndicatorResult]) -> str:
    if _inflation_pressure(results):
        return "인플레이션 압력"
    if _risk_on(results):
        return "리스크온"
    if _risk_off(results):
        return "리스크오프"
    return "혼조"


def _thresholds_for(category: str, thresholds: Mapping[str, float]) -> tuple[float, float]:
    if category == "oil":
        return float(thresholds.get("up", 2.0)), float(thresholds.get("down", -2.0))
    if category in RATE_CATEGORIES:
        return float(thresholds.get("up", 5.0)), float(thresholds.get("down", -5.0))
    if category in DOLLAR_CATEGORIES:
        return float(thresholds.get("up", 0.5)), float(thresholds.get("down", -0.5))
    if category in ASSET_CATEGORIES:
        return float(thresholds.get("up", 1.0)), float(thresholds.get("down", -1.0))
    return float(thresholds.get("up", 1.0)), float(thresholds.get("down", -1.0))


def _change(results: Mapping[str, IndicatorResult], key: str) -> float | None:
    result = results.get(key)
    if result is None:
        return None
    return result.change


def _any_positive(results: Mapping[str, IndicatorResult], keys: tuple[str, ...]) -> bool:
    return any((change := _change(results, key)) is not None and change > 0 for key in keys)


def _any_negative(results: Mapping[str, IndicatorResult], keys: tuple[str, ...]) -> bool:
    return any((change := _change(results, key)) is not None and change < 0 for key in keys)


def _known_all_negative(results: Mapping[str, IndicatorResult], keys: tuple[str, ...]) -> bool:
    known_changes = [_change(results, key) for key in keys if _change(results, key) is not None]
    return bool(known_changes) and all(change < 0 for change in known_changes)


def _risk_on(results: Mapping[str, IndicatorResult]) -> bool:
    equity_up = _any_positive(results, ("nasdaq100_futures", "nasdaq"))
    crypto_up = _any_positive(results, ("btc", "eth"))
    ten_year_change = _change(results, "us10y")
    dollar_change = _change(results, "dxy")
    ten_year_not_spiking = ten_year_change is None or ten_year_change < 5
    dollar_not_strong = dollar_change is None or dollar_change < 0.5
    return equity_up and crypto_up and ten_year_not_spiking and dollar_not_strong


def _risk_off(results: Mapping[str, IndicatorResult]) -> bool:
    equity_down = _any_negative(results, ("nasdaq100_futures", "nasdaq"))
    crypto_down = _known_all_negative(results, ("btc", "eth"))
    ten_year_change = _change(results, "us10y")
    dollar_change = _change(results, "dxy")
    rate_or_dollar_up = (
        (ten_year_change is not None and ten_year_change > 0)
        or (dollar_change is not None and dollar_change > 0)
    )
    return equity_down and crypto_down and rate_or_dollar_up


def _inflation_pressure(results: Mapping[str, IndicatorResult]) -> bool:
    wti_change = _change(results, "wti")
    brent_change = _change(results, "brent")
    ten_year_change = _change(results, "us10y")
    return (
        wti_change is not None
        and brent_change is not None
        and ten_year_change is not None
        and wti_change >= 2
        and brent_change >= 2
        and ten_year_change >= 5
    )
