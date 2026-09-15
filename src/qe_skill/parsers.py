"""Bounded deterministic parsers for untrusted M1 project evidence."""

from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NoReturn, cast

import yaml
from pydantic import Field, JsonValue
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

from qe_skill.domain import Artifact, Digest, Ref
from qe_skill.inventory import InventoryEntry

PARSER_VERSION: Literal["1.0"] = "1.0"
HTTP_METHODS = ("delete", "get", "head", "options", "patch", "post", "put", "trace")
REMOTE_REF = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:)?//")


@dataclass(frozen=True)
class ParserLimits:
    max_bytes: int = 2 * 1024 * 1024
    max_depth: int = 64
    max_records: int = 10_000

    def __post_init__(self) -> None:
        if self.max_bytes < 1 or self.max_depth < 1 or self.max_records < 1:
            raise ValueError("Parser limits must be positive.")


class SourceSpan(Artifact):
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    column_start: int | None = Field(default=None, ge=0)
    column_end: int | None = Field(default=None, ge=0)
    symbol: str | None = None


class ExtractionRecord(Artifact):
    source: Ref
    source_hash: Digest
    kind: Literal[
        "heading",
        "paragraph",
        "list_item",
        "code_fence",
        "structured_value",
        "openapi_operation",
        "openapi_parameter",
        "openapi_response",
        "openapi_schema",
        "openapi_security",
        "python_module",
        "python_class",
        "python_function",
        "python_async_function",
        "python_import",
        "python_decorator",
        "project_model_record",
    ]
    location: str = Field(min_length=1)
    span: SourceSpan | None = None
    name: str | None = None
    text: str = Field(min_length=1)
    attributes: dict[str, JsonValue] = Field(default_factory=dict)
    extraction_method: str = Field(min_length=1)
    interpretation: Literal["explicit", "structural", "heuristic", "unresolved"]
    inferred: bool
    confidence: float = Field(ge=0, le=1)


class ParseResult(Artifact):
    source: Ref
    source_hash: Digest | None = None
    source_type: str = Field(min_length=1)
    parser: str = Field(min_length=1)
    parser_version: Literal["1.0"] = PARSER_VERSION
    status: Literal["PARSED", "PARTIAL", "FAILED", "UNSUPPORTED", "MUTATED"]
    extractions: list[ExtractionRecord]
    issues: list[str]


class ParseFailure(ValueError):
    pass


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def _source_ref(entry: InventoryEntry) -> Ref:
    return Ref(id=entry.id, project_id=entry.project_id, snapshot_id=entry.snapshot_id)


def _record_id(entry: InventoryEntry, kind: str, location: str, name: str | None) -> str:
    payload = f"{entry.id}\0{kind}\0{location}\0{name or ''}".encode()
    return f"extraction.{hashlib.sha256(payload).hexdigest()[:24]}"


def _span(
    entry: InventoryEntry,
    identifier: str,
    line_start: int,
    line_end: int,
    column_start: int | None = None,
    column_end: int | None = None,
    symbol: str | None = None,
) -> SourceSpan:
    return SourceSpan(
        id=f"span.{identifier.removeprefix('extraction.')}",
        project_id=entry.project_id,
        snapshot_id=entry.snapshot_id,
        line_start=line_start,
        line_end=line_end,
        column_start=column_start,
        column_end=column_end,
        symbol=symbol,
    )


def _record(
    entry: InventoryEntry,
    *,
    kind: str,
    location: str,
    text: str,
    line_start: int | None = None,
    line_end: int | None = None,
    column_start: int | None = None,
    column_end: int | None = None,
    symbol: str | None = None,
    name: str | None = None,
    attributes: dict[str, JsonValue] | None = None,
    method: str,
    interpretation: str = "structural",
    inferred: bool = False,
    confidence: float = 1.0,
) -> ExtractionRecord:
    identifier = _record_id(entry, kind, location, name)
    return ExtractionRecord.model_validate(
        {
            "id": identifier,
            "project_id": entry.project_id,
            "snapshot_id": entry.snapshot_id,
            "source": _source_ref(entry).model_dump(),
            "source_hash": entry.content_hash,
            "kind": kind,
            "location": location,
            "span": _span(
                entry,
                identifier,
                line_start,
                line_end if line_end is not None else line_start,
                column_start,
                column_end,
                symbol,
            ).model_dump()
            if line_start is not None
            else None,
            "name": name,
            "text": text,
            "attributes": attributes or {},
            "extraction_method": method,
            "interpretation": interpretation,
            "inferred": inferred,
            "confidence": confidence,
        }
    )


