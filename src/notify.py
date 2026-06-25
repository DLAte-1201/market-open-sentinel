from __future__ import annotations

import os
import sys


def send_discord_message(message: str, webhook_url: str | None = None) -> bool:
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        _safe_print(message)
        _safe_print("\nDISCORD_WEBHOOK_URL이 없어 콘솔 출력만 수행했습니다.")
        return False

    try:
        import requests

        response = requests.post(url, json={"content": message}, timeout=15)
        response.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - 알림 실패 시에도 실행 로그를 남기고 종료
        print(f"Discord Webhook 전송 실패: {exc}")
        _safe_print(message)
        return False

    print("Discord Webhook 전송 완료")
    return True


def _safe_print(text: str) -> None:
    encoding = sys.stdout.encoding or "utf-8"
    safe_text = text.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(safe_text)
