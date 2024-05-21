import sys
import time
import json
from util import NotionUtil, GitlabUtil, JiraUtil, GitUtil

# ARGV (systemCode)[all system] (date)[next date]
releaseDate = sys.argv[1]

systemCode = ""
if len(sys.argv) > 2:
    systemCode = sys.argv[2]

systemBaseInfo = {
    "address-service": {"project_id": 975,
                        "gitlab_url": "https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/business_module/shoalter-ecommerce-business-address-service",
                        "system_full_name": "Ecommerence Engine Address Service",
                        "repo_path": "E:/Code/shoalter-ecommerce-business/shoalter-ecommerce-business-address-service/"}
    , "cart-service": {"project_id": 967,
                       "gitlab_url": "https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/business_module/shoalter-ecommerce-business-cart-service",
                       "system_full_name": "Ecommerence Engine Cart Service",
                       "repo_path": "E:/Code/shoalter-ecommerce-business/shoalter-ecommerce-business-cart-service/"}
    , "order-service": {"project_id": 971,
                        "gitlab_url": "https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/business_module/shoalter-ecommerce-business-order-service",
                        "system_full_name": "Ecommerence Engine Order Service",
                        "repo_path": "E:/Code/shoalter-ecommerce-business/shoalter-ecommerce-business-order-service/"}
    , "IIMS-HKTV": {"project_id": 528,
                    "gitlab_url": "https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/inventory/ims",
                    "domain": "iims-restful.shoalter.com,iims-grpc.shoalter.com",
                    "system_full_name": "Share Stock HKTVmall IIMS (Intracompany Inventory Management System)",
                    "repo_path": "E:/Code/nochange/ims"}
    , "IIDS": {"project_id": 531,
               "gitlab_url": "https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/inventory/ids",
               "domain": "iids-restful.shoalter.com, iids-grpc.shoalter.com",
               "system_full_name": "Share Stock IIDS (Intracompany Inventory Distribution system) ",
               "repo_path": "E:/Code/nochange/ids"}
    , "IIMS-LM": {"project_id": 865,
                  "gitlab_url": "https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/inventory/uuid-iims",
                  "system_full_name": "Share Stock LittleMall IIMS (Intracompany Inventory Management System)",
                  "repo_path": "E:/Code/nochange/uuid-iims"}
}

buildTicketDescTemplate = """
GitLab Project: [${gitlab_url}|${gitlab_url}]

{color:#ff5630}*ArgoCD MR:* {color}[${mr_url}|${mr_url}]

Revision: ${release_branch}
Tag: ${release_sha}

System update: *N*

Domain: ${domain}

Service interruption: *N*
Maintenance page: *N*

Can fall back: *Y*
Fall back revision: ${fallback_sha}
Fall back tag: ${fallback_branch}

Execute IMPEX/SQL before build : *N*

Execute IMPEX/SQL after build : *N*

Contact: [Willy Cheng, [willy.cheng@shoalter.com|mailto:willy.cheng@shoalter.com],  Tony Ng, [hokan@shoatler.com|mailto:bill.kuo@shoatler.com]]
System programmer contact: [Willy Cheng, [willy.cheng@shoalter.com|mailto:willy.cheng@shoalter.com],  Tony Ng, [hokan@shoatler.com|mailto:bill.kuo@shoatler.com]]

Tickets:

${feature_tickets}
"""


def get_release_notion_info():
    releaseNotionItemList = NotionUtil.findByReleaseDateIsAndBuildTicketIsEmpty(releaseDate)
    notionItemInfo = {}
    for notionItem in releaseNotionItemList:
        sysCode = notionItem["properties"]["System"]["select"]["name"]
        completeRatio = notionItem["properties"]["CompleteRatio"]["rollup"]["number"]
        ticketLink = notionItem["properties"]["Ticket"]["url"]
        fixVersion = notionItem["properties"]["fixVersion"]["rich_text"][0]["plain_text"]
        if completeRatio < 1:
            raise ValueError("task is not completed, sysCode[" + sysCode + "]ticketLink[" + ticketLink + "]")
        if sysCode not in notionItemInfo:
            notionItemInfo[sysCode] = {}
            notionItemInfo[sysCode]["tickets"] = []
            notionItemInfo[sysCode]["notion_pages_id"] = []
        notionItemInfo[sysCode]["tickets"].append(ticketLink)
        notionItemInfo[sysCode]["fix_version"] = fixVersion
        notionItemInfo[sysCode]["notion_pages_id"].append(notionItem["id"])
    return notionItemInfo


# for item in releaseNotionItemList:
#     print(item.notionItem["properties"]["Project"])
# if len(systemCode) > 0:
#     sysCodeAr = systemCode.split(",")
#     releaseNotionItemList = [item for item in releaseNotionItemList if item.getProjectName() in sysCodeAr]
#
# print(len(releaseNotionItemList))
#

