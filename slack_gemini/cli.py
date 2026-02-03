import os
import sys
import argparse
from dotenv import load_dotenv
from slack_sdk import WebClient
from .bot import run_server, run_gemini_command

def send_message(text):
    load_dotenv()
    token = os.environ.get("SLACK_BOT_TOKEN")
    channel = os.environ.get("SLACK_CHANNEL_ID")
    if not token or not channel:
        print("Error: SLACK_BOT_TOKEN or SLACK_CHANNEL_ID is missing in .env")
        return
    
    client = WebClient(token=token)
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        if response["ok"]:
            print(f"Successfully sent message to {channel}")
        else:
            print(f"Failed to send message: {response['error']}")
    except Exception as e:
        print(f"Error: {e}")

def run_prompt(prompt):
    load_dotenv()
    print(f"Running gemini prompt: {prompt}")
    data, raw_log = run_gemini_command(prompt)
    
    if data and isinstance(data, dict):
        response_text = data.get("response", "No response field in data.")
        slack_msg = f"🚀 *CLI Gemini Prompt*\n\n*Q:* {prompt}\n\n*A:* {response_text}"
        send_message(slack_msg)
        print(response_text)
    else:
        print("Error: Gemini execution or parsing failed.")
        print(raw_log)

def main():
    parser = argparse.ArgumentParser(description="Slack Gemini Bot CLI")
    subparsers = parser.add_subparsers(dest="command", help="commands")

    # slack-gemini run
    run_parser = subparsers.add_parser("run", help="Run the Slack Gemini Bot server")

    # slack-gemini send "message"
    send_parser = subparsers.add_parser("send", help="Send a message to Slack")
    send_parser.add_argument("message", help="The message to send")

    # slack-gemini prompt "query"
    prompt_parser = subparsers.add_parser("prompt", help="Run a Gemini prompt and send the result to Slack")
    prompt_parser.add_argument("text", help="The prompt text to send to Gemini")

    args = parser.parse_args()

    if args.command == "run":
        run_server()
    elif args.command == "send":
        send_message(args.message)
    elif args.command == "prompt":
        run_prompt(args.text)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
