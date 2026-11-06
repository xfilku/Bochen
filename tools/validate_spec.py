"""Check documentation links, M0 references and the JSON Schema subset in examples.

This is a documentation check, not an application test or a full OpenAPI validator.
It uses only the Python standard library. Run from any working directory.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs/contracts/openapi-m0.json"
SPEC = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
ERRORS: list[str] = []


def resolve(pointer: str):
    if not pointer.startswith("#/"):
        raise ValueError(f"Unsupported external reference: {pointer}")
    value = SPEC
    for part in pointer[2:].split("/"):
        value = value[part.replace("~1", "/").replace("~0", "~")]
    return value


def walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def matches(value, schema: dict) -> bool:
    """Evaluate the keywords used by this repository's example schemas only."""
    if "$ref" in schema and not matches(value, resolve(schema["$ref"])):
        return False
    if "allOf" in schema and not all(matches(value, s) for s in schema["allOf"]):
        return False
    if "anyOf" in schema and not any(matches(value, s) for s in schema["anyOf"]):
        return False
    if "not" in schema and matches(value, schema["not"]):
        return False
    if "if" in schema:
        branch = "then" if matches(value, schema["if"]) else "else"
        if branch in schema and not matches(value, schema[branch]):
            return False
    if "const" in schema and value != schema["const"]:
        return False
    if "enum" in schema and value not in schema["enum"]:
        return False
    kind = schema.get("type")
    checks = {
        "object": lambda: isinstance(value, dict),
        "array": lambda: isinstance(value, list),
        "string": lambda: isinstance(value, str),
        "integer": lambda: isinstance(value, int) and not isinstance(value, bool),
        "boolean": lambda: isinstance(value, bool),
        "null": lambda: value is None,
    }
    if kind is not None and (kind not in checks or not checks[kind]()):
        return False
    if isinstance(value, dict):
        props = schema.get("properties", {})
        if any(key not in value for key in schema.get("required", [])):
            return False
        if len(value) < schema.get("minProperties", 0):
            return False
        if schema.get("additionalProperties") is False and value.keys() - props.keys():
            return False
        if any(key in props and not matches(item, props[key]) for key, item in value.items()):
            return False
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", float("inf")):
            return False
        if "items" in schema and not all(matches(item, schema["items"]) for item in value):
            return False
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", float("inf")):
            return False
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            return False
        try:
            if schema.get("format") == "date":
                if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
                    return False
                date.fromisoformat(value)
            if schema.get("format") == "date-time":
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if "T" not in value or parsed.utcoffset() is None:
                    return False
        except ValueError:
            return False
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", -float("inf")) or value > schema.get("maximum", float("inf")):
            return False
    return True


