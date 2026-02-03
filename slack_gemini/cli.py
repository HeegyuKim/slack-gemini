import os
import sys
import argparse
from dotenv import load_dotenv
from slack_sdk import WebClient
from .bot import run_server

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

def main():
    parser = argparse.ArgumentParser(description="Slack Gemini Bot CLI")
    subparsers = parser.add_subparsers(dest="command", help="commands")

    # slack-gemini run
    run_parser = subparsers.add_parser("run", help="Run the Slack Gemini Bot server")

    # slack-gemini send "message"
    send_parser = subparsers.add_parser("send", help="Send a message to Slack")
    send_parser.add_argument("message", help="The message to send")

    args = parser.parse_args()

    if args.command == "run":
        run_server()
    elif args.command == "send":
        send_message(args.message)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
