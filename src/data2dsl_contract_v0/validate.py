"""Deterministic conformance checks for the experimental data2dsl contract v0."""

from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "comparison.schema.json"
EXAMPLES = (
    ROOT / "examples" / "work-summary-github-conflict.json",
    ROOT / "examples" / "work-summary-github-match.json",
)
EXPECTED_JSONSCHEMA_VERSION = "4.26.0"


class ContractError(ValueError):
    """A stable, human-readable contract violation."""


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ContractError(f"{path}: document root must be an object")
    return value


def _schema_validator() -> Draft202012Validator:
    actual = version("jsonschema")
    if actual != EXPECTED_JSONSCHEMA_VERSION:
        raise ContractError(
            f"jsonschema version must be {EXPECTED_JSONSCHEMA_VERSION}, got {actual}"
        )
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    offset = parsed.utcoffset()
    if offset is None or offset.total_seconds() != 0:
        raise ContractError("window timestamps must carry UTC offset")
    return parsed


def _expected_policy(value_kind: str) -> str:
    return {
        "integer": "integer-exact",
        "string": "string-exact",
        "string-set": "string-set-exact",
        "float": "float-exact",
        "percentage": "percentage-exact",
    }[value_kind]


def _canonical_value(value: dict[str, Any]) -> Any:
    kind = value["kind"]
    if kind == "integer":
        return int(value["value"])
    if kind == "float":
        return float(value["value"])
    if kind == "percentage":
        return float(str(value["value"]).rstrip("%").strip())
    if kind == "string":
        return value["value"]
    items = value["items"]
    if items != sorted(items):
        raise ContractError("string-set items must be sorted by Unicode code point")
    return tuple(items)


def _expected_delta(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any] | None:
    kind = left["kind"]
    if kind == "integer":
        return {"kind": "integer", "value": str(int(right["value"]) - int(left["value"]))}
    if kind == "float":
        diff = round(float(right["value"]) - float(left["value"]), 6)
        diff_str = f"{diff:.6f}".rstrip("0").rstrip(".") if "." in f"{diff:.6f}" else str(diff)
        return {"kind": "float", "value": diff_str}
    if kind == "percentage":
        l_val = float(str(left["value"]).rstrip("%").strip())
        r_val = float(str(right["value"]).rstrip("%").strip())
        diff = round(r_val - l_val, 4)
        diff_str = f"{diff:.4f}".rstrip("0").rstrip(".") if "." in f"{diff:.4f}" else str(diff)
        return {"kind": "percentage", "value": f"{diff_str}%"}
    if kind == "string-set":
        left_items = set(left["items"])
        right_items = set(right["items"])
        return {
            "kind": "string-set",
            "added": sorted(right_items - left_items),
            "removed": sorted(left_items - right_items),
        }
    return None


def validate_document(document: dict[str, Any]) -> None:
    validator = _schema_validator()
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        location = "/".join(str(item) for item in first.absolute_path) or "$"
        raise ContractError(f"schema violation at {location}: {first.message}")

    query = document["query"]
    result = document["result"]
    observations = document["observations"]
    query_id = query["query_id"]
    if result["query_id"] != query_id:
        raise ContractError("result query_id must match query")

    window = query["window"]
    if _utc(window["start"]) >= _utc(window["end"]):
        raise ContractError("query window must have start before end")

    value_kind = query["metric"]["value_kind"]
    policy = query["comparison"]
    if policy["equality"] != _expected_policy(value_kind):
        raise ContractError("comparison equality must match metric value_kind")
    if result["comparison"] != policy:
        raise ContractError("result comparison policy must equal query policy")

    sides: dict[str, dict[str, Any]] = {}
    observation_ids: set[str] = set()
    evidence_ids: set[str] = set()
    for observation in observations:
        side = observation["side"]
        if side in sides:
            raise ContractError(f"duplicate observation side: {side}")
        sides[side] = observation
        if observation["observation_id"] in observation_ids:
            raise ContractError("observation_id values must be unique")
        observation_ids.add(observation["observation_id"])
        if observation["query_id"] != query_id:
            raise ContractError("observation query_id must match query")
        for key in ("subject", "metric", "window"):
            if observation[key] != query[key]:
                raise ContractError(f"observation {side} {key} must match query")
        value = observation["value"]
        if observation["state"] == "OBSERVED":
            if value is None:
                raise ContractError("OBSERVED requires a value")
            if value["kind"] != value_kind:
                raise ContractError("observation value kind must match metric")
            _canonical_value(value)
        elif value is not None:
            raise ContractError("UNEVALUABLE and EXPIRED observations require null value")
        for evidence in observation["evidence"]:
            evidence_id = evidence["evidence_id"]
            if evidence_id in evidence_ids:
                raise ContractError("evidence_id values must be unique")
            evidence_ids.add(evidence_id)
            if evidence["target_uri"] != query["subject"]["repository"]:
                raise ContractError("evidence target_uri must match query repository")
            location = evidence["location"]
            if location["kind"] == "markdown-lines" and location["end_line"] < location["start_line"]:
                raise ContractError("markdown evidence end_line must not precede start_line")

    if result["evidence_ids"] != sorted(evidence_ids):
        raise ContractError("result evidence_ids must be the sorted complete evidence set")

    left = sides.get("left")
    right = sides.get("right")
    expected_left_id = left["observation_id"] if left else None
    expected_right_id = right["observation_id"] if right else None
    if result["left_observation_id"] != expected_left_id:
        raise ContractError("left_observation_id does not resolve to the left observation")
    if result["right_observation_id"] != expected_right_id:
        raise ContractError("right_observation_id does not resolve to the right observation")

    if left is None:
        expected_outcome, expected_delta = "MISSING_LEFT", None
    elif right is None:
        expected_outcome, expected_delta = "MISSING_RIGHT", None
    elif left["state"] != "OBSERVED" or right["state"] != "OBSERVED":
        expected_outcome, expected_delta = "UNEVALUABLE", None
    else:
        left_value = _canonical_value(left["value"])
        right_value = _canonical_value(right["value"])
        if left_value == right_value:
            expected_outcome, expected_delta = "MATCH", None
        else:
            expected_outcome = "CONFLICT"
            expected_delta = _expected_delta(left["value"], right["value"])

    if result["outcome"] != expected_outcome:
        raise ContractError(f"outcome must be {expected_outcome}")
    if result["delta"] != expected_delta:
        raise ContractError(f"delta must be {expected_delta!r}")


