import configparser

import requests
from datetime import datetime, timedelta

from dto.NotionTaskDto import NotionTaskDto

task_database_id = 'b2bc16e47be74cc68bd90b6d1bf8a5b8'  # Replace with your database ID
subtask_database_id = '39c41b1fa9a9464fb197e088349c5861'  # Replace with your database ID
release_database_id = '4125f6f2e3f3425d9ebdcc0c4e493069'  # Replace with your database ID

config = configparser.ConfigParser()
config.read('application.ini')
integration_token = config["DEFAULT"]["notion_token"]  # Replace with your integration token

jira_url_prefix = "https://hongkongtv.atlassian.net/browse/"

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


def findByReleaseDateIsAndBuildTicketIsEmpty(releaseDate):
    url = f'https://api.notion.com/v1/databases/{task_database_id}/query'
    payload = {"page_size": 100, "filter": {"and": [{
        "property": "ReleaseDate",
        "select": {
            "equals": releaseDate
        }
    }, {
        "property": "BuildTicket",
        "url": {
            "does_not_equal": "xx"
        }

    }
    ]}}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        raise ValueError("[findByTicketLike] fetch notion data by issue key failed, releaseDate[" + releaseDate + "]data["+str(data)+"]")


def findByTicketLike(issueKey):
    url = f'https://api.notion.com/v1/databases/{subtask_database_id}/query'
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


def findByTicket(database_id, issueKey):
    try:
        url = f'https://api.notion.com/v1/databases/{database_id}/query'
        payload = {"page_size": 100, "filter": {
            "property": "Ticket",
            "rich_text": {
                "equals": issueKey
            }
        }}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if "results" in data:
            if len(data["results"]) == 0:
                print("notion item not found, databaseId[" + database_id + "]issueKey[" + issueKey + "]")
            return data["results"]
        else:
            raise ValueError("[findByTicketLike] fetch notion data by issue key failed, issueKey[" + issueKey + "]")
    except Exception as e:
        print("can't get notion item, databaseId[" + database_id + "]issueKey[" + issueKey + "]")
        raise e


def findOpenedItem(database_id):
    url = f'https://api.notion.com/v1/databases/{database_id}/query'
    payload = {"page_size": 100, "filter": {
        "and": [
            {
                "property": "JiraStatus",
                "select": {
                    "does_not_equal": "CLOSED"
                }
            },
            {
                "property": "JiraStatus",
                "select": {
                    "does_not_equal": "CANCELED"
                }
            },
            {
                "property": "JiraStatus",
                "select": {
                    "does_not_equal": "Report"
                }
            }
        ]

    }}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        return data


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
                'url': f'{jira_url_prefix}{subTaskKey}'
            },
            "ParentTicket": {
                'type': 'url',
                'url': f'{jira_url_prefix}{taskKey}'
            },
            'Assignee': {
                'type': 'people',
                'people': [{'object': 'user', 'id': notionPeopleId}]}
        }
    }
    response = requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)
    print(response.json())


def createTask(issue):
    print(f'start create task, issue.key[{issue.key}]')
    payload = {
        "parent": {"type": "database_id", "database_id": task_database_id},
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": f"[{issue.key}] {issue.fields.summary}"}}]
            },
            "Ticket": {
                'type': 'url',
                'url': jira_url_prefix + issue.key
            },
            'Assignee': {
                'type': 'people',
                'people': [{'object': 'user', 'id': getAssigneeByIssue(issue)}]
            },
            "JiraStatus": {
                "type": "select",
                'select': {
                    'name': issue.fields.status.name
                }
            },
            "ReleaseDate": {
                "type": "select",
                'select': {
                    'name': "uncheck"
                }
            }
        }
    }

    system_name = None
    if "[cart-service]" in issue.fields.summary:
        system_name = "cart-service"
    elif "[address-service]" in issue.fields.summary:
        system_name = "address-service"
    elif "[order-service]" in issue.fields.summary:
        system_name = "order-service"
    elif "[IIDS]" in issue.fields.summary:
        system_name = "IIDS"
    elif "[IIMS-LM]" in issue.fields.summary:
        system_name = "IIMS-LM"
    elif "[IIMS]" in issue.fields.summary:
        system_name = "IIMS-HKTV"

    if system_name:
        payload["properties"]["System"] = {
            "type": "select",
            'select': {
                'name': system_name
            }
        }

    response = requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)
    print(response.json())


