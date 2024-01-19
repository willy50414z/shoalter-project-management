import sys

from util import NotionUtil, GitlabUtil

#ARGV (systemCode)[all system] (date)[next date]
releaseDateStr = sys.argv[1]

systemCode = ""
if len(sys.argv) > 2:
    systemCode = sys.argv[2]

buildTicketTitleMap = {
    "Notification" : "Shoalter - Production Build - Merchant Notification System"
    ,"IIDS" : "Shoalter - Production Build - Share Stock IIDS (Intracompany Inventory Distribution system)"
    ,"IIMS-HKTV" : "Shoalter - Production Build - Share Stock HKTVmall IIMS (Intracompany Inventory Management System)"
    ,"IIMS-LM" : "Shoalter - Production Build - Share Stock LittleMall IIMS (Intracompany Inventory Management System)"
}

#[Notion] get release tickets[IIDS/IIMS/IIMS-LM/Notification/Address/Order]
releaseNotionItemList = NotionUtil.findByReleaseDate(releaseDateStr)
# for item in releaseNotionItemList:
#     print(item.notionItem["properties"]["Project"])
print(len(releaseNotionItemList))
if len(systemCode) > 0:
    sysNameList = systemCode.split(",")
    releaseNotionItemList = [item for item in releaseNotionItemList if item.getProjectName() in sysNameList]

print(len(releaseNotionItemList))

#[GIT] create release branch from staging
for item in releaseNotionItemList:
    gitlabProjectId = GitlabUtil.getProjectId(item.getProjectName());
    releaseBranchRes = GitlabUtil.createBranches(gitlabProjectId, "staging", "release/" + releaseDateStr.replace("-", "") + "_0545")
    branchName = releaseBranchRes["name"]
    commitSha = releaseBranchRes["commit"]["id"]

#[GIT] merge to main branch
    #create MR
    mrRes = GitlabUtil.createMergeRequest(gitlabProjectId, "staging", "main", "Merge request to main branch for creating build ticket", "Merge request to main branch for creating build ticket")
    print(f"approveMergeRequest response[{mrRes}]")
    mrIid = mrRes["iid"]

    #approve and merge MR
    print(f"approveMergeRequest response[{GitlabUtil.approveMergeRequest(gitlabProjectId, mrIid)}]")
    print(f"mergeMergeRequest response[{GitlabUtil.mergeMergeRequest(gitlabProjectId, mrIid)}]")

#[GIT] wait argo CI complete and get MR url
#[JIRA] get lastest JIRA build ticket
#[JIRA] create build ticket