def _failure(entry: InventoryEntry, status: str, parser: str, issue: str) -> ParseResult:
    return ParseResult.model_validate(
        {
            "id": f"parse.{entry.id.removeprefix('source.')}",
            "project_id": entry.project_id,
            "snapshot_id": entry.snapshot_id,
            "source": _source_ref(entry).model_dump(),
            "source_hash": entry.content_hash,
            "source_type": entry.source_type,
            "parser": parser,
            "status": status,
            "extractions": [],
            "issues": [issue],
        }
    )


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise ParseFailure("JSON contains a duplicate object key.")
        output[key] = value
    return output


def _reject_constant(value: str) -> NoReturn:
    raise ParseFailure(f"Non-finite JSON number is forbidden: {value}")


def _check_yaml_nodes(root: Node, limits: ParserLimits) -> None:
    pending: list[tuple[Node, int]] = [(root, 0)]
    seen: set[int] = set()
    count = 0
    while pending:
        node, depth = pending.pop()
        if depth > limits.max_depth:
            raise ParseFailure("YAML nesting exceeds the configured parser depth.")
        identity = id(node)
        if identity in seen:
            continue
        seen.add(identity)
        count += 1
        if count > limits.max_records:
            raise ParseFailure("YAML node count exceeds the configured parser limit.")
        if isinstance(node, MappingNode):
            keys: set[tuple[str, str]] = set()
            for key, value in node.value:
                if not isinstance(key, ScalarNode):
                    raise ParseFailure("Complex YAML mapping keys are unsupported.")
                identity_key = (key.tag, key.value)
                if identity_key in keys:
                    raise ParseFailure("YAML contains a duplicate mapping key.")
                keys.add(identity_key)
                pending.extend(((key, depth + 1), (value, depth + 1)))
        elif isinstance(node, SequenceNode):
            pending.extend((child, depth + 1) for child in node.value)


def _bounded_value(value: object, limits: ParserLimits) -> JsonValue:
    pending: list[tuple[object, int]] = [(value, 0)]
    count = 0
    while pending:
        current, depth = pending.pop()
        count += 1
        if depth > limits.max_depth:
            raise ParseFailure("Structured data nesting exceeds the configured parser depth.")
        if isinstance(current, dict):
            if not all(isinstance(key, str) for key in current):
                raise ParseFailure("Structured object keys must be strings.")
            pending.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            pending.extend((item, depth + 1) for item in current)
        elif isinstance(current, dt.date | dt.datetime):
            raise ParseFailure(
                "Implicit YAML timestamp values are unsupported; quote them to preserve text."
            )
        elif current is not None and not isinstance(current, str | int | float | bool):
            raise ParseFailure("Structured data contains an unsupported value type.")
        if count > limits.max_records:
            raise ParseFailure("Structured record count exceeds the configured parser limit.")
    return value  # type: ignore[return-value]


def _pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _structured_records(
    entry: InventoryEntry, value: JsonValue, method: str, line_count: int, limits: ParserLimits
) -> list[ExtractionRecord]:
    records: list[ExtractionRecord] = []
    pending: list[tuple[str, JsonValue]] = [("", value)]
    while pending:
        pointer, current = pending.pop()
        if isinstance(current, dict):
            for key in sorted(current, reverse=True):
                pending.append((f"{pointer}/{_pointer(key)}", current[key]))
        elif isinstance(current, list):
            for index in range(len(current) - 1, -1, -1):
                pending.append((f"{pointer}/{index}", current[index]))
        else:
            location = pointer or "/"
            text = json.dumps(current, ensure_ascii=False, sort_keys=True)
            records.append(
                _record(
                    entry,
                    kind="structured_value",
                    location=location,
                    text=text,
                    line_start=1,
                    line_end=max(line_count, 1),
                    attributes={"value": current},
                    method=method,
                    interpretation="explicit",
                )
            )
        if len(records) > limits.max_records:
            raise ParseFailure("Structured extraction count exceeds the configured parser limit.")
    return records


