from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .indicators import IndicatorResult


KST = ZoneInfo("Asia/Seoul")

SECTION_ORDER = [
    ("risk_assets", "위험자산", ["btc", "eth", "nasdaq", "nasdaq100_futures", "sp500", "dow", "sox"]),
    ("rates_fx", "금리/환율", ["us10y", "us2y", "yield_spread_10y2y", "usdkrw", "dxy"]),
    ("commodities", "원자재", ["wti", "brent", "gold", "silver"]),
]


def build_report(
    results: dict[str, IndicatorResult],
    market_state: str,
    now: datetime | None = None,
) -> str:
    utc_now = now or datetime.now(timezone.utc)
    if utc_now.tzinfo is None:
        utc_now = utc_now.replace(tzinfo=timezone.utc)
    utc_now = utc_now.astimezone(timezone.utc)
    kst_now = utc_now.astimezone(KST)

    lines = [
        "[미국 본장 개장 시장 점검]",
        f"기준 시각: {kst_now:%Y-%m-%d %H:%M} KST / {utc_now:%Y-%m-%d %H:%M} UTC",
        "투자 권유가 아닌 시장 리스크 점검용 알림입니다.",
        "",
    ]

    for index, (_, title, keys) in enumerate(SECTION_ORDER, start=1):
        lines.append(f"{index}. {title}")
        for key in keys:
            result = results.get(key)
            if result is not None:
                lines.append(format_indicator_line(result))
        lines.append("")

    lines.extend(
        [
            "4. 자동 해석",
            f"- 시장 상태: {market_state}",
            f"- 해석: {_interpretation_sentence(market_state)}",
            "",
            "※ 자동 수집 데이터이므로 실제 투자 판단 전 원자료 확인 필요",
        ]
    )
    return "\n".join(lines)


def format_indicator_line(result: IndicatorResult) -> str:
    return (
        f"- {result.name}: {format_value(result)}, "
        f"{format_change(result)} {result.status_emoji}"
    )


def format_value(result: IndicatorResult) -> str:
    if result.value is None:
        return "N/A"

    if result.unit == "bp":
        return f"{_format_number(result.value, result.decimals)}bp"
    return f"{_format_number(result.value, result.decimals)}{result.unit}"


def format_change(result: IndicatorResult) -> str:
    if result.change is None:
        return "N/A"

    if result.change_type == "bp":
        return f"{result.change:+.0f}bp"
    return f"{result.change:+.1f}%"


def _format_number(value: float, decimals: int) -> str:
    return f"{value:,.{decimals}f}"


def _interpretation_sentence(market_state: str) -> str:
    if market_state == "리스크온":
        return "주요 위험자산 흐름이 우호적이며 금리와 달러 부담은 제한적으로 보입니다."
    if market_state == "리스크오프":
        return "위험자산 약세와 달러 또는 금리 상승이 겹쳐 방어적 점검이 필요합니다."
    if market_state == "인플레이션 압력":
        return "유가와 장기금리가 함께 상승해 물가 부담 확대 가능성을 점검해야 합니다."
    return "지표 방향이 엇갈려 개장 직후 추가 확인이 필요합니다."
