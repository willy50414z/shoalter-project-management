import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from util import SlackUtil

if __name__ == '__main__':
    channel_message_list = SlackUtil.get_channel_message("C05UMG8CA65", 1000 * 60 * 60 * 24 * 2)
    logMessageMap = {}
    for channel_message in channel_message_list:
        if "blocks" in channel_message:
            # print(message)
            message = channel_message["blocks"][0]["elements"][0]["elements"][0]["text"]
            for logMesRow in message.split("\n\n"):
                if "[developer-alert]" in logMesRow:
                    logMesRow = logMesRow[logMesRow.rfind("[developer-alert]") + 17:]
                    errorType = logMesRow.split(",")[0]
                    if errorType in logMessageMap:
                        logMessageMap[errorType].append(logMesRow[logMesRow.find(",") + 2:len(logMesRow) - 2])
                    else:
                        logMessageMap[errorType] = [logMesRow[logMesRow.find(",") + 2:len(logMesRow) - 2]]
    for key, value in logMessageMap.items():
        logMessageMap[key] = list(set(value))
    print(json.dumps(logMessageMap, indent=4))