def _markdown_records(entry: InventoryEntry, text: str, markdown: bool) -> list[ExtractionRecord]:
    lines = text.splitlines()
    records: list[ExtractionRecord] = []
    paragraph_start: int | None = None
    paragraph_lines: list[str] = []
    fence_start: int | None = None
    fence_marker: str | None = None

    def flush_paragraph(end: int) -> None:
        nonlocal paragraph_start, paragraph_lines
        if paragraph_start is not None:
            records.append(
                _record(
                    entry,
                    kind="paragraph",
                    location=f"lines:{paragraph_start}-{end}",
                    text="\n".join(paragraph_lines),
                    line_start=paragraph_start,
                    line_end=end,
                    method="markdown-structure" if markdown else "text-structure",
                )
            )
        paragraph_start = None
        paragraph_lines = []

    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if markdown and fence_marker is not None:
            if stripped.startswith(fence_marker):
                records.append(
                    _record(
                        entry,
                        kind="code_fence",
                        location=f"lines:{fence_start}-{number}",
                        text=f"Fenced code block lines {fence_start}-{number}",
                        line_start=fence_start,
                        line_end=number,
                        attributes={"closed": True},
                        method="markdown-structure",
                    )
                )
                fence_marker = None
                fence_start = None
            continue
        fence = re.match(r"^\s*(`{3,}|~{3,})", line) if markdown else None
        if fence:
            flush_paragraph(number - 1)
            fence_marker = fence.group(1)[0] * len(fence.group(1))
            fence_start = number
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line) if markdown else None
        item = re.match(r"^\s*(?:[-+*]|\d+[.)])\s+(.+?)\s*$", line)
        if heading:
            flush_paragraph(number - 1)
            title = heading.group(2)
            explicit_id = re.search(r"\s+\{#([^}]+)\}\s*$", title)
            if explicit_id:
                title = title[: explicit_id.start()].rstrip()
            records.append(
                _record(
                    entry,
                    kind="heading",
                    location=f"line:{number}",
                    text=title,
                    line_start=number,
                    line_end=number,
                    name=title,
                    attributes={
                        "level": len(heading.group(1)),
                        "explicit_id": explicit_id.group(1) if explicit_id else None,
                    },
                    method="markdown-structure",
                )
            )
        elif item:
            flush_paragraph(number - 1)
            records.append(
                _record(
                    entry,
                    kind="list_item",
                    location=f"line:{number}",
                    text=item.group(1),
                    line_start=number,
                    line_end=number,
                    method="markdown-structure" if markdown else "text-structure",
                )
            )
        elif not stripped:
            flush_paragraph(number - 1)
        else:
            paragraph_start = paragraph_start or number
            paragraph_lines.append(line)
    flush_paragraph(len(lines))
    if fence_marker is not None and fence_start is not None:
        records.append(
            _record(
                entry,
                kind="code_fence",
                location=f"lines:{fence_start}-{len(lines)}",
                text=f"Unclosed fenced code block from line {fence_start}",
                line_start=fence_start,
                line_end=max(len(lines), fence_start),
                attributes={"closed": False},
                method="markdown-structure",
                interpretation="unresolved",
                confidence=1.0,
            )
        )
    return records


def _decorator_text(node: ast.expr) -> str:
    return ast.unparse(node)