def main() -> int:
    documents = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    for path in documents:
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            target = target.strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z]+://", target, re.I):
                continue
            if not (path.parent / unquote(target)).resolve().exists():
                ERRORS.append(f"Missing link in {path.name}: {target}")
        for char in content:
            if char in "\u200b\u200c\u200d\u2060\ufeff\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069":
                ERRORS.append(f"Unexpected invisible control in {path.name}: U+{ord(char):04X}")
                break

    for node in walk(SPEC):
        if "$ref" in node:
            try:
                resolve(node["$ref"])
            except (ValueError, KeyError) as exc:
                ERRORS.append(f"Invalid reference: {exc}")

    test_text = (ROOT / "docs/07-testy.md").read_text(encoding="utf-8")
    known_tests = set(re.findall(r"^\| ([AUISP]\d{2}) \|", test_text, re.M))
    endpoint_text = (ROOT / "docs/05-routery-endpointy.md").read_text(encoding="utf-8")
    ids = set()
    count = 0
    for path, item in SPEC["paths"].items():
        for method, operation in item.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            count += 1
            operation_id = operation["operationId"]
            if operation_id in ids:
                ERRORS.append(f"Duplicate operationId: {operation_id}")
            ids.add(operation_id)
            if operation_id not in endpoint_text:
                ERRORS.append(f"Operation missing from endpoint plan: {operation_id}")
            expected = set(re.findall(r"\{([^}]+)\}", path))
            actual = {p["name"] for p in operation.get("parameters", []) if p["in"] == "path" and p.get("required")}
            if expected != actual:
                ERRORS.append(f"Path parameters do not match: {path}")
            for test in operation.get("x-test-ids", []):
                if test not in known_tests:
                    ERRORS.append(f"Unknown test {test} in {operation_id}")
            if path != "/health" and operation.get("security", SPEC.get("security")) != [{"ApiKeyAuth": []}]:
                ERRORS.append(f"Missing API key protection: {operation_id}")
            if "204" in operation["responses"] and "content" in operation["responses"]["204"]:
                ERRORS.append(f"204 response has body: {operation_id}")

    examples = json.loads((ROOT / "docs/examples/m0-requests.json").read_text(encoding="utf-8"))
    for example in examples:
        if not matches(example["value"], SPEC["components"]["schemas"][example["schema"]]):
            ERRORS.append(f"Invalid positive example: {example['name']}")

    invalid_examples = [
        ("CustomerUpdate", {}),
        ("CustomerUpdate", {"display_name": None}),
        ("CustomerCreate", {"display_name": "Anna", "phone": "500600700", "status": "confirmed"}),
        ("OrderCreate", {"customer_id": 1, "bake_id": 1}),
        ("OrderCreate", {"customer_id": 1, "bake_id": 1, "items": [], "extra_items": []}),
        ("OrderReplace", {"items": [{"bake_product_id": 1, "quantity": 2}]}),
        ("OrderItemInput", {"bake_product_id": 1, "quantity": True}),
        ("OrderItemInput", {"bake_product_id": 1, "quantity": "2"}),
        ("OrderExtraItemInput", {"description": "Ziemniaki", "quantity": "0.000", "unit": "kg"}),
        ("OrderExtraItemInput", {"description": "Jabłka", "quantity": "1.5", "unit": "piece"}),
        ("OrderExtraItemInput", {"description": "Ziemniaki", "quantity": 10, "unit": "kg"}),
        ("BakeCreate", {"name": "Piątek", "bake_date": "2030-11-22", "accepting_from": "2030-11-20T12:00:00", "order_deadline": "2030-11-21T17:00:00Z"}),
    ]
    for name, value in invalid_examples:
        if matches(value, SPEC["components"]["schemas"][name]):
            ERRORS.append(f"Invalid example unexpectedly accepted by {name}: {value}")

    task_text = (ROOT / "docs/06-plan-implementacji.md").read_text(encoding="utf-8")
    task_ids = re.findall(r"^### (T\d{2})\.", task_text, re.M)
    if task_ids != [f"T{i:02}" for i in range(1, 32)]:
        ERRORS.append("Expected exactly T01-T31 in implementation plan")
    for line in task_text.splitlines():
        if line.startswith("- Testy:"):
            for test in re.findall(r"\b[AUISP]\d{2}\b", line):
                if test not in known_tests:
                    ERRORS.append(f"Unknown test in task plan: {test}")

    cases = json.loads((ROOT / "docs/examples/parser-cases.json").read_text(encoding="utf-8"))
    for case in cases:
        for test in case["tests"]:
            if test not in known_tests:
                ERRORS.append(f"Unknown test in parser case {case['id']}: {test}")

    if ERRORS:
        for error in ERRORS:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(documents)} Markdown documents; {count} operations; {len(SPEC['components']['schemas'])} schemas.")
    print(f"OK: local links, references, authentication declarations, {len(task_ids)} task IDs and {len(known_tests)} test IDs.")
    print(f"OK: {len(examples)} positive examples, {len(invalid_examples)} negative examples and {len(cases)} parser cases linked to tests.")
    print("This checks documentation only. Application tests have not been implemented or run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
