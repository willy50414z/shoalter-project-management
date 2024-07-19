import javalang
from javalang.parser import JavaSyntaxError
from javalang.tree import MethodDeclaration, ClassDeclaration, CompilationUnit


def get_java_structure(java_class_file_path):
    with open(java_class_file_path, 'r', encoding='utf-8') as file:
        java_code = file.read()
    try:
        return javalang.parse.parse(java_code)
    except JavaSyntaxError as e:
        print(f"can't analyze java code, file[{java_class_file_path}]")
        return None


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