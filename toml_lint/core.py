import re
from dataclasses import dataclass
from typing import Any, List, Union

from tree_sitter import Node, Tree
from tree_sitter_languages import get_language, get_parser

# https://github.com/hukkin/tomli#building-a-tomlitomllib-compatibility-layer
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore


TRANSFORM_REGEX = re.compile(r"\(at\sline\s\d+,")
ERROR_FORMAT_REGEX = re.compile(r"^(.+)\(at\sline\s(\d+),\scolumn\s(\d+)\)$")


@dataclass
class Position:
    line: int
    column: int


@dataclass
class ErrorNodeLintedItem:
    start_postion: Position
    message: str


def get_toml_tree(toml_text: str) -> Tree:
    parser = get_parser("toml")
    tree = parser.parse(bytes(toml_text, "utf8"))
    return tree


def get_error_nodes(tree: Tree) -> List[Node]:
    nodes: List[Node] = []

    language = get_language("toml")
    query = language.query("[(ERROR) @error]")
    captures = query.captures(tree.root_node)
    for c in captures:
        nodes.append(c[0])

    return nodes


def get_pair_node_by_recursive_up(node: Node) -> Node:
    res: List[Node] = []
    orig_node = node

    def f(node: Node):
        if node.parent is None:
            return res.append(orig_node)
        if node.parent is not None:
            if node.parent.type == "pair":
                return res.append(node.parent)
        f(node.parent)

    f(node)

    return res[0]


def transform_real_line_messages(errors: List[ErrorNodeLintedItem]) -> List[str]:
    res: List[str] = []

    for error in errors:
        line = error.start_postion.line + 1
        message = error.message
        res.append(TRANSFORM_REGEX.sub(f"(at line {line},", message))

    return res


def execute_lint_for_full(toml_text: str) -> Union[Any, None]:
    try:
        tomllib.loads(toml_text)
    except Exception as e:
        return e.args[0]
    else:
        return None


def execute_lint_for_error_nodes(nodes: List[Node]):
    items: List[ErrorNodeLintedItem] = []

    for node in nodes:
        try:
            r = get_pair_node_by_recursive_up(node)
            text = str(r.text.decode())
            tomllib.loads(text)
        except Exception as e:
            item = ErrorNodeLintedItem(
                start_postion=Position(
                    line=node.start_point[0], column=node.start_point[1]
                ),
                message=e.args[0],
            )
            items.append(item)

    return items


def sort_messages(messages: List[str]) -> List[str]:
    res: List[str] = []

    list_of_list_for_sorting: List[List[Any]] = []
    for message in messages:
        m = ERROR_FORMAT_REGEX.match(message)
        if m:
            line = int(m[2])
            column = int(m[3])
            list_of_list_for_sorting.append([line, column, message])

    sorted_list_of_list = sorted(list_of_list_for_sorting)

    for s in sorted_list_of_list:
        res.append(s[2])

    return res


def uniq_sort_messages(messages: List[str]):
    conved_sets = set(messages)
    conved_list = list(conved_sets)
    sorted_list = sort_messages(conved_list)
    return sorted_list


def print_plain_message(messages: List[str], display_filename: str) -> None:
    for message in messages:
        m = ERROR_FORMAT_REGEX.match(message)
        if m:
            msg = m[1]
            line = m[2]
            column = m[3]
            output = f"{display_filename}:{line}:{column} error: {msg}"
            print(output)


def lint(toml_text: str, display_filename: str) -> None:
    full_linted_message: Union[str, None] = execute_lint_for_full(toml_text)

    tree = get_toml_tree(toml_text)
    error_nodes = get_error_nodes(tree)
    error_linted_items = execute_lint_for_error_nodes(error_nodes)
    transformed_messages = transform_real_line_messages(error_linted_items)

    merged: List[str] = []
    merged.extend(transformed_messages)
    if full_linted_message:
        merged.append(full_linted_message)

    completed = uniq_sort_messages(merged)

    print_plain_message(completed, display_filename)
