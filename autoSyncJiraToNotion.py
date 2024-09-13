from util import JiraUtil, NotionUtil
import time
from datetime import datetime
import logging

excludeTicket = ["MS-1490", "MS-1308", "MS-3246"]
excludeParentKey = ["SI-108", "SI-18"]
completeTaskStatusList = ["Done", "Cancelled", "Pending UAT", "Launch Ready", "Closed", "已關閉", "完成",
                          "On Hold", "已取消"]

def create_notion_item(issue):
    if issue.fields.issuetype.name != '大型工作' and not issue.key.startswith('BUILD'):
        notionItemList = NotionUtil.findByTicket(
            NotionUtil.subtask_database_id if issue.fields.issuetype.subtask else NotionUtil.ecom_engine_database_id,
            NotionUtil.jira_url_prefix + issue.key)
        if 0 == len(notionItemList):
            # create notion
            if issue.fields.issuetype.subtask:
                NotionUtil.createSubTask(issue)
            else:
                create_task_res = NotionUtil.create_task(NotionUtil.ecom_engine_database_id, issue)
                # 有subtask的task就不需要建subtasks
                subtask = NotionUtil.findByTicket(NotionUtil.subtask_database_id,
                                                  NotionUtil.jira_url_prefix + issue.key)
                try:
                    if len(issue.fields.subtasks) == 0 and 0 == len(subtask):
                        NotionUtil.createSubTask(issue, create_task_res.json()["id"])
                    elif "Task" not in subtask:
                        NotionUtil.update_subtask_relate_to_task(subtask[0]["id"], create_task_res.json()["id"])
                        # TODO remove task if subTask db contains Task
                except Exception as e:
                    raise Exception(f"create task fail, create_task_res[{create_task_res}]subtask[{subtask}]errorMsg[{e}]")

def create_team1_task_from_jira():
    # fetch JIRA incomplete ticket
    issueList = JiraUtil.get_team1_incompleted_task()
    # for issue in issueList:
    #     print(issue.key)
    # filt out build and complete ticket
    issueList = list(filter(lambda issue: not issue.key.startswith('BUILD') and ((
                                                                                         not issue.fields.issuetype.subtask and issue.key not in excludeParentKey and issue.fields.status.name not in completeTaskStatusList) or (
                                                                                         issue.fields.issuetype.subtask and issue.fields.parent.key not in excludeParentKey and issue.key not in excludeTicket and issue.fields.parent.fields.status.name not in completeTaskStatusList)),
                            issueList))
    # for issue in issueList:
    #     print(issue.key)
    # print("==================")

    #sort => build main ticket first
    issueList = sorted(issueList, key=lambda issue: issue.fields.issuetype.subtask)

    # for issue in issueList:
    #     print(issue.key)

    # check is ticket exist in notion
    for issue in issueList:
        if issue.key == "EER-1462":
            print("aa")
        create_notion_item(issue)


def create_eer_task_from_jira():
    issueList = JiraUtil.getEERIncompletedTask()
    for issue in issueList:
        if issue.key == "EER-1331":
            print("aa")
        create_notion_item(issue)

def updateNotionTicketStatus():
    itemList = NotionUtil.findOpenedItem(NotionUtil.task_database_id)
    for item in itemList:
        if item["properties"]["Ticket"]["url"] is not None and "/" in item["properties"]["Ticket"]["url"]:
            urlAr = item["properties"]["Ticket"]["url"].split("/")
            issueKey = urlAr[len(urlAr)-1]
            NotionUtil.updateTaskStatus(item, JiraUtil.findIssueByKey(issueKey))

    itemList = NotionUtil.findOpenedItem(NotionUtil.subtask_database_id)
    for item in itemList:
        if "EER-816" in str(item["properties"]["Ticket"]):
            aa = 0
        if item["properties"]["Ticket"]["url"] is not None and "/" in item["properties"]["Ticket"]["url"]:
            urlAr = item["properties"]["Ticket"]["url"].split("/")
            issueKey = urlAr[len(urlAr) - 1]
            NotionUtil.updateSubTaskStatus(item, JiraUtil.findIssueByKey(issueKey))

def update_eer_and_team1_ticket_status():
    itemList = NotionUtil.findOpenedItem(NotionUtil.ecom_engine_database_id)
    for item in itemList:
        if "MS-1462" in str(item["properties"]["Ticket"]):
            aa = 0
        if item["properties"]["Ticket"]["url"] is not None and "/" in item["properties"]["Ticket"]["url"]:
            urlAr = item["properties"]["Ticket"]["url"].split("/")
            issueKey = urlAr[len(urlAr) - 1]
            NotionUtil.updateTaskStatus(item, JiraUtil.findIssueByKey(issueKey))

    itemList = NotionUtil.findOpenedItem(NotionUtil.subtask_database_id)
    for item in itemList:
        if "EER-816" in str(item["properties"]["Ticket"]):
            aa = 0
        if item["properties"]["Ticket"]["url"] is not None and "/" in item["properties"]["Ticket"]["url"]:
            urlAr = item["properties"]["Ticket"]["url"].split("/")
            issueKey = urlAr[len(urlAr) - 1]
            NotionUtil.updateSubTaskStatus(item, JiraUtil.findIssueByKey(issueKey))


# create notion item

# update notion status

def printJiraTicket():
    issueList = JiraUtil.get_team1_incompleted_task()

    for issue in issueList:
        print(issue.key)

    # filt out build and complete ticket
    issueList = list(filter(lambda issue: not issue.key.startswith('BUILD') and ((
                                                                                         not issue.fields.issuetype.subtask and issue.key not in excludeParentKey and issue.fields.status.name not in completeTaskStatusList) or (
                                                                                         issue.fields.issuetype.subtask and issue.fields.parent.key not in excludeParentKey and issue.key not in excludeTicket and issue.fields.parent.fields.status.name not in completeTaskStatusList)),
                            issueList))
    # sort => build main ticket first
    issueList = sorted(issueList, key=lambda issue: issue.fields.issuetype.subtask)

    print("-------------------------")
    for issue in issueList:
        print(issue.key)

if __name__ == '__main__':
    # printJiraTicket()
    # updateNotionTicketStatus()
    # print(JiraUtil.findIssueByKey("BUILD-4504").fields.description)
    # print(NotionUtil.findOpenedItem(NotionUtil.task_database_id)[0])
    # print(NotionUtil.findByTicketLike("xx"))
    # updateNotionTicketStatus()
    # createEcomEngineTaskFromJira()

    logging.basicConfig(filename='./log/autoSyncJiraToNotionapp.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    while 1 == 1:
        try:
            logging.info("start sync Jira ticket, " + datetime.now().strftime("%Y%m%d %H:%M:%S.%f"))
            create_eer_task_from_jira()
            create_team1_task_from_jira()
            update_eer_and_team1_ticket_status()
            logging.info("end sync Jira ticket, " + datetime.now().strftime("%Y%m%d %H:%M:%S.%f"))
        except Exception as e:
            logging.info("autoSyncJiraToNotion execute fail, exception[{}]", e)
        time.sleep(1800)