def checkTicketHasMerged(notionInfo):
    # create feature branch to staging的MR，看看是否有change，應該要是0
    for sysCode in notionInfo.keys():
        print(f"check has feature branch merged to staging, sysCode[{sysCode}]")
        projectId = systemBaseInfo[sysCode]["project_id"]
        for jiraUrl in notionInfo[sysCode]["tickets"]:
            issueKey = jiraUrl.split("browse/")[1]
            mrRes = GitlabUtil.createMergeRequest(projectId, "feature/" + issueKey, "staging",
                                                  "Merge request to staging for check has ticket merged",
                                                  "Merge request to staging for check has ticket merged")
            if "toStagingMrIid" not in notionInfo[sysCode]:
                notionInfo[sysCode]["toStagingMrIid"] = []
            notionInfo[sysCode]["toStagingMrIid"].append(mrRes["iid"])

    # 睡個5秒等gitlab整理一下訊息
    time.sleep(10)

    # 撈MR看看change是不是0
    for sysCode in notionInfo.keys():
        projectId = systemBaseInfo[sysCode]["project_id"]
        for mrIid in notionInfo[sysCode]["toStagingMrIid"]:
            mrRes = GitlabUtil.getMergeRequest(projectId, mrIid)
            # 有沒有問題都close check branch
            GitlabUtil.closeMergeRequest(projectId, mrIid)
            if mrRes["changes_count"] is not None:
                raise ValueError(
                    f"feature branch is not merge to staging, feature branch[{mrRes["source_branch"]}]MR[{mrRes["web_url"]}]")
            print(f"feature branch merged to staging check completed, sysCode[{sysCode}]")


def createReleaseBranch(notionInfo):
    for sysCode in notionInfo.keys():
        if sysCode not in systemBaseInfo or "project_id" not in systemBaseInfo[sysCode]:
            raise ValueError("can't find gitlab project id, sysCode[" + sysCode + "]")
        releaseVersion = notionInfo[sysCode]["fix_version"].split("@")[1]
        release_branch_name = "release/" + releaseVersion.replace("-", "") + "_0545"
        print(f"create release branch, sysCode[{sysCode}]branch_name[{release_branch_name}]")
        releaseBranchRes = GitlabUtil.createBranches(systemBaseInfo[sysCode]["project_id"], "staging",
                                                     release_branch_name)
        print(f"response[{releaseBranchRes}]")
        if "message" in releaseBranchRes and 'Branch already exists' == releaseBranchRes["message"]:
            print(f"Branch already exists, delete branch and re-create")
            releaseBranchRes = GitlabUtil.delete_branch(systemBaseInfo[sysCode]["project_id"], release_branch_name)
            print(f"delete release branch response[{releaseBranchRes}]")
            releaseBranchRes = GitlabUtil.createBranches(systemBaseInfo[sysCode]["project_id"], "staging",
                                                         release_branch_name)
            print(
                f"re-create release branch, sysCode[{sysCode}]branch_name[{release_branch_name}]response[{releaseBranchRes}]")
        notionInfo[sysCode]["release_branch"] = release_branch_name
        notionInfo[sysCode]["sha"] = releaseBranchRes["commit"]["id"]


def check_pipeline_process(notionInfo):
    # get pipeline id
    for sysCode in notionInfo.keys():
        projectId = systemBaseInfo[sysCode]["project_id"]
        pipelineRsList = GitlabUtil.getPipelinesByProjectId(projectId)
        waitTime = 0
        while "pipeline_id" not in notionInfo[sysCode]:
            for pipeineRes in pipelineRsList:
                if pipeineRes["sha"] == notionInfo[sysCode]["sha"] and pipeineRes["ref"] == notionInfo[sysCode][
                    "release_branch"] and (pipeineRes["status"] == 'created' or pipeineRes["status"] == "running"):
                    notionInfo[sysCode]["pipeline_id"] = pipeineRes["id"]
                    break
            waitTime += 1
            if waitTime > 30:
                raise ValueError("can't find release branch pipeline")
            time.sleep(10)

    # check pipeline status
    allPipelineComplete = False
    while not allPipelineComplete:
        allPipelineComplete = True
        for sysCode in notionInfo.keys():
            projectId = systemBaseInfo[sysCode]["project_id"]
            pipId = notionInfo[sysCode]["pipeline_id"]
            pipelineJobsRes = GitlabUtil.getPipelineJobsByProjectIdAndPipId(projectId, pipId)
            pipelineJobsRes = sorted(pipelineJobsRes, key=lambda job: job["id"])
            for jobInfo in pipelineJobsRes:
                if jobInfo["status"] != "success" and jobInfo["status"] != "failed":
                    print(f"{sysCode} is {jobInfo["status"]} in {jobInfo["name"]}")
                    allPipelineComplete = False
                    break
                elif jobInfo["status"] == "failed":
                    print(
                        f"release branch pipeline failed, skip this project, sysCode[{sysCode}]pipeline url[{jobInfo["web_url"]}]")
                    notionInfo.pop(sysCode)
                elif jobInfo["status"] == "success" and "create merge request" in str(jobInfo["name"]):
                    notionInfo[sysCode]["create_release_mr_job_id"] = jobInfo["id"]
        # 30秒檢查一次
        time.sleep(60)


