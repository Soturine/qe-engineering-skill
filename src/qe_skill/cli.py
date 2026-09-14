"""Bounded, read-only JSON validation CLI. No evidence execution or network access."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import NoReturn

from jsonschema import Draft202012Validator
from pydantic import ValidationError

from qe_skill.domain import ProjectModel, SourceLedger
from qe_skill.integrity import validate_project_model
from qe_skill.schemas import schema_text
from qe_skill.validation import Issue, Result, TrustContext, validate_ledger

MAX_BYTES = 2 * 1024 * 1024
MAX_DEPTH = 64
MAX_RECORDS = 2000


class InputFailure(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise InputFailure("MODEL_DUPLICATE_KEY", "JSON contains duplicate object keys.")
        output[key] = value
    return output


def reject_constant(value: str) -> NoReturn:
    raise InputFailure("MODEL_JSON", "Non-finite numbers are not valid JSON evidence.")


def read_json(path: Path) -> object:
    if path.is_symlink() or not path.is_file():
        raise InputFailure("SRC_INPUT", "Input must be an explicitly selected regular JSON file.")
    try:
        with path.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise InputFailure("SRC_INPUT_LIMIT", "JSON exceeds the M0 input byte limit.")
        value: object = json.loads(
            data.decode("utf-8-sig"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise InputFailure("MODEL_JSON", "Input is not valid UTF-8 JSON.") from error
    except RecursionError as error:
        raise InputFailure("SRC_INPUT_LIMIT", "JSON nesting exceeds the parser limit.") from error
    pending = [(value, 0)]
    records = 0
    while pending:
        item, depth = pending.pop()
        if depth > MAX_DEPTH:
            raise InputFailure("SRC_INPUT_LIMIT", "JSON exceeds the M0 nesting limit.")
        if isinstance(item, dict):
            records += 1
            pending.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            pending.extend((child, depth + 1) for child in item)
        if records > MAX_RECORDS:
            raise InputFailure("SRC_INPUT_LIMIT", "JSON exceeds the M0 record-count limit.")
    return value


def read_context(path: Path | None) -> TrustContext:
    if path is None:
        return TrustContext()
    value = read_json(path)
    if not isinstance(value, dict) or set(value) != {"approved_record_hashes"}:
        raise InputFailure("APPROVAL_CONTEXT", "Trusted context must contain only approval hashes.")
    hashes = value["approved_record_hashes"]
    if not isinstance(hashes, list) or not all(
        isinstance(item, str) and len(item) == 64 and all(c in "0123456789abcdef" for c in item)
        for item in hashes
    ):
        raise InputFailure("APPROVAL_CONTEXT", "Trusted context contains invalid approval digests.")
    return TrustContext(frozenset(hashes))


def emit(result: Result) -> int:
    print(
        json.dumps(
            {
                "schema_version": "1.0",
                "valid": result.valid,
                "issues": [asdict(i) for i in result.issues],
                "validation_scope": "Declared M0 contracts and gates; not source authentication.",
                "publication_authorized": False,
            },
            sort_keys=True,
        )
    )
    return 0 if result.valid else 1


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        emit(Result([Issue("MODEL_COMMAND", "input", "Invalid command arguments; use --help.")]))
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    parser = Parser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "validate-ledger",
            "validate-oracle",
            "validate-project-model",
            "validate-test-case",
        ],
    )
    parser.add_argument("file", type=Path, help="Ledger JSON, or complete Project Model JSON")
    parser.add_argument("--id", dest="artifact_id", help="Required oracle/test identifier")
    parser.add_argument(
        "--trusted-approvals",
        type=Path,
        help="Operator-selected governance context, never extracted from evidence",
    )
    args = parser.parse_args(argv)
    try:
        value = read_json(args.file)
        ledger_command = args.command == "validate-ledger"
        schema = json.loads(schema_text("source-ledger" if ledger_command else "project-model"))
        if next(Draft202012Validator(schema).iter_errors(value), None) is not None:
            raise InputFailure("MODEL_SCHEMA", "Input does not satisfy the versioned JSON Schema.")
        if ledger_command:
            if args.artifact_id or args.trusted_approvals:
                raise InputFailure(
                    "MODEL_COMMAND", "Ledger command does not accept selection or approval."
                )
            return emit(validate_ledger(SourceLedger.model_validate(value)))
        model = ProjectModel.model_validate(value)
        if args.command in {"validate-oracle", "validate-test-case"}:
            candidates = (
                model.oracles if args.command == "validate-oracle" else model.tests.test_cases
            )
            if args.artifact_id is None or not any(c.id == args.artifact_id for c in candidates):
                raise InputFailure("MODEL_SELECTION", "Select an existing oracle/test using --id.")
        elif args.artifact_id:
            raise InputFailure("MODEL_COMMAND", "Project Model validation does not take --id.")
        # Full context is checked even for a selected artifact: no partial-context bypass.
        return emit(validate_project_model(model, read_context(args.trusted_approvals)))
    except InputFailure as error:
        return emit(Result([Issue(error.code, "input", str(error))]))
    except ValidationError:
        return emit(
            Result([Issue("MODEL_SCHEMA", "input", "Strict domain shape validation failed.")])
        )
    except OSError:
        return emit(Result([Issue("SRC_INPUT", "input", "Input file could not be read.")]))


if __name__ == "__main__":
    sys.exit(main())
