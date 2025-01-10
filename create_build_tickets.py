import sys
import time
import json
from util import NotionUtil, GitlabUtil, JiraUtil, maven_util
from service.git_svc import GitService

class BuildTicketService:
    system_base_info = {
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
        , "IIMS": {"project_id": 528,
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
    stage_id = 0
    create_raw_build_ticket_stage_id = 999


    def is_skip_this_stage(self, notion_info, sys_code, stage_id):
        if notion_info[sys_code] is None or notion_info[sys_code]["stage_id"] > stage_id:
            return True
        else:
            notion_info[sys_code]["stage_id"] = stage_id
            return False


    def update_process(self, sys_code, notion_info, exception):
        notion_info[sys_code]["error_msg"] = str(exception)
        # 保留這個會一直抓到舊的MR
        if "toStagingMrIid" in notion_info[sys_code]:
            del notion_info[sys_code]["toStagingMrIid"]
        for page_id in notion_info[sys_code]["notion_pages_id"]:
            print(
                f"update exception message to notion, sys_code[{sys_code}]page_id[{page_id}]message[{exception}]")
            print(NotionUtil.update_build_ticket(page_id, json.dumps(notion_info[sys_code])))
        notion_info[sys_code] = None

    def build_notion_item_info(self, sys_code, notionItem, notionItemInfo):
        ticketLink = notionItem["properties"]["Ticket"]["url"]
        if sys_code not in notionItemInfo:
            notionItemInfo[sys_code] = {"stage_id": self.stage_id}
            notionItemInfo[sys_code]["tickets"] = []
            notionItemInfo[sys_code]["notion_pages_id"] = []
        notionItemInfo[sys_code]["tickets"].append(ticketLink)
        notionItemInfo[sys_code]["release_date"] = notionItem["properties"]["ReleaseDate"]["select"]["name"]
        notionItemInfo[sys_code]["notion_pages_id"].append(notionItem["id"])
        return notionItemInfo

    def get_release_notion_info(self, release_date):
        releaseNotionItemList = NotionUtil.findByReleaseDateIsAndBuildTicketIsEmpty(release_date)
        notionItemInfo = {}
        not_complete_sys = []

        for notionItem in releaseNotionItemList:
            sys_code = notionItem["properties"]["System"]["select"]["name"]
            if sys_code != 'HYBRIS':
                if notionItem["properties"]["BuildTicket"]["url"] and notionItem["properties"]["BuildTicket"]["url"].startswith(NotionUtil.jira_url_prefix):
                    continue
                elif notionItem["properties"]["BuildTicket"]["url"]:
                    completeRatio = notionItem["properties"]["CompleteRatio"]["rollup"]["number"]
                    if completeRatio is not None and completeRatio < 1 or sys_code in not_complete_sys:
                        not_complete_sys.append(sys_code)
                        notionItemInfo[sys_code] = None
                        print("task is not completed, sys_code[" + sys_code + "]ticketLink[" +
                              notionItem["properties"]["Ticket"]["url"] + "]")
                    else:
                        build_ticket_info = json.loads(notionItem["properties"]["BuildTicket"]["url"])
                        if build_ticket_info["stage_id"] == self.create_raw_build_ticket_stage_id:
                            notionItemInfo[sys_code] = self.build_notion_item_info(sys_code, notionItem, notionItemInfo)[sys_code]
                            notionItemInfo[sys_code]["build_ticket_issue_key"] = build_ticket_info["build_ticket_issue_key"]
                        else:
                            notionItemInfo[sys_code] = build_ticket_info
                else:
                    notionItemInfo[sys_code] = self.build_notion_item_info(sys_code, notionItem, notionItemInfo)[sys_code]

        return notionItemInfo


    # for item in releaseNotionItemList:
    #     print(item.notionItem["properties"]["Project"])
    # if len(systemCode) > 0:
    #     sysCodeAr = systemCode.split(",")
    #     releaseNotionItemList = [item for item in releaseNotionItemList if item.getProjectName() in sysCodeAr]
    #
    # print(len(releaseNotionItemList))
    #

    def check_ticket_has_merged(self, notion_info):
        # create feature branch to staging的MR，看看是否有change，應該要是0
        for sys_code in notion_info.keys():
            if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                continue
            try:
                print(f"check has feature branch merged to staging, sysCode[{sys_code}]")
                projectId = self.system_base_info[sys_code]["project_id"]
                for jiraUrl in notion_info[sys_code]["tickets"]:
                    issueKey = jiraUrl.split("browse/")[1]
                    mrRes = GitlabUtil.createMergeRequest(projectId, "feature/" + issueKey, "staging",
                                                          "Merge request to staging for check has ticket merged",
                                                          "Merge request to staging for check has ticket merged")
                    if "toStagingMrIid" not in notion_info[sys_code]:
                        notion_info[sys_code]["toStagingMrIid"] = []
                    if "iid" in mrRes:
                        notion_info[sys_code]["toStagingMrIid"].append(mrRes["iid"])
                    elif mrRes["message"][0].startswith("Another open merge request already exists"):
                        notion_info[sys_code]["toStagingMrIid"].append(
                            mrRes["message"][0][mrRes["message"][0].find("!") + 1:])
                    else:
                        raise ValueError(
                            f"response is unexpect, mrRes[{mrRes}]")
            except Exception as e:
                self.update_process(sys_code, notion_info, e)
        # 睡個5秒等gitlab整理一下訊息
        print("wait 10 seconds for gitlab create merge request")
        time.sleep(10)

        # 撈MR看看change是不是0
        for sys_code in notion_info.keys():
            if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                continue
            try:
                projectId = self.system_base_info[sys_code]["project_id"]
                for mrIid in notion_info[sys_code]["toStagingMrIid"]:
                    mrRes = GitlabUtil.getMergeRequest(projectId, mrIid)
                    # 有沒有問題都close check branch
                    GitlabUtil.closeMergeRequest(projectId, mrIid)
                    if mrRes["changes_count"] is not None:
                        raise ValueError(
                            f"feature branch is not merge to staging, feature branch[{mrRes["source_branch"]}]MR[{mrRes["web_url"]}]")
                    print(f"feature branch merged to staging check completed, sysCode[{sys_code}], mrIid[{mrIid}]")
            except Exception as e:
                self.update_process(sys_code, notion_info, e)


    def create_release_branch(self, notion_info, release_date):
        for sys_code in notion_info.keys():
            if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                continue
            try:
                if sys_code not in self.system_base_info or "project_id" not in self.system_base_info[sys_code]:
                    raise ValueError("can't find gitlab project id, sysCode[" + sys_code + "]")
                releaseVersion = notion_info[sys_code]["release_date"]
                release_branch_name = "release/" + releaseVersion.replace("-", "") + "_0545"
                print(f"create release branch, sysCode[{sys_code}]branch_name[{release_branch_name}]")

                # //*****
                if GitlabUtil.is_branch_exists(self.system_base_info[sys_code]["project_id"], release_branch_name):
                    print(f"Branch already exists, delete branch and re-create")
                    GitlabUtil.delete_branch(self.system_base_info[sys_code]["project_id"], release_branch_name)

                gitService = GitService(self.system_base_info[sys_code]["repo_path"])
                # gitService.delete_and_checkout("staging")
                gitService.create_branch("staging", release_branch_name)
                maven_util.update_maven_property(self.system_base_info[sys_code]["repo_path"],
                                                 "shoalter-infra-grpc-proto.version",
                                                 f"release-{release_date.replace("-", "")}_0545")
                gitService.commit_and_push("update shoalter infra grpc version", release_branch_name)
                notion_info[sys_code]["release_branch"] = release_branch_name
                notion_info[sys_code]["sha"] = gitService.get_head_sha()
                # **********

                # releaseBranchRes = GitlabUtil.createBranches(self.system_base_info[sys_code]["project_id"], "staging",
                #                                              release_branch_name)
                # print(f"response[{releaseBranchRes}]")
                #
                # if "message" in releaseBranchRes and 'Branch already exists' == releaseBranchRes["message"]:
                #     print(f"Branch already exists, delete branch and re-create")
                #     releaseBranchRes = GitlabUtil.delete_branch(self.system_base_info[sys_code]["project_id"],
                #                                                 release_branch_name)
                #     print(f"delete release branch response[{releaseBranchRes}]")
                #     releaseBranchRes = GitlabUtil.createBranches(self.system_base_info[sys_code]["project_id"], "staging",
                #                                                  release_branch_name)
                #     print(
                #         f"re-create release branch, sysCode[{sys_code}]branch_name[{release_branch_name}]response[{releaseBranchRes}]")
                # notion_info[sys_code]["release_branch"] = release_branch_name
                # notion_info[sys_code]["sha"] = releaseBranchRes["commit"]["id"]


            except Exception as e:
                self.update_process(sys_code, notion_info, e)

    def check_pipeline_process(self, notion_info):
        # get pipeline id
        for sys_code in notion_info.keys():
            if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                continue
            try:
                projectId = self.system_base_info[sys_code]["project_id"]
                waitTime = 0
                while "pipeline_id" not in notion_info[sys_code]:
                    pipelineRsList = GitlabUtil.getPipelinesByProjectId(projectId)
                    for pipeineRes in pipelineRsList:
                        if pipeineRes["sha"] == notion_info[sys_code]["sha"] and pipeineRes["ref"] == notion_info[sys_code][
                            "release_branch"]:
                            if pipeineRes["status"] == 'created' or pipeineRes["status"] == "running":
                                notion_info[sys_code]["pipeline_id"] = pipeineRes["id"]
                                break
                            else:
                                print(f"pipeline status is not in ('created', 'running') sha[{pipeineRes["sha"]}]ref[{pipeineRes["ref"]}]status[{pipeineRes["status"]}]")
                    waitTime += 1
                    if waitTime > 6:
                        raise ValueError("can't find release branch pipeline")
                    print(f"wait 10 second for {sys_code} pipeline created, wait times[{waitTime}]")
                    time.sleep(10)
            except Exception as e:
                self.update_process(sys_code, notion_info, e)

        # check pipeline status
        allPipelineComplete = False
        pipeline_fail_systems = []
        job_retry_map = {}
        while not allPipelineComplete:
            allPipelineComplete = True
            for sys_code in notion_info.keys():
                if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                    continue
                try:
                    projectId = self.system_base_info[sys_code]["project_id"]
                    pipId = notion_info[sys_code]["pipeline_id"]
                    pipelineJobsRes = GitlabUtil.getPipelineJobsByProjectIdAndPipId(projectId, pipId)
                    pipelineJobsRes = sorted(pipelineJobsRes, key=lambda job: job["id"])
                    for jobInfo in pipelineJobsRes:
                        if jobInfo["status"] != "success" and jobInfo["status"] != "failed":
                            print(f"{sys_code} is {jobInfo["status"]} in {jobInfo["name"]}")
                            allPipelineComplete = False
                            break
                        elif jobInfo["status"] == "failed":
                            fail_job_id = jobInfo['id']
                            if fail_job_id in job_retry_map and job_retry_map[fail_job_id] > 5:
                                pipeline_fail_systems.append(sys_code)
                                print(
                                    f"release branch pipeline failed, skip this project, sysCode[{sys_code}]pipeline url[{jobInfo["web_url"]}]")
                            else:
                                job_retry_map[fail_job_id] = job_retry_map[fail_job_id] + 1 if fail_job_id in job_retry_map else 1
                                GitlabUtil.retry_job(projectId, fail_job_id)
                            break
                        elif jobInfo["status"] == "success" and "create merge request" in str(jobInfo["name"]):
                            notion_info[sys_code]["create_release_mr_job_id"] = jobInfo["id"]
                            break
                except Exception as e:
                    self.update_process(sys_code, notion_info, e)
            for pipeline_fail_system in pipeline_fail_systems:
                print(f"*****************{pipeline_fail_system} pipeline fail, remove from build systems*****************")
                notion_info.pop(pipeline_fail_system)
            # 60秒檢查一次
            print("======wait 60 seconds for next check======")
            time.sleep(60)


    def load_release_mr_url(self, notion_info):
        for sys_code in notion_info.keys():
            if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                continue
            try:
                print(f"load release mr url, sysCode[{sys_code}]")
                projectId = self.system_base_info[sys_code]["project_id"]
                createReleaseMrJobId = notion_info[sys_code]["create_release_mr_job_id"]
                jobLog = GitlabUtil.getPipelineJobLogByProjectIdAndJobId(projectId, createReleaseMrJobId)
                releaseMrRes = json.loads(jobLog[jobLog.find("{"):jobLog.rfind("}") + 1])
                notion_info[sys_code]["release_mr_url"] = releaseMrRes["web_url"]
            except Exception as e:
                self.update_process(sys_code, notion_info, e)


    def load_last_build_info(self, notion_info, sys_code):
        ticket = JiraUtil.get_last_build_ticket(self.system_base_info[sys_code]["system_full_name"])
        desc = ticket[0].fields.description

        lastRevisionInfoStr = desc[desc.find("Revision:") + 10:desc.rfind("System update:") - 2].replace("\n    \n  ", "")
        if "\n    Tag: " in  lastRevisionInfoStr:
            lastRevisionInfoAr = lastRevisionInfoStr.split("\n    Tag: ")
        elif "\nTag: " in  lastRevisionInfoStr:
            lastRevisionInfoAr = lastRevisionInfoStr.split("\nTag: ")
        else:
            raise ValueError(f"can't get correct lastRevisionInfo, lastRevisionInfo[{lastRevisionInfoStr}]")
        notion_info[sys_code]["last_revision"] = lastRevisionInfoAr[0]
        notion_info[sys_code]["last_tag"] = lastRevisionInfoAr[1]


    def build_build_ticket_content(self, notion_info, sys_code):
        buildTicketDesc = self.buildTicketDescTemplate
        buildTicketDesc = buildTicketDesc.replace("${gitlab_url}", self.system_base_info[sys_code]["gitlab_url"])
        buildTicketDesc = buildTicketDesc.replace("${mr_url}", notion_info[sys_code]["release_mr_url"])
        buildTicketDesc = buildTicketDesc.replace("${release_branch}", notion_info[sys_code]["release_branch"])
        buildTicketDesc = buildTicketDesc.replace("${release_sha}", notion_info[sys_code]["sha"])
        buildTicketDesc = buildTicketDesc.replace("${domain}", "" if "domain" not in self.system_base_info[sys_code] else
        self.system_base_info[sys_code]["domain"])
        buildTicketDesc = buildTicketDesc.replace("${fallback_sha}", notion_info[sys_code]["last_revision"])
        buildTicketDesc = buildTicketDesc.replace("${fallback_branch}", notion_info[sys_code]["last_tag"])
        feature_tickets = ""
        for ticket in notion_info[sys_code]["tickets"]:
            feature_tickets += "[" + ticket + "|" + ticket + "|smart-link]\r\n"
        feature_tickets = feature_tickets[:len(feature_tickets) - 2]
        buildTicketDesc = buildTicketDesc.replace("${feature_tickets}", feature_tickets)
        return buildTicketDesc


    def update_build_ticket(self, notion_info):
        for sys_code in notion_info.keys():
            if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                continue
            try:
                release_version = notion_info[sys_code]["release_date"]
                title = "Shoalter - Production Build - " + self.system_base_info[sys_code][
                    "system_full_name"] + f" - {release_version} 05:45:00"
                self.load_last_build_info(notion_info, sys_code)
                desc = self.build_build_ticket_content(notion_info, sys_code)
                # print(
                #     f"create build ticket, sys_code[{sys_code}]release_version[{release_version}]title[{title}]desc[{desc}]")
                build_ticket_issue_key = JiraUtil.update_build_ticket(notion_info[sys_code]["build_ticket_issue_key"], title, desc, release_version)
                print("build ticket create success, issue.key[" + str(build_ticket_issue_key) + "]")
            except Exception as e:
                self.update_process(sys_code, notion_info, e)


    def update_raw_build_ticket_info_to_notion(self, notion_info):
        for sys_code in notion_info.keys():
            try:
                if notion_info[sys_code] and notion_info[sys_code]["notion_pages_id"]:
                    for page_id in notion_info[sys_code]["notion_pages_id"]:
                        notion_info[sys_code]["stage_id"] = self.create_raw_build_ticket_stage_id
                        print(
                            f"update build ticket link to notion, page_id[{page_id}][{notion_info[sys_code]["build_ticket_issue_key"]}]")
                        print(f"response[{NotionUtil.update_build_ticket(page_id, json.dumps(notion_info[sys_code]))}]")
            except Exception as e:
                self.update_process(sys_code, notion_info, e)

    def update_build_ticket_link_to_notion(self, notion_info):
        for sys_code in notion_info.keys():
            if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                continue
            try:
                for page_id in notion_info[sys_code]["notion_pages_id"]:
                    print(
                        f"update build ticket link to notion, page_id[{page_id}][{notion_info[sys_code]["build_ticket_issue_key"]}]")
                    print(f"response[{NotionUtil.update_build_ticket(page_id,
                                                                     NotionUtil.jira_url_prefix + str(
                                                                         notion_info[sys_code]["build_ticket_issue_key"]))}]")
            except Exception as e:
                self.update_process(sys_code, notion_info, e)


    def merge_release_to_main(self, notion_info):
        for sys_code in notion_info.keys():
            if self.is_skip_this_stage(notion_info, sys_code, self.stage_id):
                continue
            try:
                print(f"merge branch to main, sys_code[{sys_code}] from branch[{notion_info[sys_code]["release_branch"]}]")
                GitService(self.system_base_info[sys_code]["repo_path"]).merge_and_push(notion_info[sys_code]["release_branch"],
                                       "main")
            except Exception as e:
                self.update_process(sys_code, notion_info, e)

    def create_raw_build_ticket(self, notion_info):
        for sys_code in notion_info.keys():
            if notion_info[sys_code] is not None and "build_ticket_issue_key" not in notion_info[sys_code]:
                release_version = notion_info[sys_code]["release_date"]
                title = "Shoalter - Production Build - " + self.system_base_info[sys_code][
                    "system_full_name"] + f" - {release_version} 05:45:00"
                build_ticket_issue_key = JiraUtil.create_build_ticket(title, "waiting for update", release_version)
                notion_info[sys_code]["build_ticket_issue_key"] = build_ticket_issue_key.key

    def create_raw_ticket(self, release_date):
        notion_info = self.get_release_notion_info(release_date)

        self.create_raw_build_ticket(notion_info)

        self.update_raw_build_ticket_info_to_notion(notion_info)
        
    def update_build_ticket_info(self, release_date):
        notion_info = self.get_release_notion_info(release_date)
        self.stage_id += 1
        # order = notion_info["order-service"]
        # notion_info = {}
        # notion_info["order-service"] = order
        if len(notion_info) == 0:
            print("no system need to create build ticket")
            return

        # create MR for check is ticket merged
        self.check_ticket_has_merged(notion_info)
        self.stage_id += 1

        self.create_release_branch(notion_info, release_date)
        self.stage_id += 1

        # 等gitlab create好pipeline
        # time.sleep(30)
        self.check_pipeline_process(notion_info)
        self.stage_id += 1

        self.load_release_mr_url(notion_info)
        self.stage_id += 1

        self.update_build_ticket(notion_info)
        self.stage_id += 1

        self.update_build_ticket_link_to_notion(notion_info)
        self.stage_id += 1

        self.merge_release_to_main(notion_info)


if __name__ == '__main__':
    releaseDate = "2025-01-13"
    bt_svc = BuildTicketService()
    # bt_svc.create_raw_ticket(releaseDate)
    bt_svc.update_build_ticket_info(releaseDate)

    # maven_util.update_maven_property(BuildTicketService().system_base_info["order-service"]["repo_path"],
    #                                  "shoalter-infra-grpc-proto.version",
    #                                  f"release-20250113_0545")
    # gitService = GitService("E:/Code/shoalter-ecommerce-business/shoalter-ecommerce-business-cart-service/")
    # gitService.repo.git.push("origin")
    # print(GitlabUtil.getBranches(BuildTicketService().system_base_info["address-service"]["project_id"]))


