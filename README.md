# Slack Gemini Bot

Slack에서 Gemini CLI를 활용해 대화하고 실행 로그를 관리할 수 있는 도구입니다.

## 주요 기능

- **Gemini CLI 연동**: `@mention`을 통해 Gemini에게 질문하고 답변을 받습니다.
- **스레드 지원**: 대화 맥락 유지를 위해 스레드 내에서 답변합니다.
- **🤔 반응**: 질문을 인식하면 이모지로 즉각 피드백을 줍니다.
- **JSON 로그 첨부**: 실행 결과뿐만 아니라 전체 JSON 로그(`--output-format json`)를 파일로 첨부합니다.
- **CLI 인터페이스**: 서버 실행 및 간단한 메시지 전송을 위한 명령어를 제공합니다.

## 설치 방법

```bash
cd slack-gemini
pip install -e .
```

## 사용 방법

### 1. 전역 설정 (.env)
다음 환경 변수가 설정되어 있어야 합니다:
- `SLACK_BOT_TOKEN`: 슬랙 봇 토큰 (xoxb-...)
- `SLACK_APP_TOKEN`: 슬랙 앱 레벨 토큰 (xapp-...)
- `SLACK_CHANNEL_ID`: `send` 명령어를 사용할 기본 채널 ID

### 2. 명령어

**봇 서버 실행 (Socket Mode)**
```bash
slack-gemini run
```

**슬랙 채널로 메시지 전송**
```bash
slack-gemini send "안녕하세요!"
```

**Gemini 실행 후 결과를 슬랙으로 전송**
```bash
slack-gemini prompt "현재 삼성전자 주가는?"
```

## Slack App 설정 안내

이 봇이 정상적으로 작동하려면 Slack App에 다음과 같은 권한(Scopes)이 반드시 필요합니다:

### Bot Token Scopes
- `app_mentions:read`: 멘션 이벤트 수신
- `chat:write`: 메시지 전송
- `reactions:write`: 🤔 이모지 반응 추가
- `files:write`: 상세 로그 JSON 파일 업로드

### App-Level Scopes
- `connections:write`: Socket Mode 연결

---
> [!NOTE]
> `gemini` CLI가 시스템에 설치되어 있어야 하며, Node.js v20 이상 환경을 권장합니다.
