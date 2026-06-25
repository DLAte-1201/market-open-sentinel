from __future__ import annotations

import math
from typing import Any

from .indicators import IndicatorDefinition, IndicatorResult


def fetch_yfinance_indicator(indicator: IndicatorDefinition) -> IndicatorResult:
    if not indicator.ticker:
        return IndicatorResult.unavailable(indicator, "yfinance ticker is missing")

    try:
        import yfinance as yf

        ticker = yf.Ticker(indicator.ticker)
        current_value = _get_current_value(ticker)
        previous_close = _get_previous_close(ticker)

        if current_value is None:
            return IndicatorResult.unavailable(indicator, "current value is unavailable")
        if previous_close is None:
            return IndicatorResult.unavailable(indicator, "previous close is unavailable")
        if previous_close == 0:
            return IndicatorResult.unavailable(indicator, "previous close is zero")

        change_percent = ((current_value - previous_close) / previous_close) * 100
        return IndicatorResult.from_values(
            indicator=indicator,
            value=current_value,
            previous_value=previous_close,
            change=change_percent,
        )
    except Exception as exc:  # noqa: BLE001 - 개별 지표 실패가 전체 실행을 막지 않게 처리
        return IndicatorResult.unavailable(indicator, str(exc))


def _get_current_value(ticker: Any) -> float | None:
    fast_value = _read_fast_info(ticker, ("last_price", "regular_market_price"))
    if fast_value is not None:
        return fast_value

    intraday_close = _last_history_close(ticker, period="1d", interval="1m")
    if intraday_close is not None:
        return intraday_close

    return _last_history_close(ticker, period="5d", interval="1d")


def _get_previous_close(ticker: Any) -> float | None:
    fast_value = _read_fast_info(ticker, ("previous_close", "regular_market_previous_close"))
    if fast_value is not None:
        return fast_value

    closes = _history_closes(ticker, period="10d", interval="1d")
    if len(closes) >= 2:
        return closes[-2]
    return None


def _read_fast_info(ticker: Any, keys: tuple[str, ...]) -> float | None:
    try:
        fast_info = ticker.fast_info
    except Exception:
        return None

    for key in keys:
        try:
            if hasattr(fast_info, "get"):
                value = fast_info.get(key)
            else:
                value = getattr(fast_info, key)
        except Exception:
            value = None
        parsed = _safe_float(value)
        if parsed is not None:
            return parsed
    return None


def _last_history_close(ticker: Any, period: str, interval: str) -> float | None:
    closes = _history_closes(ticker, period=period, interval=interval)
    if not closes:
        return None
    return closes[-1]


def _history_closes(ticker: Any, period: str, interval: str) -> list[float]:
    try:
        history = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=False,
            prepost=True,
        )
    except Exception:
        return []

    if history is None or history.empty or "Close" not in history:
        return []

    closes: list[float] = []
    for value in history["Close"].dropna().tolist():
        parsed = _safe_float(value)
        if parsed is not None:
            closes.append(parsed)
    return closes


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed
