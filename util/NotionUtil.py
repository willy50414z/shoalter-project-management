import requests
from datetime import datetime, timedelta

from dto.NotionTaskDto import NotionTaskDto

task_database_id = 'e79515c7c75b490fb38147dbf5a645b8'  # Replace with your database ID
release_database_id = '4125f6f2e3f3425d9ebdcc0c4e493069'  # Replace with your database ID
integration_token = 'secret_1gyebl9EyV1eMpsIU2wSsUJMSiw4LqGHNJqqan4Qvvj'  # Replace with your integration token

peopleIdMap = {
    'TW - IT - BE - JOHN CHANG': '744b3b5b-ca64-4a33-a074-e948f1619b25'
    , 'TW - IT - BE - Luke Chen': 'a6f22742-dbb2-4c6f-aa85-55278672f272'
    , 'TW - IT - BE - Willy Cheng': '9ec132c2-2c35-4d72-a587-e567036b717e'
    , 'TW - IT - BE - Ainsley Wang': '496f4dd0-d2fa-4550-bc6c-1c661fe91c10'
    , 'TW - IT - BE - Shelby Cheng': 'a3458ee5-b64c-46f4-8264-f6aea1a08a45'
}

headers = {
    'Authorization': f'Bearer {integration_token}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'  # Specify the Notion API version
}

def findAllReleases():
    url = f'https://api.notion.com/v1/databases/{release_database_id}/query'
    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        raise ValueError("[findAllReleases] fetch notion data by issue key failed")

def findByReleaseDate(releaseDate):
    url = f'https://api.notion.com/v1/databases/{task_database_id}/query'
    payload = {"page_size": 100, "filter": {
        "property": "ReleaseDate",
        "select": {
            "equals": releaseDate
        }
    }}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "results" in data:
        notionItemList = []
        for item in data["results"]:
            notionItemList.append(NotionTaskDto(item))
        return notionItemList
    else:
        raise ValueError("[findByTicketLike] fetch notion data by issue key failed, releaseDate[" + releaseDate + "]")

def findByTicketLike(issueKey):
    url = f'https://api.notion.com/v1/databases/{task_database_id}/query'
    payload = {"page_size": 100, "filter": {
        "property": "Ticket",
        "rich_text": {
            "contains": issueKey
        }
    }}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        raise ValueError("[findByTicketLike] fetch notion data by issue key failed, issueKey[" + issueKey + "]")

def deleteOutOfDateTask():
    url = f'https://api.notion.com/v1/databases/{task_database_id}/query'
    three_months_ago = datetime.now() - timedelta(days=90)

    payload = {"page_size": 100, "filter": {
        "property": "Last edited time",
        "date": {"before": three_months_ago.isoformat()}
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    outOfDateTask = [task for task in data["results"] if task["properties"]["Status"]["status"]["name"] == "Done"]
    print("Prepared to delete " + str(len(outOfDateTask)) + " blocks")
    for task in outOfDateTask:
        print("Delete block ID[" + task["id"] + "]Name[" + task["properties"]["Name"]["title"][0]["plain_text"] + "]")
        response = requests.delete("https://api.notion.com/v1/blocks/" + task["id"], headers=headers)


def createPage(subTaskKey, title, taskKey, assigneeName):
    # assignee
    notionPeopleId = '9ec132c2-2c35-4d72-a587-e567036b717e'
    if assigneeName in peopleIdMap:
        notionPeopleId = peopleIdMap[assigneeName]

    payload = {
        "parent": {"type": "database_id", "database_id": task_database_id},
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": f"[{subTaskKey}] {title}"}}]
            },
            "ReleaseDate": {
                "type": "select",
                'select': {
                    'name': 'uncheck',
                    'color': 'brown'
                }
            },
            "Ticket": {
                'type': 'url',
                'url': f'https://hongkongtv.atlassian.net/browse/{subTaskKey}'
            },
            "ParentTicket": {
                'type': 'url',
                'url': f'https://hongkongtv.atlassian.net/browse/{taskKey}'
            },
            'Assignee': {
                'type': 'people',
                'people': [{'object': 'user', 'id': notionPeopleId}]}
        }
    }
    response = requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)
    print(response.json())

def update(database_id, payload):
    url = f'https://api.notion.com/v1/databases/{release_database_id}'
    response = requests.patch(url, json=payload, headers=headers)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        raise ValueError("[findAllReleases] fetch notion data by issue key failed")


if __name__ == '__main__':
    for item in findByReleaseDate("2023-11-13"):
        print(item.getTitle())
    # for item in findByReleaseDate("2023-11-13"):
    #     # print(item)
    #     print(item["properties"]["Name"]["title"][0]["plain_text"])
    #     print(item["properties"]["Project"]["select"]["name"])
    #     print(item["properties"]["Ticket"]["url"])
    #     for attachment in item["properties"]["attachment"]["multi_select"]:
    #         print(attachment["name"])
    # print()
