import os
import subprocess
import logging
import json
import tempfile
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSION_FILE = ".slack_gemini_sessions.json"

def load_sessions():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
    return {}

def save_sessions(sessions):
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(sessions, f)
    except Exception as e:
        logger.error(f"Error saving sessions: {e}")

def run_gemini_command(prompt, session_id=None):
    """gemini CLI 명령어를 실행하고 결과를 반환합니다."""
    try:
        cmd = ["gemini", "-y", "-p", prompt, "--output-format", "json"]
        if session_id:
            cmd.extend(["--resume", session_id])
            
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        raw_output = result.stdout.strip()
        
        try:
            start_idx = raw_output.find('{')
            end_idx = raw_output.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = raw_output[start_idx:end_idx]
                data = json.loads(json_str)
                return data, raw_output
            else:
                return None, raw_output
        except json.JSONDecodeError:
            return None, raw_output
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Gemini execution error: {e.stderr}")
        return {"error": e.stderr}, e.stderr
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": str(e)}, str(e)

def get_app():
    load_dotenv()
    app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

    @app.event("app_mention")
    def handle_app_mentions(event, say):
        text = event.get("text")
        user = event.get("user")
        thread_ts = event.get("thread_ts") or event.get("ts")
        
        prompt = " ".join(text.split()[1:]).strip()
        
        if not prompt:
            say(f"<@{user}>님, 무엇을 도와드릴까요? 프롬프트를 입력해주세요.", thread_ts=thread_ts)
            return

        try:
            app.client.reactions_add(
                channel=event.get("channel"),
                name="thinking_face",
                timestamp=event.get("ts")
            )
        except Exception as e:
            logger.error(f"Error adding reaction: {e}")

        # 기존 세션 확인
        sessions = load_sessions()
        session_id = sessions.get(thread_ts)

        # Gemini 실행
        data, raw_log = run_gemini_command(prompt, session_id=session_id)
        
        # 만약 resume 실패 시 (세션 만료 등) 다시 시도
        if session_id and data and data.get("error") and "session" in data.get("error").lower():
            logger.info("Session resume failed, retrying with fresh session...")
            data, raw_log = run_gemini_command(prompt, session_id=None)

        if data and isinstance(data, dict):
            # 새 세션 ID 저장
            new_session_id = data.get("session_id")
            if new_session_id:
                sessions[thread_ts] = new_session_id
                save_sessions(sessions)

            response_text = data.get("response", "응답 데이터에 'response' 필드가 없습니다.")
            say(f"<@{user}> Gemini 결과:\n\n{response_text}", thread_ts=thread_ts)
            
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                    tmp.write(raw_log)
                    tmp_path = tmp.name
                
                app.client.files_upload_v2(
                    channel=event.get("channel"),
                    file=tmp_path,
                    filename="gemini_log.json",
                    title="Gemini Full Log (JSON)",
                    initial_comment="상세 실행 로그입니다.",
                    thread_ts=thread_ts
                )
                os.remove(tmp_path)
            except Exception as e:
                logger.error(f"Error uploading file: {e}")
                say(f"⚠️ 로그 파일 업로드 중 오류가 발생했습니다: {e}", thread_ts=thread_ts)
        else:
            say(f"<@{user}> Gemini 실행 결과 (JSON 파싱 실패):\n\n{raw_log}", thread_ts=thread_ts)
        
        # 답변 완료 후 이모지 제거
        try:
            app.client.reactions_remove(
                channel=event.get("channel"),
                name="thinking_face",
                timestamp=event.get("ts")
            )
        except Exception as e:
            logger.error(f"Error removing reaction: {e}")
            
    return app

def run_server():
    load_dotenv()
    app = get_app()
    app_token = os.environ.get("SLACK_APP_TOKEN")
    if not app_token:
        print("Error: SLACK_APP_TOKEN is missing in .env")
        return
    handler = SocketModeHandler(app, app_token)
    print("⚡ Slack Gemini Bot is starting with Socket Mode...")
    handler.start()
