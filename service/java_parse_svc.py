import json
import os
import subprocess

import javalang
from javalang.parser import JavaSyntaxError
from javalang.tree import MethodDeclaration, ClassDeclaration, CompilationUnit

ANNOTATION_KEY_METHOD_PATH = "methodPath"
ANNOTATION_KEY_REMARK = "remark"
ANNOTATION_LIST = ["EcomRevampServiceMigration", "EcomRevampServiceMigrationSrc", "EcomRevampControllerMigration"]


def get_java_file_info(file_path):
    result = subprocess.run(
        ['java', '-jar', f"{os.getcwd()}/libs/JavaParser.jar", file_path],
        capture_output=True,  # Captures stdout and stderr
        text=True  # Converts byte output to strings
    )
    try:
        if len(result.stdout) > 0:
            return json.loads(result.stdout)
        else:
            return {}
    except Exception as e:
        print(f"parse response to json fail, source[{result.stdout}]")
        raise e


def get_java_structure(java_class_file_path):
    with open(java_class_file_path, 'r', encoding='utf-8') as file:
        java_code = file.read()
    if "case WEIGHT_UNIT_KG -> totalWeight + weightOfProduct;" in java_code:
        java_code = java_code.replace("        totalWeight =", "")
        java_code = java_code.replace("switch (weightUnitOfProduct) {", "")
        java_code = java_code.replace("case WEIGHT_UNIT_KG -> totalWeight + weightOfProduct;", "")
        java_code = java_code.replace("case WEIGHT_UNIT_G, WEIGHT_UNIT_ML -> totalWeight + (weightOfProduct / 1000);",
                                      "")
        java_code = java_code.replace("case WEIGHT_UNIT_OZ -> totalWeight + (weightOfProduct * 0.0283495231);", "")
        java_code = java_code.replace("case WEIGHT_UNIT_PD -> totalWeight + (weightOfProduct * 0.45359237);", "")
        java_code = java_code.replace("default -> totalWeight;", "")
        java_code = java_code.replace("};", "")
    if "case \"CREDIT_CARD\" -> PaymentType.PAYMENT_TYPE_CREDIT_CARD;" in java_code:
        java_code = java_code.replace("return switch (paymentTypeCode) {\n"
                                      + "      case \"CREDIT_CARD\" -> PaymentType.PAYMENT_TYPE_CREDIT_CARD;\n"
                                      + "      case \"PAYME\" -> PaymentType.PAYMENT_TYPE_PAYME;\n"
                                      + "      case \"PAYPAL\" -> PaymentType.PAYMENT_TYPE_PAYPAL;\n"
                                      + "      case \"UNIONPAY\" -> PaymentType.PAYMENT_TYPE_UNIONPAY;\n"
                                      + "      case \"POS\" -> PaymentType.PAYMENT_TYPE_POS;\n"
                                      + "      case \"CITI_COBRAND\" -> PaymentType.PAYMENT_TYPE_CITI_COBRAND;\n"
                                      + "      case \"VISA\" -> PaymentType.PAYMENT_TYPE_VISA;\n"
                                      + "      case \"MASTER\" -> PaymentType.PAYMENT_TYPE_MASTER;\n"
                                      + "      case \"AMEX\" -> PaymentType.PAYMENT_TYPE_AMEX;\n"
                                      + "      case \"OCTOPUS\" -> PaymentType.PAYMENT_TYPE_OCTOPUS;\n"
                                      + "      case \"ALIPAYHK\" -> PaymentType.PAYMENT_TYPE_ALIPAYHK;\n"
                                      + "      case \"WECHATPAY\" -> PaymentType.PAYMENT_TYPE_WECHATPAY;\n"
                                      + "      case \"BOCPAY\" -> PaymentType.PAYMENT_TYPE_BOCPAY;\n"
                                      + "      case \"UPQR\" -> PaymentType.PAYMENT_TYPE_UPQR;\n"
                                      + "      case \"ATOME\" -> PaymentType.PAYMENT_TYPE_ATOME;\n"
                                      + "      case \"MCQR\" -> PaymentType.PAYMENT_TYPE_MCQR;\n"
                                      + "      case \"JCB\" -> PaymentType.PAYMENT_TYPE_JCB;\n"
                                      + "      case \"MPAY\" -> PaymentType.PAYMENT_TYPE_MPAY;\n"
                                      + "      case \"APPLEPAY\" -> PaymentType.PAYMENT_TYPE_APPLEPAY;\n"
                                      + "      case \"MFOOD\" -> PaymentType.PAYMENT_TYPE_MFOOD;\n"
                                      + "      default -> PaymentType.PAYMENT_TYPE_UNKNOWN;\n"
                                      + "    };", "return null;")
    java_code = java_code.replace("String[]::new", "")
    java_code = java_code.replace("\"CREDIT_CARD\"::equalsIgnoreCase", "")
    java_code = java_code.replace("\"success\"::equals", "")
    java_code = java_code.replace(".class::", "")
    java_code = java_code.replace("()::", "")
    java_code = java_code.replace("::", "")

    java_code = java_code.replace("if (entry instanceof CartEntryModelDto childEntry) {",
                                  "if (entry instanceof CartEntryModelDto) {")
    # java_code = java_code.replace("::", "")
    try:
        return javalang.parse.parse(java_code)
    except JavaSyntaxError as e:
        print(f"can't analyze java code, file[{java_class_file_path}]")
        return None


def find_method_by_line_number(java_file_info, line_number):
    method_list = java_file_info["methodList"]
    for method in method_list:
        if int(method["range"]["start"]) <= int(line_number) <= int(method["range"]["end"]):
            return method
    # raise FileNotFoundError(f"[find_method_by_line_number]can't find method, line_number[{line_number}]java_file_info[{java_file_info}]")


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
