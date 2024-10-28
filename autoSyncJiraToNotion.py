from util import JiraUtil, NotionUtil
import time
from datetime import datetime
import logging

excludeTicket = ["MS-1490", "MS-1308", "MS-3246"]
excludeParentKey = ["SI-108", "SI-18"]
completeTaskStatusList = ["Done", "Cancelled", "Pending UAT", "Launch Ready", "Closed", "已關閉", "完成",
                          "On Hold", "已取消"]
excluded_sub_task = ["MS-1664", "EER-108", "EER-109", "EER-110", "EER-276", "EER-277", "EER-427", "EER-500", "EER-501",
                     "EER-515", "EER-516", "EER-517", "EER-536", "EER-537", "EER-538", "EER-539", "EER-540", "EER-541",
                     "EER-568", "EER-577", "EER-578", "EER-582", "EER-622", "EER-623", "EER-627", "EER-637", "EER-648",
                     "EER-651", "EER-652", "EER-671", "EER-682", "EER-684", "EER-685", "EER-687", "EER-690", "EER-704",
                     "EER-705", "EER-715", "EER-720", "EER-722", "EER-733", "EER-734", "EER-735", "EER-736", "EER-738",
                     "EER-739", "EER-740", "EER-741", "EER-742", "EER-743", "EER-744", "EER-745", "EER-749", "EER-750",
                     "EER-751", "EER-752", "EER-756", "EER-757", "EER-758", "EER-759", "EER-760", "EER-761", "EER-762",
                     "EER-763", "EER-765", "EER-767", "EER-769", "EER-770", "EER-783", "EER-788", "EER-789", "EER-790",
                     "EER-791", "EER-793", "EER-795", "EER-796", "EER-797", "EER-798", "EER-801", "EER-802", "EER-803",
                     "EER-804", "EER-805", "EER-810", "EER-813", "EER-814", "EER-815", "EER-816", "EER-817", "EER-818",
                     "EER-823", "EER-836", "EER-838", "EER-855", "EER-858", "EER-859", "EER-861", "EER-1490", "MS-1597",
                     "MS-1598", "MS-1661", "MS-1662", "MS-1943", "MS-1944", "MS-3440", "MS-3441", "MS-3444", "MS-3549",
                     "MS-3626", "MS-3649", "MS-3679", "MS-3694", "MS-3743", "MS-3790", "MS-3937", "MS-3940", "MS-3970",
                     "MS-3971", "MS-3972", "MS-3973", "MS-3974", "MS-4171", "MS-4195", "MS-4196", "MS-4197", "MS-4198",
                     "EER-1603", "EER-1571", "EER-1552", "EER-1535", "EER-1474", "EER-1471", "EER-1421", "EER-975",
                     "MS-4676", "MS-4677", "MS-4681", "EER-928", "EER-929", "EER-930", "EER-935", "EER-913", "EER-907",
                     "MS-4479", "MS-4184", "EER-719", "MS-3902", "MS-3903", "HYBRIS-2720", "EER-578", "EER-582",
                     "EER-622", "EER-623", "EER-627", "EER-637", "EER-648", "EER-651", "EER-652", "EER-671", "EER-682",
                     "EER-684", "EER-685", "EER-687", "EER-690", "EER-704", "EER-705", "EER-715", "EER-720", "EER-722",
                     "EER-733", "EER-734", "EER-735", "EER-736", "EER-738", "EER-739", "EER-740", "EER-741", "EER-742",
                     "EER-743", "EER-744", "EER-745", "EER-749", "EER-750", "EER-751", "EER-752", "EER-756", "EER-757",
                     "EER-758", "EER-759", "EER-760", "EER-761", "EER-762", "EER-763", "EER-765", "EER-767", "EER-769",
                     "EER-770", "EER-783", "EER-791", "EER-793", "EER-795", "EER-796", "EER-797", "EER-798", "EER-801",
                     "EER-802", "EER-803", "EER-804", "EER-805", "EER-810", "EER-813", "EER-814", "EER-815", "EER-816",
                     "EER-817", "EER-818", "EER-823", "EER-836", "EER-838", "EER-855", "EER-858", "EER-859", "EER-861",
                     "EER-1490", "MS-1943", "MS-1944", "MS-3549", "MS-3626", "MS-3649", "MS-3694", "MS-3743", "MS-3790",
                     "MS-3937", "MS-3940", "MS-3970", "MS-3971", "MS-3972", "MS-3973", "MS-3974", "MS-4171", "MS-4195",
                     "MS-4196", "MS-4197", "MS-4198", "EER-1603", "EER-1474", "EER-975", "MS-4676", "MS-4677",
                     "MS-4681", "EER-928", "EER-929", "EER-930", "EER-935", "EER-913", "EER-907", "MS-4479", "MS-4184",
                     "EER-719", "MS-3902", "MS-3903", "HYBRIS-2720"]


