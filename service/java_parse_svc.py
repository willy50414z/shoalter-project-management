import json
import os

from util import cmd_util

ANNOTATION_KEY_METHOD_PATH = "methodPath"
ANNOTATION_KEY_REMARK = "remark"
ANNOTATION_LIST = ["EcomRevampServiceMigration", "EcomRevampServiceMigrationSrc", "EcomRevampControllerMigration"]


def get_java_file_info(file_path):

    try:
        result = cmd_util.exec(['java', '-jar', f"{os.getcwd()}/libs/JavaParser.jar", file_path])
    except Exception as e:
        print(f"parse java file fail, file_path[{file_path}]")
        raise e
    try:
        if len(result) > 0:
            return json.loads(result)
        else:
            return {}
    except Exception as e:
        print(f"parse response to json fail, source[{result}]")
        raise e



def find_method_by_line_number(java_file_info, line_number):
    method_list = java_file_info["methodList"]
    for method in method_list:
        if int(method["range"]["start"]) <= int(line_number) <= int(method["range"]["end"]):
            return method
    # raise FileNotFoundError(f"[find_method_by_line_number]can't find method, line_number[{line_number}]java_file_info[{java_file_info}]")




def get_revamp_file_anno_info(matching_files):
    anno_info = []
    for has_anno_file in matching_files:
        java_structure = get_java_file_info(has_anno_file)
        method_list = java_structure["methodList"]
        for method in method_list:
            method_anno_info = get_revamp_method_anno_info(method)
            if len(method_anno_info) > 0:
                anno_info.append(method_anno_info)
    return anno_info


def get_revamp_method_anno_info(method):
    anno_info = {}
    methodPaths = []
    for annotation in method["annotationList"]:
        if annotation["name"] in ANNOTATION_LIST:
            if ANNOTATION_KEY_METHOD_PATH in annotation["attrs"]:
                anno_info[ANNOTATION_KEY_METHOD_PATH] = annotation["attrs"][ANNOTATION_KEY_METHOD_PATH]
            if ANNOTATION_KEY_REMARK in annotation["attrs"]:
                anno_info[ANNOTATION_KEY_REMARK] = annotation["attrs"][ANNOTATION_KEY_REMARK]
    return anno_info