def _python_records(entry: InventoryEntry, text: str) -> list[ExtractionRecord]:
    tree = ast.parse(text, filename=entry.path, mode="exec", type_comments=True)
    records = [
        _record(
            entry,
            kind="python_module",
            location=entry.path,
            text=entry.path,
            line_start=1,
            line_end=max(len(text.splitlines()), 1),
            name=entry.path,
            method="python-ast",
            interpretation="explicit",
        )
    ]
    parents: list[str] = []

    class Visitor(ast.NodeVisitor):
        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            qualified = ".".join([*parents, node.name])
            records.append(
                _record(
                    entry,
                    kind="python_class",
                    location=f"symbol:{qualified}",
                    text=ast.get_source_segment(text, node) or node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    column_start=node.col_offset,
                    column_end=node.end_col_offset,
                    symbol=qualified,
                    name=node.name,
                    attributes={"bases": [ast.unparse(base) for base in node.bases]},
                    method="python-ast",
                    interpretation="explicit",
                )
            )
            self._decorators(node.decorator_list, qualified)
            parents.append(node.name)
            self.generic_visit(node)
            parents.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._function(node, "python_function")

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._function(node, "python_async_function")

        def _function(
            self,
            node: ast.FunctionDef | ast.AsyncFunctionDef,
            kind: Literal["python_function", "python_async_function"],
        ) -> None:
            qualified = ".".join([*parents, node.name])
            records.append(
                _record(
                    entry,
                    kind=kind,
                    location=f"symbol:{qualified}",
                    text=ast.get_source_segment(text, node) or node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    column_start=node.col_offset,
                    column_end=node.end_col_offset,
                    symbol=qualified,
                    name=node.name,
                    attributes={
                        "signature": ast.unparse(node.args),
                        "returns": ast.unparse(node.returns) if node.returns else None,
                    },
                    method="python-ast",
                    interpretation="explicit",
                )
            )
            self._decorators(node.decorator_list, qualified)
            parents.append(node.name)
            self.generic_visit(node)
            parents.pop()

        def _decorators(self, decorators: list[ast.expr], qualified: str) -> None:
            for index, decorator in enumerate(decorators):
                value = _decorator_text(decorator)
                records.append(
                    _record(
                        entry,
                        kind="python_decorator",
                        location=f"symbol:{qualified}:decorator:{index}",
                        text=value,
                        line_start=decorator.lineno,
                        line_end=decorator.end_lineno or decorator.lineno,
                        symbol=qualified,
                        name=value,
                        attributes={"decorated_symbol": qualified},
                        method="python-ast",
                        interpretation="structural",
                    )
                )

        def visit_Import(self, node: ast.Import) -> None:
            self._import(node, [alias.name for alias in node.names])

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            module = "." * node.level + (node.module or "")
            self._import(node, [f"{module}:{alias.name}" for alias in node.names])

        def _import(self, node: ast.Import | ast.ImportFrom, names: list[str]) -> None:
            value = ast.get_source_segment(text, node) or ast.unparse(node)
            records.append(
                _record(
                    entry,
                    kind="python_import",
                    location=f"line:{node.lineno}",
                    text=value,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    attributes={"imports": cast(list[JsonValue], names)},
                    method="python-ast",
                    interpretation="explicit",
                )
            )

    Visitor().visit(tree)
    return records


def _schema_ref(schema: object) -> str | None:
    if isinstance(schema, dict):
        value = schema.get("$ref")
        if isinstance(value, str):
            return value
    return None


def _content_schema_refs(container: JsonValue | None) -> list[str]:
    if not isinstance(container, dict):
        return []
    direct = _schema_ref(container)
    references = [direct] if direct else []
    content = container.get("content")
    if not isinstance(content, dict):
        return references
    for media in content.values():
        if not isinstance(media, dict):
            continue
        reference = _schema_ref(media.get("schema"))
        if reference:
            references.append(reference)
    return sorted(set(references))


