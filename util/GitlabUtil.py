import requests
from datetime import datetime

headers = {
    'PRIVATE-TOKEN': 'glpat-PDfSzcSAg3aPHxZZrPyi'
}
noDeleteBranchs = ["dev","main","staging"]

projectMap = {
    "IIDS": 531
    ,"IIMS-HKTV" : 528
    ,"IIMS-LM" : 865
    ,"Notification" : 818
}

def getProjectId(projectCode):
    if projectCode not in projectMap:
        raise KeyError(f"projectCode[{projectCode}] not found in projectMap")
    return projectMap[projectCode]

def getBranches(projectId):
    response = requests.get(f"https://ite-git01.hktv.com.hk/api/v4/projects/{projectId}/repository/branches", headers=headers)
    return response.json()

def createBranches(projectId, fromBranch, toBranch):
    response = requests.post(f"https://ite-git01.hktv.com.hk/api/v4/projects/{projectId}/repository/branches?branch={toBranch}&ref={fromBranch}", headers=headers)
    return response.json()

def deleteBranch(projectId, branch_name):
    print(f'delete branch {projectId} - {branch_name}')
    # response = requests.delete("https://ite-git01.hktv.com.hk/api/v4/projects/{projectId}/repository/branches/{branch_name}", headers=headers)
    # return response.json()

def getMergeRequest(status):
    response = requests.get(f"https://ite-git01.hktv.com.hk/api/v4/merge_requests?state={status}", headers=headers)
    return response.json()

def createMergeRequest(projectId, frombranch, toBranch, title, description):
    merge_request_data = {
        "source_branch": frombranch,
        "target_branch": toBranch,
        "title": title,
        "description": description,
    }
    response = requests.post(f"https://ite-git01.hktv.com.hk/api/v4/projects/{projectId}/merge_requests", json=merge_request_data, headers=headers)
    # {'id': 33344, 'iid': 140, 'project_id': 531, 'title': 'title', 'description': 'desc', 'state': 'opened',
    #  'created_at': '2023-11-01T10:15:10.400Z', 'updated_at': '2023-11-01T10:15:10.400Z', 'merged_by': None,
    #  'merge_user': None, 'merged_at': None, 'closed_by': None, 'closed_at': None, 'target_branch': 'main',
    #  'source_branch': 'feature/MS-2687', 'user_notes_count': 0, 'upvotes': 0, 'downvotes': 0,
    #  'author': {'id': 379, 'username': 'willycheng', 'name': 'TW - IT - BE - Willy Cheng', 'state': 'active',
    #             'locked': False,
    #             'avatar_url': 'https://ite-git01.hktv.com.hk/uploads/-/system/user/avatar/379/avatar.png',
    #             'web_url': 'https://ite-git01.hktv.com.hk/willycheng'}, 'assignees': [], 'assignee': None,
    #  'reviewers': [], 'source_project_id': 531, 'target_project_id': 531, 'labels': [], 'draft': False,
    #  'work_in_progress': False, 'milestone': None, 'merge_when_pipeline_succeeds': False, 'merge_status': 'checking',
    #  'detailed_merge_status': 'preparing', 'sha': '590804c44a3e2dcc8bcd674671084c2b0cf478f9', 'merge_commit_sha': None,
    #  'squash_commit_sha': None, 'discussion_locked': None, 'should_remove_source_branch': None,
    #  'force_remove_source_branch': None, 'prepared_at': None, 'reference': '!140',
    #  'references': {'short': '!140', 'relative': '!140', 'full': 'hktv/tw/shoalter_ecommerce/inventory/ids!140'},
    #  'web_url': 'https://ite-git01.hktv.com.hk/hktv/tw/shoalter_ecommerce/inventory/ids/-/merge_requests/140',
    #  'time_stats': {'time_estimate': 0, 'total_time_spent': 0, 'human_time_estimate': None,
    #                 'human_total_time_spent': None}, 'squash': False, 'squash_on_merge': False,
    #  'task_completion_status': {'count': 0, 'completed_count': 0}, 'has_conflicts': False,
    #  'blocking_discussions_resolved': True, 'approvals_before_merge': None, 'subscribed': True, 'changes_count': None,
    #  'latest_build_started_at': None, 'latest_build_finished_at': None, 'first_deployed_to_production_at': None,
    #  'pipeline': None, 'head_pipeline': None, 'diff_refs': None, 'merge_error': None, 'user': {'can_merge': True}}
    return response.json()

def getMergeRequest(projectId, iid):
    response = requests.get(f"https://ite-git01.hktv.com.hk/api/v4/projects/{projectId}/merge_requests/{iid}", headers=headers)
    return response.json()

def approveMergeRequest(projectId, iid):
    response = requests.post(f"https://ite-git01.hktv.com.hk/api/v4/projects/{projectId}/merge_requests/{iid}/approve", headers=headers)
    return response.json()

def mergeMergeRequest(projectId, iid):
    response = requests.put(f"https://ite-git01.hktv.com.hk/api/v4/projects/{projectId}/merge_requests/{iid}/merge", headers=headers)
    return response.json()

def getDiffDays(dateStr):
    target_date = datetime.strptime(dateStr, '%Y-%m-%dT%H:%M:%S.%f%z')

    # Get the current date and time
    current_date = datetime.now(target_date.tzinfo)

    # Calculate the difference in days
    time_difference = current_date - target_date
    return time_difference.days

def deleteOutDateBranch():
    projectIdList = [
        531, #IIDS
        528, #IIMS-HKTV
        865, #IIMS-UUID
        818, #message center
        975, #Address-service
        971 #Order-service
    ]

    mrs = getMergeRequest('opened')
    openedMrBranch = []
    for mr in mrs:
        openedMrBranch.append(mr["target_branch"])
        openedMrBranch.append(mr["source_branch"])

    for projectId in projectIdList:
        branches = getBranches(projectId)
        
        for branch in branches:
            if branch["name"] in noDeleteBranchs or str(branch["name"]).startswith("release") or branch["name"] in openedMrBranch:
                continue
            
            if getDiffDays(branch["commit"]["committed_date"]) > 90:
                deleteBranch(projectId, branch["name"])

# if __name__ == '__main__':
    # print(createMergeRequest(531, "feature/MS-2687", "main", "title", "desc"))
    # print(approveMergeRequest(865, 44))
    # print(getMergeRequest(865, 44))
    # print(mergeMergeRequest(865, 44))