def createSubTask(issue):
    print(f'start create subtask, issue.key[{issue.key}]')
    payload = {
        "parent": {"type": "database_id", "database_id": subtask_database_id},
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"type": "text", "text": {"content": f"[{issue.key}] {issue.fields.summary}"}}]
            },
            'Assignee': {
                'type': 'people',
                'people': [{'object': 'user', 'id': getAssigneeByIssue(issue)}]
            },
            "Ticket": {
                'type': 'url',
                'url': jira_url_prefix + issue.key
            },
            "JiraStatus": {
                "type": "select",
                'select': {
                    'name': issue.fields.status.name
                }
            },
            "Status": {"status": {"name": "Not started"}},
            "Task": {
                "type": "relation",
                "relation": [
                    {
                        "id":
                            findByTicket(task_database_id,
                                         f"{jira_url_prefix}{issue.fields.parent.key if issue.fields.issuetype.subtask else issue.key}")[
                                0]["id"]
                    }
                ]
            }
        }
    }

    response = requests.post('https://api.notion.com/v1/pages', json=payload, headers=headers)
    print(response.json())


def getAssigneeByIssue(issue):
    return peopleIdMap[
        issue.fields.assignee.displayName if issue.fields.assignee is not None and issue.fields.assignee.displayName in peopleIdMap else 'TW - IT - BE - Willy Cheng']


def updateTaskStatus(page, issue):
    # issue.fields.fixVersions[0].name
    # page["properties"]["fixVersion"]["rich_text"][0]["plain_text"]
    if page["properties"]["JiraStatus"]["select"]["name"] == issue.fields.status.name and len(
            page["properties"]["fixVersion"]["rich_text"]) > 1 and page["properties"]["fixVersion"]["rich_text"][0][
        "plain_text"] == issue.fields.fixVersions[0].name:
        return ""
    else:
        url = f'https://api.notion.com/v1/pages/{page["id"]}'
        fix_versions = ""
        for fix_version in issue.fields.fixVersions:
            fix_versions += fix_version.name + ","
        if len(fix_versions) > 0:
            fix_versions = fix_versions[0:len(fix_versions)-1]

        payload = {
            "properties": {
                # 'Assignee': {
                #     'type': 'people',
                #     'people': [{'object': 'user', 'id': getAssigneeByIssue(issue)}]
                # },
                "JiraStatus": {
                    "type": "select",
                    'select': {
                        'name': issue.fields.status.name
                    }
                },
                "fixVersion": {
                    'rich_text': [{
                        'text': {
                            'content': fix_versions}
                    }]
                }
            }
        }
        response = requests.patch(url, json=payload, headers=headers)
        return response.json()


def update_build_ticket(page_id, issue_key):
    url = f'https://api.notion.com/v1/pages/{page_id}'
    payload = {"properties": {
        "BuildTicket": {
            'type': 'url',
            'url': str(issue_key)
        }
    }
    }
    response = requests.patch(url, json=payload, headers=headers)
    return response.json()


def updateSubTaskStatus(page, issue):
    # issue.fields.fixVersions[0].name
    # page["properties"]["fixVersion"]["rich_text"][0]["plain_text"]
    try:
        if page["properties"]["JiraStatus"]["select"] is not None and page["properties"]["JiraStatus"]["select"][
            "name"] == issue.fields.status.name:
            return ""
        else:
            url = f'https://api.notion.com/v1/pages/{page["id"]}'
            payload = {
                "properties": {
                    # 'Assignee': {
                    #     'type': 'people',
                    #     'people': [{'object': 'user', 'id': getAssigneeByIssue(issue)}]
                    # },
                    "JiraStatus": {
                        "type": "select",
                        'select': {
                            'name': issue.fields.status.name
                        }
                    }
                }
            }
            if issue.fields.status.name == "已取消":
                payload["properties"]["Status"] = {"status": {"name": "Done"}}
            response = requests.patch(url, json=payload, headers=headers)
            return response.json()
    except Exception:
        print("[updateSubTaskStatus] update SubTask Status throw error")
        print(page)
        print(issue)
        raise
# if __name__ == '__main__':
# for item in findByReleaseDate("2023-11-13"):
#     print(item.getTitle())
# for item in findByReleaseDate("2023-11-13"):
#     # print(item)
#     print(item["properties"]["Name"]["title"][0]["plain_text"])
#     print(item["properties"]["Project"]["select"]["name"])
#     print(item["properties"]["Ticket"]["url"])
#     for attachment in item["properties"]["attachment"]["multi_select"]:
#         print(attachment["name"])
# print()
