import configparser
import json
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

config = configparser.ConfigParser()
config.read('application.ini')
# Set your Slack API token
slack_token = config["DEFAULT"]["slack_token"]
# Set the channel where you want to retrieve messages
# channel_id = "C05UMG8CA65"

# Initialize the WebClient with your Slack token
client = WebClient(token=slack_token)


def get_channel_message(channel_id, period_ms):
    isNotComplete = True
    next_cursor = None
    now_timestamp = int(time.time())
    startTime = now_timestamp - period_ms / 1000
    messageList = []
    while isNotComplete:
        # Call the conversations.history method to retrieve messages from the channel
        response = client.conversations_history(channel=channel_id, limit=100, cursor=next_cursor)
        # Print out the retrieved messages
        # print(response)
        next_cursor = response["response_metadata"]["next_cursor"]
        for message in response["messages"]:
            if float(message["ts"]) < startTime:
                isNotComplete = False
                break
            messageList.append(message)
    return messageList
