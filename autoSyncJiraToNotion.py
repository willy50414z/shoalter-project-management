from util import JiraUtil, NotionUtil
import time
from datetime import datetime
import logging

excludeTicket = ["MS-1490", "MS-1308", "MS-3246"]
excludeParentKey = ["SI-108", "SI-18"]
completeTaskStatusList = ["Done", "Cancelled", "Pending UAT", "Launch Ready", "Closed", "已關閉", "完成",
                          "On Hold", "已取消"]


def createNotionTaskFromJira():
    # fetch JIRA incomplete ticket
    issueList = JiraUtil.getIncompletedTask()
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
        if issue.key == "EER-1134":
            print("aa")
        # only create subtask or task without subtask
        if issue.fields.issuetype.name != '大型工作' and not issue.key.startswith('BUILD'):
            notionItemList = NotionUtil.findByTicket(
                NotionUtil.subtask_database_id if issue.fields.issuetype.subtask else NotionUtil.task_database_id,
                NotionUtil.jira_url_prefix + issue.key)
            if 0 == len(notionItemList):
                # create notion
                if issue.fields.issuetype.subtask:
                    NotionUtil.createSubTask(issue)
                else:
                    NotionUtil.createTask(NotionUtil.task_database_id, issue)
                    # 有subtask的task就不需要建subtasks
                    if len(issue.fields.subtasks) == 0:
                        NotionUtil.createSubTask(issue)

def createEcomEngineTaskFromJira():
    issueList = JiraUtil.getEERIncompletedTask()
    for issue in issueList:
        if issue.key == "EER-1134":
            print("aa")
        # only create subtask or task without subtask
        if issue.fields.issuetype.name != '大型工作' and not issue.key.startswith('BUILD'):
            notionItemList = NotionUtil.findByTicket(
                NotionUtil.ecom_engine_database_id,
                NotionUtil.jira_url_prefix + issue.key)
            if notionItemList is None or 0 == len(notionItemList):
                NotionUtil.createTask(NotionUtil.ecom_engine_database_id, issue)

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


# create notion item

# update notion status

def printJiraTicket():
    issueList = JiraUtil.getIncompletedTask()

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
    # print(NotionUtil.findByTicketLike("1134"))
    # updateNotionTicketStatus()

    logging.basicConfig(filename='E:/tmp/autoSyncJiraToNotionapp.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    while 1 == 1:
        try:
            logging.info("start sync Jira ticket, " + datetime.now().strftime("%Y%m%d %H:%M:%S.%f"))
            createNotionTaskFromJira()
            updateNotionTicketStatus()
            logging.info("end sync Jira ticket, " + datetime.now().strftime("%Y%m%d %H:%M:%S.%f"))
        except Exception as e:
            logging.info("autoSyncJiraToNotion execute fail, exception[{}]", e)
        time.sleep(1800)

    # NotionUtil.deleteOutOfDateTask()
    # print(NotionUtil.findByTicketLike("2428"))

    # notionItems = NotionUtil.findAllReleases()
    # for notionItem in notionItems:
    #     print(notionItem["id"])
    #     print(notionItem["properties"]["Name"]["title"][0]["text"]["content"])
    #     print(notionItem["properties"]["Release Date"]["date"]["start"])
    #     for releaseTicket in notionItem["properties"]["ReleaseTickets"]["multi_select"]:
    #         print(releaseTicket["name"])
