from __future__ import annotations

import math
import os
from typing import Any

from .indicators import IndicatorDefinition, IndicatorResult


FRED_OBSERVATIONS_URL = "https://api.stlouisfed.org/fred/series/observations"


def fetch_fred_indicator(
    indicator: IndicatorDefinition,
    api_key: str | None = None,
) -> IndicatorResult:
    if not indicator.series_id:
        return IndicatorResult.unavailable(indicator, "FRED series_id is missing")

    key = api_key or os.getenv("FRED_API_KEY")
    if not key:
        return IndicatorResult.unavailable(indicator, "FRED_API_KEY is missing")

    try:
        observations = _fetch_observations(indicator.series_id, key)
        values = _latest_two_numeric_values(observations)
        if len(values) < 2:
            return IndicatorResult.unavailable(indicator, "not enough FRED observations")

        current_value = values[0]
        previous_value = values[1]
        change_bp = (current_value - previous_value) * 100

        return IndicatorResult.from_values(
            indicator=indicator,
            value=current_value,
            previous_value=previous_value,
            change=change_bp,
        )
    except Exception as exc:  # noqa: BLE001 - 개별 지표 실패가 전체 실행을 막지 않게 처리
        return IndicatorResult.unavailable(indicator, str(exc))


def _fetch_observations(series_id: str, api_key: str) -> list[dict[str, Any]]:
    import requests

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 20,
    }
    response = requests.get(FRED_OBSERVATIONS_URL, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()
    observations = payload.get("observations", [])
    if not isinstance(observations, list):
        return []
    return observations


def _latest_two_numeric_values(observations: list[dict[str, Any]]) -> list[float]:
    values: list[float] = []
    for observation in observations:
        value = _safe_float(observation.get("value"))
        if value is not None:
            values.append(value)
        if len(values) == 2:
            break
    return values


def _safe_float(value: Any) -> float | None:
    if value is None or value == ".":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed
