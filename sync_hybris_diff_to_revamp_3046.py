import json
import os

from javalang.tree import *
import javalang

from util import GitUtil

branch_name = "POC/check_revamp_3046"
repo_path = "E:/Code/hktv-hybris"

def get_branch_diff(repo_path, branch_name):
    diff_info = []
    commits = GitUtil.get_branch_commits(repo_path, branch_name)
    for commit in commits:
        if "HYBRIS-3189" in commit.message:
            return diff_info
        else:
            commit_diff_info = {"sha": commit.hexsha, "parent_sha": commit.parents[0].hexsha,
                                "committed_date": commit.committed_date}
            commit_diff_info.update(GitUtil.get_commit_diff(repo_path, commit))
            diff_info.append(commit_diff_info)


def get_java_structure(java_class_file_path):
    with open(java_class_file_path, 'r', encoding='utf-8') as file:
        java_code = file.read()
    return javalang.parse.parse(java_code)


def find_method_by_line_number(java_class_structure, line_number):
    # [0] package
    # [1] import
    # [2] package
    method_list = java_class_structure.children[len(java_class_structure.children) - 1][0].methods

    lastMethod = None
    for method in method_list:
        if method.position[0] > int(line_number):
            break
        lastMethod = method
    return lastMethod


def _find_method_by_line_number(node, line_number):
    if node is None:
        return None
    if isinstance(node, MethodDeclaration):
        if line_number < node.position[0]:
            return True
    if isinstance(node, ClassDeclaration) or isinstance(node, CompilationUnit):
        for child_node in node.children:
            result = _find_method_by_line_number(child_node, line_number)
            if result:
                return result
    elif isinstance(node, list):
        lasNode = None
        for child_node in node:
            result = _find_method_by_line_number(child_node, line_number)
            if result and isinstance(result, bool):
                return lasNode
            elif result:
                return result
            else:
                lasNode = child_node
    return None


def get_revamp_related_info(method):
    revamp_paths = []
    remark = ""
    for ann in method.annotations:
        if "EcomRevampServiceMigration" == ann.name:
            for annotation_var in ann.element:
                if "methodPath" == annotation_var.name:
                    for anno_value_entity in annotation_var.value.values:
                        revamp_paths.append(anno_value_entity.value[1:len(anno_value_entity.value) - 1])
                elif "remark" == annotation_var.name:
                    remark = annotation_var.value.value

    result = {}
    if len(revamp_paths) > 0:
        result["related_method"] = revamp_paths
    if len(remark) > 0:
        result["remark"] = remark
    return result


def get_revamp_related_change_list(commit_diff, repo_dir):
    change_list = []
    for key, value in commit_diff.items():
        if "sha" != key and "parent_sha" != key and key.endswith(".java") and not key.endswith("/ThirdPartyLoginPageController.java"):
            file_path = repo_dir + "/" + key
            # change to parent sha
            GitUtil.reset(repo_dir, commit_diff["parent_sha"])
            print(f"start analyze changed file, sha[{commit_diff["parent_sha"]}]file_path[{file_path}]")
            java_structure = get_java_structure(file_path)
            for line_num in value:
                # find method info
                method = find_method_by_line_number(java_structure, line_num)
                if method:
                    revamp_related_info = get_revamp_related_info(method)
                    if len(revamp_related_info) > 0:
                        change_list.append({key + ":" + line_num: revamp_related_info})
    return change_list


if __name__ == '__main__':
    # get_java_structure("C:/work/hybris_docker/hybris_docker_hktvmall/bin/ext-hktv/hktvstorefront/web/src/hk/com/hktv/storefront/controllers/pages/ThirdPartyLoginPageController.java")


    branch_diff = get_branch_diff(repo_path, branch_name)
    print(f"hybris branch[{branch_name}]commits size[{len(branch_diff)}]diff lines[{str(branch_diff)}]")

    revamp_related_change_summary = []
    for commit_diff in branch_diff:
        revamp_related_change_list = get_revamp_related_change_list(commit_diff, repo_path)
        revamp_related_change_summary.append(
            {"sha": commit_diff["sha"], "committed_date": commit_diff["committed_date"],
             "revamp_related_info_list": revamp_related_change_list})
    revamp_related_change_summary = sorted(revamp_related_change_summary,
                                           key=lambda x: x["committed_date"], reverse=True)

    branch_change_summary = {}
    for revamp_related_change in revamp_related_change_summary:
        sha = revamp_related_change["sha"]
        for changeRow in revamp_related_change["revamp_related_info_list"]:
            file_path = list(changeRow.keys())[0]
            if file_path not in branch_change_summary:
                branch_change_summary[file_path] = {}
                branch_change_summary[file_path]["sha"] = [sha]
                branch_change_summary[file_path]["related_method"] = changeRow[file_path]["related_method"]
            else:
                branch_change_summary[file_path]["sha"].append(sha)

    output_json = json.dumps({"branch": branch_name, "commits_change_summary": revamp_related_change_summary,
                              "branch_change_summary": branch_change_summary},
                             ensure_ascii=False, indent=4)
    print(output_json)