def _openapi_records(
    entry: InventoryEntry, value: JsonValue, line_count: int
) -> list[ExtractionRecord]:
    if not isinstance(value, dict) or not isinstance(value.get("openapi"), str):
        return []
    records: list[ExtractionRecord] = []
    global_security = value.get("security")
    paths = value.get("paths")
    if isinstance(paths, dict):
        for path in sorted(paths):
            path_item = paths[path]
            if not isinstance(path_item, dict):
                continue
            inherited = path_item.get("parameters")
            for method in HTTP_METHODS:
                operation = path_item.get(method)
                if not isinstance(operation, dict):
                    continue
                base = f"/paths/{_pointer(path)}/{method}"
                operation_name = f"{method.upper()} {path}"
                records.append(
                    _record(
                        entry,
                        kind="openapi_operation",
                        location=base,
                        text=operation_name,
                        line_start=1,
                        line_end=max(line_count, 1),
                        name=operation_name,
                        attributes={
                            "path": path,
                            "method": method.upper(),
                            "operation_id": operation.get("operationId")
                            if isinstance(operation.get("operationId"), str)
                            else None,
                            "request_schema_refs": cast(
                                list[JsonValue],
                                _content_schema_refs(operation.get("requestBody")),
                            ),
                        },
                        method="openapi-structure",
                        interpretation="explicit",
                    )
                )
                parameters = [
                    item
                    for group in (inherited, operation.get("parameters"))
                    if isinstance(group, list)
                    for item in group
                    if isinstance(item, dict)
                ]
                for index, parameter in enumerate(parameters):
                    name = parameter.get("name")
                    location = parameter.get("in")
                    if not isinstance(name, str) or not isinstance(location, str):
                        continue
                    records.append(
                        _record(
                            entry,
                            kind="openapi_parameter",
                            location=f"{base}/parameters/{index}",
                            text=f"{name} in {location}",
                            line_start=1,
                            line_end=max(line_count, 1),
                            name=name,
                            attributes={
                                "operation": operation_name,
                                "in": location,
                                "required": parameter.get("required")
                                if isinstance(parameter.get("required"), bool)
                                else None,
                                "schema_ref": _schema_ref(parameter.get("schema")),
                            },
                            method="openapi-structure",
                            interpretation="explicit",
                        )
                    )
                responses = operation.get("responses")
                if isinstance(responses, dict):
                    for status in sorted(responses):
                        response = responses[status]
                        records.append(
                            _record(
                                entry,
                                kind="openapi_response",
                                location=f"{base}/responses/{_pointer(status)}",
                                text=f"{operation_name} declares response {status}",
                                line_start=1,
                                line_end=max(line_count, 1),
                                name=status,
                                attributes={
                                    "operation": operation_name,
                                    "status": status,
                                    "schema_refs": cast(
                                        list[JsonValue], _content_schema_refs(response)
                                    ),
                                },
                                method="openapi-structure",
                                interpretation="explicit",
                            )
                        )
                security = operation.get("security", global_security)
                if isinstance(security, list):
                    records.append(
                        _record(
                            entry,
                            kind="openapi_security",
                            location=f"{base}/security",
                            text=json.dumps(security, ensure_ascii=False, sort_keys=True),
                            line_start=1,
                            line_end=max(line_count, 1),
                            name=operation_name,
                            attributes={"operation": operation_name, "security": security},
                            method="openapi-structure",
                            interpretation="explicit",
                        )
                    )
    components = value.get("components")
    schemas = components.get("schemas") if isinstance(components, dict) else None
    if isinstance(schemas, dict):
        for name in sorted(schemas):
            schema = schemas[name]
            required = schema.get("required") if isinstance(schema, dict) else None
            properties = schema.get("properties") if isinstance(schema, dict) else None
            property_records: list[JsonValue] = []
            if isinstance(properties, dict):
                for property_name in sorted(properties):
                    property_schema = properties[property_name]
                    property_records.append(
                        {
                            "name": property_name,
                            "type": property_schema.get("type")
                            if isinstance(property_schema, dict)
                            and isinstance(property_schema.get("type"), str)
                            else "unknown",
                            "schema_ref": _schema_ref(property_schema),
                        }
                    )
            records.append(
                _record(
                    entry,
                    kind="openapi_schema",
                    location=f"/components/schemas/{_pointer(name)}",
                    text=name,
                    line_start=1,
                    line_end=max(line_count, 1),
                    name=name,
                    attributes={
                        "required_fields": required
                        if isinstance(required, list)
                        and all(isinstance(item, str) for item in required)
                        else [],
                        "properties": property_records,
                    },
                    method="openapi-structure",
                    interpretation="explicit",
                )
            )
    return records


def _remote_references(value: JsonValue) -> list[str]:
    found: set[str] = set()
    pending: list[JsonValue] = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, child in current.items():
                if key == "$ref" and isinstance(child, str) and REMOTE_REF.match(child):
                    found.add(child)
                else:
                    pending.append(child)
        elif isinstance(current, list):
            pending.extend(current)
    return sorted(found)