def create_notion_item(issue):
    if issue.key in excluded_sub_task:
        print(f"{issue.key} is exclude for save block")
        return
    if issue.fields.issuetype.name != '大型工作' and not issue.key.startswith('BUILD'):
        notionItemList = NotionUtil.findByTicket(
            NotionUtil.subtask_database_id if issue.fields.issuetype.subtask else NotionUtil.ecom_engine_database_id,
            NotionUtil.jira_url_prefix + issue.key)
        if "EER-1219" == issue.key:
            aa = 0
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
                    elif "Task" not in subtask and len(subtask) > 0:
                        NotionUtil.update_subtask_relate_to_task(subtask[0]["id"], create_task_res.json()["id"])
                        # TODO remove task if subTask db contains Task
                except Exception as e:
                    raise Exception(
                        f"create task fail, create_task_res[{create_task_res}]subtask[{subtask}]errorMsg[{e}]")


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
    #     if issue.key == "EER-1219":
    #         print(issue.key)
    # print("==================")

    # sort => build main ticket first
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
        system_name, assignee = NotionUtil.get_system_code_and_assignee(issue)
        if assignee is None:
            print(f"skip create [{issue.key}] because its exclude service")
        else:
            create_notion_item(issue)


def updateNotionTicketStatus():
    itemList = NotionUtil.findOpenedItem(NotionUtil.task_database_id)
    for item in itemList:
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


def update_eer_and_team1_ticket_status():
    itemList = NotionUtil.findOpenedItem(NotionUtil.ecom_engine_database_id)
    for item in itemList:
        if "EER-1441" in str(item["properties"]["Ticket"]):
            aa = 0
        if item["properties"]["Ticket"]["url"] is not None and "/" in item["properties"]["Ticket"]["url"]:
            urlAr = item["properties"]["Ticket"]["url"].split("/")
            issueKey = urlAr[len(urlAr) - 1]
            NotionUtil.updateTaskStatus(item, JiraUtil.findIssueByKey(issueKey))

    itemList = NotionUtil.findOpenedItem(NotionUtil.subtask_database_id)
    for item in itemList:
        if "EER-1441" in str(item["properties"]["Ticket"]):
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
    # print(NotionUtil.findByTicketLike("5466")[0])
    # updateNotionTicketStatus()
    # createEcomEngineTaskFromJira()

    logging.basicConfig(filename='./log/autoSyncJiraToNotionapp.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    while 1 == 1:
        try:
            now = datetime.now()
            if 6 < now.hour < 20:
                logging.info("start sync Jira ticket, " + now.strftime("%Y%m%d %H:%M:%S.%f"))
                create_eer_task_from_jira()
                create_team1_task_from_jira()
                update_eer_and_team1_ticket_status()
                logging.info("end sync Jira ticket, " + now.strftime("%Y%m%d %H:%M:%S.%f"))
            else:
                time.sleep(3600)
        except Exception as e:
            logging.info("autoSyncJiraToNotion execute fail, exception[{}]", e)
        time.sleep(1800)
