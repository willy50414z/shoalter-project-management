import configparser
import urllib

import requests
from datetime import datetime
from urllib.parse import quote
config = configparser.ConfigParser()
config.read('application.ini')
headers = {
    'PRIVATE-TOKEN': config["DEFAULT"]["gitlab_token"]
}
noDeleteBranchs = ["dev", "main", "staging"]

domain="https://ite-git01.hktv.com.hk"

projectMap = {
    "IIDS": 531
    , "IIMS-HKTV": 528
    , "IIMS-LM": 865
    , "Notification": 818
}


def getProjectId(projectCode):
    if projectCode not in projectMap:
        raise KeyError(f"projectCode[{projectCode}] not found in projectMap")
    return projectMap[projectCode]

def get_branch(project_id, branch_name):
    return requests.get(f"{domain}/api/v4/projects/{project_id}/repository/branches/{urllib.parse.quote_plus(branch_name)}",
                             headers=headers)

def getBranches(projectId):
    response = requests.get(f"{domain}/api/v4/projects/{projectId}/repository/branches",
                            headers=headers)
    return response.json()


def createBranches(projectId, fromBranch, toBranch):
    response = requests.post(
        f"{domain}/api/v4/projects/{projectId}/repository/branches?branch={toBranch}&ref={fromBranch}",
        headers=headers)
    return response.json()


def delete_branch(project_id, branch_name):
    response = requests.delete(
        f"{domain}/api/v4/projects/{project_id}/repository/branches/{branch_name.replace("/", "%2F")}", headers=headers)
    return response

def get_cicd_variable(project_id, var_name):
    response = requests.delete(
        f"{domain}/api/v4/projects/{project_id}/variables/{var_name}", headers=headers)
    return response

def getMergeRequestByStatus(status):
    response = requests.get(f"{domain}/api/v4/merge_requests?state={status}", headers=headers)
    return response.json()


def createMergeRequest(projectId, frombranch, toBranch, title, description):
    merge_request_data = {
        "source_branch": frombranch,
        "target_branch": toBranch,
        "title": title,
        "description": description,
    }
    response = requests.post(f"{domain}/api/v4/projects/{projectId}/merge_requests",
                             json=merge_request_data, headers=headers)
    return response.json()


def getMergeRequest(projectId, iid):
    response = requests.get(f"{domain}/api/v4/projects/{projectId}/merge_requests/{iid}",
                            headers=headers)
    return response.json()


def closeMergeRequest(projectId, iid):
    response = requests.put(f"{domain}/api/v4/projects/{projectId}/merge_requests/{iid}",
                            headers=headers, data={"state_event": "close"})
    return response.json()


def approveMergeRequest(projectId, iid):
    response = requests.post(f"{domain}/api/v4/projects/{projectId}/merge_requests/{iid}/approve",
                             headers=headers)
    return response.json()


def mergeMergeRequest(projectId, iid):
    response = requests.put(f"{domain}/api/v4/projects/{projectId}/merge_requests/{iid}/merge",
                            headers=headers)
    return response.json()


def getPipelinesByProjectId(projectId):
    response = requests.get(f"{domain}/api/v4/projects/{projectId}/pipelines", headers=headers)
    return response.json()


def getPipelineJobsByProjectIdAndPipId(projectId, pipId):
    response = requests.get(f"{domain}/api/v4/projects/{projectId}/pipelines/{pipId}/jobs",
                            headers=headers)
    return response.json()

def retry_job(projectId, jobId):
    response = requests.post(f"{domain}/api/v4/projects/{projectId}/jobs/{jobId}/retry",
                            headers=headers)
    return response.json()


def getPipelineJobLogByProjectIdAndJobId(projectId, jobId):
    response = requests.get(f"{domain}/api/v4/projects/{projectId}/jobs/{jobId}/trace",
                            headers=headers)
    return str(response.content)


def getDiffDays(dateStr):
    target_date = datetime.strptime(dateStr, '%Y-%m-%dT%H:%M:%S.%f%z')

    # Get the current date and time
    current_date = datetime.now(target_date.tzinfo)

    # Calculate the difference in days
    time_difference = current_date - target_date
    return time_difference.days


def is_branch_exists(project_id, branch_name):
    response = get_branch(project_id, branch_name)
    if response.status_code == 200:
        print(f"Branch '{branch_name}' exists in project '{project_id}'.")
        return True
    elif response.status_code == 404:
        print(f"Branch '{branch_name}' does NOT exist in project '{project_id}'.")
        return False
    else:
        print(f"Failed to check branch. Status Code: {response.status_code}, Response: {response.text}")
        return False

# def deleteOutDateBranch():
# projectIdList = [
#     531, #IIDS
#     528, #IIMS-HKTV
#     865, #IIMS-UUID
#     818, #message center
#     975, #Address-service
#     971 #Order-service
# ]
#
# mrs = getMergeRequest('opened')
# openedMrBranch = []
# for mr in mrs:
#     openedMrBranch.append(mr["target_branch"])
#     openedMrBranch.append(mr["source_branch"])
#
# for projectId in projectIdList:
#     branches = getBranches(projectId)
#
#     for branch in branches:
#         if branch["name"] in noDeleteBranchs or str(branch["name"]).startswith("release") or branch["name"] in openedMrBranch:
#             continue
#
#         if getDiffDays(branch["commit"]["committed_date"]) > 90:
#             deleteBranch(projectId, branch["name"])

# if __name__ == '__main__':
# print(createMergeRequest(531, "feature/MS-2687", "main", "title", "desc"))
# print(approveMergeRequest(865, 44))
# print(getMergeRequest(865, 44))
# print(mergeMergeRequest(865, 44))
