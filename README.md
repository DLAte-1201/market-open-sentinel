# market-open-sentinel

한국시간 오후 10시 30분, 미국 서머타임 기준 미국 본장 개장 시각에 주요 글로벌 시장 지표를 점검하고 Discord Webhook으로 한국어 요약 알림을 보내는 Python 프로젝트입니다.

이 알림은 투자 권유가 아니라 시장 리스크 점검용입니다.

## 주요 기능

- yfinance로 주가지수, 선물, 원자재, 암호화폐, 환율을 수집합니다.
- FRED API로 미국 10년물과 2년물 국채금리를 수집합니다.
- 특정 지표 수집에 실패해도 전체 실행은 중단하지 않고 해당 지표만 `N/A`로 표시합니다.
- 변화율, 금리 bp 변화, 10Y-2Y 스프레드, 상태 이모지, 자동 해석을 포함한 Discord 메시지를 생성합니다.
- GitHub Actions에서 평일마다 자동 실행됩니다.

## 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell에서는 아래처럼 가상환경을 활성화할 수 있습니다.

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 로컬 실행

`.env.example`을 참고해 `.env` 파일을 만들고 값을 채웁니다.

```env
FRED_API_KEY=your_fred_api_key_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

실행:

```bash
python -m src.main
```

`DISCORD_WEBHOOK_URL`이 없으면 Discord로 전송하지 않고 콘솔에만 출력합니다. `FRED_API_KEY`가 없으면 미국 10년물과 2년물 금리는 `N/A`로 표시됩니다.

## GitHub Secrets 설정

GitHub 저장소의 `Settings > Secrets and variables > Actions > New repository secret`에서 아래 값을 추가합니다.

- `FRED_API_KEY`
- `DISCORD_WEBHOOK_URL`

API 키와 Webhook URL은 코드에 하드코딩하지 않습니다.

## GitHub Actions 자동 실행 시간

워크플로 파일: `.github/workflows/market-open-check.yml`

현재 cron:

```yaml
cron: "30 13 * * 1-5"
```

GitHub Actions cron은 UTC 기준입니다. 미국 서머타임 기준 한국시간 오후 10시 30분은 UTC 13:30이므로 위 cron을 사용합니다.

미국 서머타임이 아닐 때는 미국 본장 개장 시간이 한국시간 오후 11시 30분이므로 cron을 아래처럼 바꿔야 합니다.

```yaml
cron: "30 14 * * 1-5"
```

수동 실행은 GitHub Actions 화면의 `workflow_dispatch`로 가능합니다.

## 감시 지표

| 구분 | 지표 | 데이터 소스 |
| --- | --- | --- |
| 위험자산 | BTC/USD, ETH/USD, 나스닥 종합지수, 나스닥100 선물, S&P 500, 다우존스 산업평균지수, 필라델피아 반도체 지수 | yfinance |
| 금리/환율 | 미국 10년물 국채금리, 미국 2년물 국채금리, 10Y-2Y 스프레드, USD/KRW, 달러 인덱스 | FRED, yfinance |
| 원자재 | WTI 원유 선물, 브렌트유 선물, 금 선물, 은 선물 | yfinance |

티커와 임계값은 `config/watchlist.yaml`에서 수정할 수 있습니다. yfinance 티커는 데이터 제공자 사정에 따라 바뀔 수 있습니다.

## 상태 이모지 규칙

- 주가지수/암호화폐/귀금속: `+1.0%` 이상 🟢, `-1.0%` 이하 🔴, 그 외 ⚪
- 원유: `+2.0%` 이상 🟠, `-2.0%` 이하 🔵, 그 외 ⚪
- 금리: `+5bp` 이상 🟡, `-5bp` 이하 🔵, 그 외 ⚪
- USD/KRW와 달러 인덱스: `+0.5%` 이상 🟡, `-0.5%` 이하 🔵, 그 외 ⚪

## 알림 예시

```text
[미국 본장 개장 시장 점검]
기준 시각: 2026-06-26 22:30 KST / 2026-06-26 13:30 UTC
투자 권유가 아닌 시장 리스크 점검용 알림입니다.

1. 위험자산
- BTC: 102,350달러, +2.1% 🟢
- ETH: 3,520.45달러, +1.4% 🟢
- 나스닥: 18,210.32포인트, +0.5% ⚪

2. 금리/환율
- 미국 10년물: 4.42%, +6bp 🟡
- 미국 2년물: 4.01%, +3bp ⚪
- 10Y-2Y 스프레드: 41bp, +3bp ⚪
- USD/KRW: 1,385.20원, +0.4% ⚪

3. 원자재
- WTI: 68.40달러, -2.8% 🔵

4. 자동 해석
- 시장 상태: 혼조
- 해석: 지표 방향이 엇갈려 개장 직후 추가 확인이 필요합니다.

※ 자동 수집 데이터이므로 실제 투자 판단 전 원자료 확인 필요
```

## 테스트

```bash
python -m unittest discover -s tests
```
