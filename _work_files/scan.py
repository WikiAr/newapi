import ast
import re
from pathlib import Path


def process_python_file(path: Path) -> bool:
    """
    Remove function name from logger messages inside each function.
    Returns True if file was modified.
    """
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    tree = ast.parse(source)

    modified = False

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        func_name = node.name

        # AST line numbers are 1-based
        start = node.lineno - 1
        end = (node.end_lineno or start) - 1

        for i in range(start, end + 1):
            line = lines[i]

            if "logger." not in line:
                continue

            # Remove function name if it appears as a standalone word
            new_line = re.sub(
                rf"\b{re.escape(func_name)}\b",
                "",
                line,
            )

            # Preserve indentation exactly
            indent = len(new_line) - len(new_line.lstrip(" "))
            body = new_line[indent:]
            body = re.sub(r" {2,}", " ", body)
            new_line = " " * indent + body

            if new_line != line:
                lines[i] = new_line
                modified = True

    if modified:
        path.write_text("\n".join(lines), encoding="utf-8")

    return modified


def process_directory(root: Path):
    """
    Walk through all .py files and process them.
    """
    for py_file in root.rglob("*.py"):
        try:
            if process_python_file(py_file):
                print(f"Modified: {py_file}")
        except SyntaxError:
            # Skip files with invalid syntax
            print(f"Skipped (syntax error): {py_file}")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent / "newapi"
    process_directory(project_root)
