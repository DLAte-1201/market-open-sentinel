from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WATCHLIST_PATH = PROJECT_ROOT / "config" / "watchlist.yaml"


@dataclass(frozen=True)
class IndicatorDefinition:
    key: str
    name: str
    source: str
    category: str
    section: str
    unit: str
    change_type: str
    ticker: str | None = None
    series_id: str | None = None
    decimals: int = 2
    thresholds: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class IndicatorResult:
    key: str
    name: str
    source: str
    category: str
    section: str
    unit: str
    change_type: str
    ticker: str | None = None
    series_id: str | None = None
    value: float | None = None
    previous_value: float | None = None
    change: float | None = None
    status_emoji: str = "⚪"
    error: str | None = None
    decimals: int = 2
    thresholds: Mapping[str, float] = field(default_factory=dict)

    @property
    def is_available(self) -> bool:
        return self.value is not None and self.change is not None

    @classmethod
    def from_values(
        cls,
        indicator: IndicatorDefinition,
        value: float,
        previous_value: float,
        change: float,
    ) -> "IndicatorResult":
        return cls(
            key=indicator.key,
            name=indicator.name,
            source=indicator.source,
            category=indicator.category,
            section=indicator.section,
            unit=indicator.unit,
            change_type=indicator.change_type,
            ticker=indicator.ticker,
            series_id=indicator.series_id,
            value=value,
            previous_value=previous_value,
            change=change,
            decimals=indicator.decimals,
            thresholds=dict(indicator.thresholds),
        )

    @classmethod
    def unavailable(
        cls,
        indicator: IndicatorDefinition,
        error: str | None = None,
    ) -> "IndicatorResult":
        return cls(
            key=indicator.key,
            name=indicator.name,
            source=indicator.source,
            category=indicator.category,
            section=indicator.section,
            unit=indicator.unit,
            change_type=indicator.change_type,
            ticker=indicator.ticker,
            series_id=indicator.series_id,
            error=error,
            decimals=indicator.decimals,
            thresholds=dict(indicator.thresholds),
        )

    def with_status(self, status_emoji: str) -> "IndicatorResult":
        return IndicatorResult(
            key=self.key,
            name=self.name,
            source=self.source,
            category=self.category,
            section=self.section,
            unit=self.unit,
            change_type=self.change_type,
            ticker=self.ticker,
            series_id=self.series_id,
            value=self.value,
            previous_value=self.previous_value,
            change=self.change,
            status_emoji=status_emoji,
            error=self.error,
            decimals=self.decimals,
            thresholds=dict(self.thresholds),
        )


# 데이터 제공자 사정에 따라 티커가 바뀔 수 있음.
DEFAULT_INDICATORS: list[IndicatorDefinition] = [
    IndicatorDefinition("btc", "BTC", "yfinance", "risk_asset", "risk_assets", "달러", "percent", ticker="BTC-USD", decimals=0, thresholds={"up": 1.0, "down": -1.0}),
    IndicatorDefinition("eth", "ETH", "yfinance", "risk_asset", "risk_assets", "달러", "percent", ticker="ETH-USD", decimals=2, thresholds={"up": 1.0, "down": -1.0}),
    IndicatorDefinition("gold", "금", "yfinance", "metal", "commodities", "달러", "percent", ticker="GC=F", decimals=2, thresholds={"up": 1.0, "down": -1.0}),
    IndicatorDefinition("silver", "은", "yfinance", "metal", "commodities", "달러", "percent", ticker="SI=F", decimals=2, thresholds={"up": 1.0, "down": -1.0}),
    IndicatorDefinition("nasdaq", "나스닥", "yfinance", "risk_asset", "risk_assets", "포인트", "percent", ticker="^IXIC", decimals=2, thresholds={"up": 1.0, "down": -1.0}),
    IndicatorDefinition("usdkrw", "USD/KRW", "yfinance", "currency", "rates_fx", "원", "percent", ticker="KRW=X", decimals=2, thresholds={"up": 0.5, "down": -0.5}),
    IndicatorDefinition("us10y", "미국 10년물", "fred", "rate", "rates_fx", "%", "bp", series_id="DGS10", decimals=2, thresholds={"up": 5.0, "down": -5.0}),
    IndicatorDefinition("us2y", "미국 2년물", "fred", "rate", "rates_fx", "%", "bp", series_id="DGS2", decimals=2, thresholds={"up": 5.0, "down": -5.0}),
    IndicatorDefinition("nasdaq100_futures", "나스닥100 선물", "yfinance", "risk_asset", "risk_assets", "포인트", "percent", ticker="NQ=F", decimals=2, thresholds={"up": 1.0, "down": -1.0}),
    IndicatorDefinition("dow", "다우", "yfinance", "risk_asset", "risk_assets", "포인트", "percent", ticker="^DJI", decimals=2, thresholds={"up": 1.0, "down": -1.0}),
    IndicatorDefinition("sp500", "S&P 500", "yfinance", "risk_asset", "risk_assets", "포인트", "percent", ticker="^GSPC", decimals=2, thresholds={"up": 1.0, "down": -1.0}),
    IndicatorDefinition("wti", "WTI", "yfinance", "oil", "commodities", "달러", "percent", ticker="CL=F", decimals=2, thresholds={"up": 2.0, "down": -2.0}),
    IndicatorDefinition("brent", "브렌트유", "yfinance", "oil", "commodities", "달러", "percent", ticker="BZ=F", decimals=2, thresholds={"up": 2.0, "down": -2.0}),
    IndicatorDefinition("dxy", "달러 인덱스", "yfinance", "dollar", "rates_fx", "포인트", "percent", ticker="DX-Y.NYB", decimals=2, thresholds={"up": 0.5, "down": -0.5}),
    IndicatorDefinition("sox", "필라델피아 반도체", "yfinance", "risk_asset", "risk_assets", "포인트", "percent", ticker="^SOX", decimals=2, thresholds={"up": 1.0, "down": -1.0}),
]


def load_watchlist(path: Path | None = None) -> list[IndicatorDefinition]:
    watchlist_path = path or DEFAULT_WATCHLIST_PATH
    if not watchlist_path.exists():
        return DEFAULT_INDICATORS

    try:
        import yaml
    except ImportError:
        return DEFAULT_INDICATORS

    with watchlist_path.open("r", encoding="utf-8") as file:
        payload = yaml.safe_load(file) or {}

    rows = payload.get("indicators", [])
    if not isinstance(rows, list) or not rows:
        return DEFAULT_INDICATORS

    return [_definition_from_mapping(row) for row in rows]


def _definition_from_mapping(row: Mapping[str, Any]) -> IndicatorDefinition:
    return IndicatorDefinition(
        key=str(row["key"]),
        name=str(row["name"]),
        source=str(row["source"]),
        category=str(row["category"]),
        section=str(row["section"]),
        unit=str(row["unit"]),
        change_type=str(row["change_type"]),
        ticker=_optional_string(row.get("ticker")),
        series_id=_optional_string(row.get("series_id")),
        decimals=int(row.get("decimals", 2)),
        thresholds=_float_mapping(row.get("thresholds", {})),
    )


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _float_mapping(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): float(item) for key, item in value.items()}