def load_release_mr_url(notionInfo):
    for sysCode in notionInfo.keys():
        print(f"load release mr url, sysCode[{sysCode}]")
        projectId = systemBaseInfo[sysCode]["project_id"]
        createReleaseMrJobId = notionInfo[sysCode]["create_release_mr_job_id"]
        jobLog = GitlabUtil.getPipelineJobLogByProjectIdAndJobId(projectId, createReleaseMrJobId)
        releaseMrRes = json.loads(jobLog[jobLog.find("{"):jobLog.rfind("}") + 1])
        notionInfo[sysCode]["release_mr_url"] = releaseMrRes["web_url"]


def load_last_build_info(notion_info, sys_code):
    ticket = JiraUtil.get_last_build_ticket(systemBaseInfo[sys_code]["system_full_name"])
    desc = ticket[0].fields.description
    lastRevisionInfo = desc[desc.find("Revision:") + 10:desc.rfind("System update:") - 2].split("\nTag: ")
    notion_info[sys_code]["last_revision"] = lastRevisionInfo[0]
    notion_info[sys_code]["last_tag"] = lastRevisionInfo[1]


def build_build_ticket_content(notion_info, sys_code):
    buildTicketDesc = buildTicketDescTemplate
    buildTicketDesc = buildTicketDesc.replace("${gitlab_url}", systemBaseInfo[sys_code]["gitlab_url"])
    buildTicketDesc = buildTicketDesc.replace("${mr_url}", notion_info[sys_code]["release_mr_url"])
    buildTicketDesc = buildTicketDesc.replace("${release_branch}", notion_info[sys_code]["release_branch"])
    buildTicketDesc = buildTicketDesc.replace("${release_sha}", notion_info[sys_code]["sha"])
    buildTicketDesc = buildTicketDesc.replace("${domain}", "" if "domain" not in systemBaseInfo[sys_code] else
    systemBaseInfo[sys_code]["domain"])
    buildTicketDesc = buildTicketDesc.replace("${fallback_sha}", notion_info[sys_code]["last_revision"])
    buildTicketDesc = buildTicketDesc.replace("${fallback_branch}", notion_info[sys_code]["last_tag"])
    feature_tickets = ""
    for ticket in notion_info[sys_code]["tickets"]:
        feature_tickets += "[" + ticket + "|" + ticket + "|smart-link]\r\n"
    feature_tickets = feature_tickets[:len(feature_tickets) - 2]
    buildTicketDesc = buildTicketDesc.replace("${feature_tickets}", feature_tickets)
    return buildTicketDesc


def create_build_ticket(notion_info):
    for sys_code in notion_info.keys():
        release_version = notion_info[sys_code]["fix_version"].split("@")[1]
        title = "Shoalter - Production Build - " + systemBaseInfo[sys_code][
            "system_full_name"] + f" - {release_version} 05:45:00"
        load_last_build_info(notion_info, sys_code)
        desc = build_build_ticket_content(notion_info, sys_code)
        print(f"create build ticket, sys_code[{sys_code}]release_version[{release_version}]title[{title}]desc[{desc}]")
        build_ticket_issue_key = JiraUtil.create_build_ticket(title, desc, release_version)
        notion_info[sys_code]["build_ticket_issue_key"] = build_ticket_issue_key
        print("build ticket create success, issue.key[" + str(build_ticket_issue_key) + "]")


def update_build_ticket_link_to_notion(notion_info):
    for sysCode in notion_info.keys():
        for page_id in notion_info[sysCode]["notion_pages_id"]:
            print(
                f"update build ticket link to notion, page_id[{page_id}][{notion_info[sysCode]["build_ticket_issue_key"]}]")
            print(NotionUtil.update_build_ticket(page_id,
                                                 notion_info[sysCode]["build_ticket_issue_key"]))


def merge_release_to_main(notionInfo):
    for sysCode in notionInfo.keys():
        GitUtil.merge_and_push(systemBaseInfo[sysCode]["repo_path"], notionInfo[sysCode]["release_branch"], "main")


if __name__ == '__main__':
    notion_info = get_release_notion_info()

    # create MR for check is ticket merged
    checkTicketHasMerged(notion_info)

    createReleaseBranch(notion_info)

    # 等gitlab create好pipeline
    time.sleep(30)
    check_pipeline_process(notion_info)

    load_release_mr_url(notion_info)

    create_build_ticket(notion_info)

    update_build_ticket_link_to_notion(notion_info)

    merge_release_to_main(notion_info)
