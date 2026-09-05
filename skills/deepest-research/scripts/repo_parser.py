#!/usr/bin/env python3
"""Index Python symbols and local import dependencies for a repository.

The parser is static and records parse failures instead of executing imported
code. Hidden, cache, dependency, and virtual-environment directories are skipped.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


METHOD = {
    "name": "static repository symbol and dependency index",
    "source": "ML-Bench: Evaluating Large Language Models and Agents for Machine Learning Tasks on Repository-Level Code",
}

SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", "node_modules", "venv", ".venv", "env", "dist", "build"}


def name_of(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{name_of(node.value)}.{node.attr}".lstrip(".")
    try:
        return ast.unparse(node)
    except Exception:
        return type(node).__name__


def parse_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text, filename=str(path))
    encoded = text.encode("utf-8")
    result: dict[str, Any] = {
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "utf8_bytes": len(encoded),
        "line_count": len(text.splitlines()),
        "imports": [],
        "classes": [],
        "functions": [],
        "globals": [],
    }
    for node in tree.body:
        if isinstance(node, ast.Import):
            result["imports"].extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            result["imports"].append(node.module or "")
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({
                "name": node.name,
                "line": node.lineno,
                "bases": [name_of(base) for base in node.bases],
                "methods": [
                    {"name": child.name, "line": child.lineno, "args": [arg.arg for arg in child.args.args]}
                    for child in node.body
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                ],
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append({
                "name": node.name,
                "line": node.lineno,
                "args": [arg.arg for arg in node.args.args],
            })
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            result["globals"].extend(
                {"name": target.id, "line": node.lineno}
                for target in targets
                if isinstance(target, ast.Name)
            )
    return result


def module_name(relative_path: str) -> str:
    path = relative_path[:-3] if relative_path.endswith(".py") else relative_path
    parts = Path(path).parts
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_repository(root_dir: str | Path) -> dict[str, Any]:
    root = Path(root_dir).resolve()
    if not root.is_dir():
        raise ValueError(f"Repository root is not a directory: {root}")
    repository_index: dict[str, Any] = {}
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS)
        for filename in sorted(files):
            if not filename.endswith(".py"):
                continue
            path = Path(current) / filename
            relative = path.relative_to(root).as_posix()
            try:
                repository_index[relative] = parse_file(path)
            except (OSError, SyntaxError) as exc:
                repository_index[relative] = {"error": str(exc)}

    modules = {module_name(path): path for path in repository_index}
    edges = []
    for source, data in repository_index.items():
        if "error" in data:
            continue
        for imported in data["imports"]:
            candidates = [module for module in modules if imported == module or imported.startswith(module + ".")]
            if candidates:
                target_module = max(candidates, key=len)
                target = modules[target_module]
                if target != source:
                    edges.append({"source": source, "target": target, "import": imported, "type": "local_import"})
    repository_digest = hashlib.sha256()
    for relative in sorted(repository_index):
        repository_digest.update(relative.encode("utf-8"))
        repository_digest.update(b"\0")
        path = root / relative
        try:
            repository_digest.update(path.read_bytes())
        except OSError:
            repository_digest.update(str(repository_index[relative].get("error", "")).encode("utf-8"))

    return {
        "tool": "repo_parser",
        "method": METHOD,
        "runtime_class": "static repository preprocessor",
        "root": str(root),
        "repository_sha256": repository_digest.hexdigest(),
        "scope": {
            "languages": ["Python"],
            "included_pattern": "**/*.py",
            "skipped_directories": sorted(SKIP_DIRS),
            "execution_policy": "project code is parsed but never imported or executed",
        },
        "module_count": len(repository_index),
        "parse_error_count": sum("error" in data for data in repository_index.values()),
        "repository_structure": repository_index,
        "dependency_graph_edges": sorted(edges, key=lambda row: (row["source"], row["target"], row["import"])),
        "limitations": "Static imports and AST symbols do not establish runtime call paths or behavior.",
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Create a static Python repository symbol and dependency index.")
    p.add_argument("root", nargs="?", type=Path, help="Repository directory.")
    p.add_argument("--output", type=Path, default=Path("repo_dependency_index.json"))
    p.add_argument("--fail-on-parse-error", action="store_true")
    p.add_argument("--demo", action="store_true", help="Parse the script directory containing this file.")
    return p


def main() -> int:
    args = parser().parse_args()
    root = Path(__file__).resolve().parent if args.demo else args.root
    if root is None:
        raise SystemExit("Provide ROOT or --demo.")
    try:
        report = parse_repository(root)
    except (OSError, ValueError) as exc:
        print(f"repo_parser: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(args.output), "modules": report["module_count"], "parse_errors": report["parse_error_count"]}))
    if args.fail_on_parse_error and report["parse_error_count"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
