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
                     "MS-4479", "MS-4184", "EER-719", "MS-3902", "MS-3903", "HYBRIS-2720", "HYBRIS-3292", "HYBRIS-3300",
                     "HYBRIS-3576", "MS-1307", "MS-1488", "MS-1489", "MS-1539", "MS-1556", "MS-1557", "MS-1559",
                     "MS-1561", "MS-1712", "MS-1713", "MS-1911", "MS-1929", "MS-1974", "MS-2123", "MS-2250", "MS-2431",
                     "MS-2464", "MS-2511", "MS-2797", "MS-2831", "MS-2880", "MS-2953", "MS-3011", "MS-3054", "MS-3111",
                     "MS-3243", "MS-3459", "MS-3542", "MS-3742", "MS-3803", "MS-3915", "MS-3929", "MS-3931", "MS-3932",
                     "MS-4134", "MS-4143", "MS-4172", "MS-4385", "MS-4408", "MS-4430", "MS-4469", "MS-4795", "MS-5161",
                     "MS-5452", "MS-5620", "MS-5878", "EER-92", "EER-93", "EER-127", "EER-152", "EER-160", "EER-199",
                     "EER-206", "EER-272", "EER-273", "EER-275", "EER-288", "EER-329", "EER-336", "EER-338", "EER-353",
                     "EER-360", "EER-361", "EER-373", "EER-384", "EER-388", "EER-401", "EER-426", "EER-435", "EER-439",
                     "EER-462", "EER-463", "EER-464", "EER-473", "EER-505", "EER-506", "EER-513", "EER-530", "EER-532",
                     "EER-534", "EER-535", "EER-595", "EER-599", "EER-603", "EER-604", "EER-605", "EER-611", "EER-636",
                     "EER-640", "EER-641", "EER-732", "EER-774", "EER-775", "EER-776", "EER-779", "EER-786", "EER-822",
                     "EER-828", "EER-833", "EER-840", "EER-841", "EER-845", "EER-846", "EER-847", "EER-848", "EER-849",
                     "EER-850", "EER-854", "EER-863", "EER-866", "EER-870", "EER-872", "EER-880", "EER-881", "EER-882",
                     "EER-883", "EER-889", "EER-893", "EER-902", "EER-921", "EER-922", "EER-937", "EER-943", "EER-951",
                     "EER-952", "EER-953", "EER-954", "EER-956", "EER-958", "EER-959", "EER-960", "EER-963", "EER-965",
                     "EER-980", "EER-984", "EER-985", "EER-1004", "EER-1006", "EER-1007", "EER-1008", "EER-1009",
                     "EER-1019", "EER-1020", "EER-1021", "EER-1023", "EER-1031", "EER-1037", "EER-1038", "EER-1039",
                     "EER-1045", "EER-1060", "EER-1066", "EER-1088", "EER-1103", "EER-1106", "EER-1111", "EER-1152",
                     "EER-1154", "EER-1161", "EER-1167", "EER-1177", "EER-1194", "EER-1208", "EER-1215", "EER-1221",
                     "EER-1232", "EER-1268", "EER-1275", "EER-1282", "EER-1289", "EER-1291", "EER-1323", "EER-1324",
                     "EER-1331", "EER-1356", "EER-1357", "EER-1358", "EER-1362", "EER-1371", "EER-1384", "EER-1399",
                     "EER-1400", "EER-1407", "EER-1411", "EER-1416", "EER-1426", "EER-1427", "EER-1428", "EER-1433",
                     "EER-1454", "EER-1503", "EER-1534", "EER-1543", "EER-1565", "EER-1569", "EER-1601", "EER-1627",
                     "EER-1164", "EER-1630", "EER-1659", "ECOMART-673", "HYBRIS-1790", "HYBRIS-1865", "HYBRIS-2200",
                     "HYBRIS-2567", "HYBRIS-3036", "HYBRIS-3189", "EER-1069", "EER-1070", "EER-1086", "EER-1134",
                     "EER-1137", "EER-1138", "EER-1139", "EER-1140", "EER-1142", "EER-1143", "EER-1145", "EER-1148",
                     "EER-1165", "EER-1220", "EER-1236", "EER-1237", "EER-1238", "EER-1239", "EER-1240", "EER-1267",
                     "EER-1270", "EER-1286", "EER-1297", "EER-1298", "EER-1338", "EER-1339", "EER-1340", "EER-1342",
                     "EER-1368", "EER-1372", "EER-1373", "EER-1374", "EER-1375", "EER-1376", "EER-1382", "EER-1383",
                     "EER-1408", "EER-1466", "EER-1467", "EER-1468", "EER-1469", "EER-1470", "EER-1472", "EER-1473",
                     "EER-1478", "EER-1479", "EER-1482", "EER-1483", "EER-1489", "EER-1491", "EER-1492", "EER-1493",
                     "EER-1494", "EER-1497", "EER-1498", "EER-1500", "EER-1501", "EER-1502", "EER-1536", "EER-1537",
                     "EER-1538", "EER-1539", "EER-1540", "EER-1570", "EER-1572", "EER-1590", "EER-1591", "EER-1592",
                     "EER-1602", "EER-1608", "EER-1610", "EER-1613", "EER-1614", "EER-1615", "EER-1616", "EER-1617",
                     "EER-1619", "EER-1620", "EER-1651", "EER-1665", "EER-1666", "HYBRIS-3413", "HYBRIS-3414",
                     "MS-5481", "MS-5587", "MS-5480", "EER-1190", "EER-1147"]


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
    # print(NotionUtil.findByTicketLike("123")[0])
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