def _expect_invalid(name: str, document: dict[str, Any]) -> None:
    try:
        validate_document(document)
    except ContractError:
        return
    raise ContractError(f"negative case unexpectedly passed: {name}")


def _missing_case(base: dict[str, Any], missing: str) -> dict[str, Any]:
    document = copy.deepcopy(base)
    document["observations"] = [item for item in document["observations"] if item["side"] != missing]
    remaining = document["observations"][0]
    result = document["result"]
    result["outcome"] = "MISSING_LEFT" if missing == "left" else "MISSING_RIGHT"
    result["left_observation_id"] = None if missing == "left" else remaining["observation_id"]
    result["right_observation_id"] = None if missing == "right" else remaining["observation_id"]
    result["delta"] = None
    result["evidence_ids"] = sorted(item["evidence_id"] for item in remaining["evidence"])
    return document


def self_test() -> None:
    conflict = _load(EXAMPLES[0])
    match = _load(EXAMPLES[1])
    validate_document(conflict)
    validate_document(match)
    validate_document(_missing_case(match, "left"))
    validate_document(_missing_case(match, "right"))

    unevaluable = copy.deepcopy(match)
    unevaluable["observations"][1]["state"] = "UNEVALUABLE"
    unevaluable["observations"][1]["value"] = None
    unevaluable["result"]["outcome"] = "UNEVALUABLE"
    validate_document(unevaluable)

    cross_key = copy.deepcopy(conflict)
    cross_key["observations"][1]["subject"]["actor"] = "github:someone-else"
    _expect_invalid("cross-key actor", cross_key)

    bad_digest = copy.deepcopy(conflict)
    bad_digest["observations"][0]["evidence"][0]["digest_sha256"] = "ABC"
    _expect_invalid("invalid digest", bad_digest)

    bad_delta = copy.deepcopy(conflict)
    bad_delta["result"]["delta"]["value"] = "-1"
    _expect_invalid("incorrect delta", bad_delta)

    missing_evidence = copy.deepcopy(match)
    missing_evidence["observations"][0]["evidence"] = []
    _expect_invalid("missing evidence", missing_evidence)

    unordered_set = copy.deepcopy(match)
    unordered_set["query"]["metric"]["value_kind"] = "string-set"
    unordered_set["query"]["comparison"]["equality"] = "string-set-exact"
    unordered_set["result"]["comparison"]["equality"] = "string-set-exact"
    for observation in unordered_set["observations"]:
        observation["metric"]["value_kind"] = "string-set"
        observation["value"] = {"kind": "string-set", "items": ["z", "a"]}
    _expect_invalid("unordered string-set", unordered_set)

    print("CONTRACT-V0-PASS: 5 positive outcomes, 5 negative invariants")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and not args.paths:
        parser.error("provide --self-test or at least one document path")
    if args.self_test:
        self_test()
    for path in args.paths:
        validate_document(_load(path))
        print(f"CONTRACT-V0-PASS: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