def _project_model_records(
    entry: InventoryEntry, value: JsonValue, line_count: int
) -> list[ExtractionRecord]:
    if not isinstance(value, dict):
        return []
    project_model = value.get("qe_model")
    if not isinstance(project_model, dict):
        return []
    records: list[ExtractionRecord] = []
    for collection in sorted(project_model):
        items = project_model[collection]
        if not isinstance(items, list):
            continue
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            label = item.get("id") or item.get("name") or str(index)
            name = str(label) if isinstance(label, str | int) else str(index)
            records.append(
                _record(
                    entry,
                    kind="project_model_record",
                    location=f"/qe_model/{_pointer(collection)}/{index}",
                    text=f"{collection} record {name}",
                    line_start=1,
                    line_end=max(line_count, 1),
                    name=name,
                    attributes={"collection": collection, "value": item},
                    method="explicit-project-model-structure",
                    interpretation="explicit",
                )
            )
    return records


def parse_entry(
    root: Path,
    entry: InventoryEntry,
    *,
    limits: ParserLimits | None = None,
) -> ParseResult:
    """Parse one inventoried source after revalidating its root and content identity."""

    limits = limits or ParserLimits()
    parser = f"{entry.source_type}-parser"
    if entry.state != "INVENTORIED" or entry.content_hash is None:
        status = "UNSUPPORTED" if entry.state == "UNSUPPORTED" else "FAILED"
        return _failure(entry, status, parser, entry.reason or "Source is not parse-eligible.")
    resolved_root = root.resolve(strict=True)
    candidate = resolved_root.joinpath(*entry.path.split("/"))
    try:
        resolved = candidate.resolve(strict=True)
        if not _inside(resolved_root, resolved) or not resolved.is_file():
            return _failure(entry, "FAILED", parser, "Source path escapes root or is not a file.")
        if resolved.stat().st_size > limits.max_bytes:
            return _failure(entry, "FAILED", parser, "Source exceeds the parser byte limit.")
        data = resolved.read_bytes()
    except OSError:
        return _failure(entry, "FAILED", parser, "Source could not be read for parsing.")
    current_hash = hashlib.sha256(data).hexdigest()
    if current_hash != entry.content_hash:
        return _failure(entry, "MUTATED", parser, "Source changed after inventory.")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeError:
        return _failure(entry, "FAILED", parser, "Source is not valid UTF-8 text.")
    line_count = max(len(text.splitlines()), 1)
    issues: list[str] = []
    try:
        if entry.source_type in {"markdown", "text"}:
            records = _markdown_records(entry, text, entry.source_type == "markdown")
            if any(
                record.kind == "code_fence" and record.interpretation == "unresolved"
                for record in records
            ):
                issues.append("Markdown contains an unclosed fenced-code block.")
        elif entry.source_type == "python":
            records = _python_records(entry, text)
        elif entry.source_type in {"json", "yaml"}:
            if entry.source_type == "json":
                value = json.loads(
                    text, object_pairs_hook=_unique_object, parse_constant=_reject_constant
                )
                method = "json-data"
            else:
                yaml_node = yaml.compose(text, Loader=yaml.SafeLoader)
                if yaml_node is None:
                    value = None
                else:
                    _check_yaml_nodes(yaml_node, limits)
                    value = yaml.load(text, Loader=yaml.SafeLoader)
                method = "yaml-safe-data"
            bounded = _bounded_value(value, limits)
            records = _structured_records(entry, bounded, method, line_count, limits)
            records.extend(_openapi_records(entry, bounded, line_count))
            records.extend(_project_model_records(entry, bounded, line_count))
            remote = _remote_references(bounded)
            if remote:
                issues.append(
                    f"Remote references were recorded but not fetched ({len(remote)} blocked)."
                )
        else:
            return _failure(entry, "UNSUPPORTED", parser, "No parser supports this source type.")
    except (
        ParseFailure,
        json.JSONDecodeError,
        yaml.YAMLError,
        SyntaxError,
        RecursionError,
    ) as error:
        return _failure(entry, "FAILED", parser, f"Parser rejected source: {type(error).__name__}.")
    if len(records) > limits.max_records:
        return _failure(entry, "FAILED", parser, "Extraction count exceeds the parser limit.")
    return ParseResult(
        id=f"parse.{entry.id.removeprefix('source.')}",
        project_id=entry.project_id,
        snapshot_id=entry.snapshot_id,
        source=_source_ref(entry),
        source_hash=current_hash,
        source_type=entry.source_type,
        parser=parser,
        status="PARTIAL" if issues else "PARSED",
        extractions=records,
        issues=issues,
    )
