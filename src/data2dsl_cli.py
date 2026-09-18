from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from data2dsl_adapters import (
    DiagitCommitMetricResponse,
    GitHubDiagitAdapter,
    WorkSummaryMarkdownAdapter,
)
from data2dsl_comparator import compare_observations
from data2dsl_contract_v0.validate import validate_document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="data2dsl",
        description="data2dsl: neutral factual data comparator and bundle generator",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run self-test on built-in comparison fixtures.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # compare
    cmp_parser = subparsers.add_parser(
        "compare", help="Compare two observation JSON files deterministically."
    )
    cmp_parser.add_argument(
        "--left", required=True, type=Path, help="Path to left observation JSON."
    )
    cmp_parser.add_argument(
        "--right", required=True, type=Path, help="Path to right observation JSON."
    )
    cmp_parser.add_argument(
        "--query", type=Path, default=None, help="Optional query JSON path."
    )
    cmp_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )
    cmp_parser.add_argument(
        "--format", choices=["json", "markdown"], default="json", help="Output format (json | markdown)."
    )

    # compare-golden
    golden_parser = subparsers.add_parser(
        "compare-golden",
        help="Compare work-summary.md claim with Diagit GitHub response.",
    )
    golden_parser.add_argument(
        "--markdown", required=True, type=Path, help="Path to work-summary.md."
    )
    golden_parser.add_argument(
        "--github-response",
        required=True,
        type=Path,
        help="Path to Diagit GitHub response JSON.",
    )
    golden_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )

    # validate
    val_parser = subparsers.add_parser(
        "validate", help="Validate a comparison bundle JSON against contract v0."
    )
    val_parser.add_argument(
        "--bundle", required=True, type=Path, help="Path to bundle JSON."
    )

    # discover
    discover_parser = subparsers.add_parser(
        "discover",
        help="Build a bounded data graph from one explicit JSON source envelope.",
    )
    discover_parser.add_argument(
        "--input",
        default="-",
        help="Path to {sources, query} JSON, or '-' to read it from stdin.",
    )
    discover_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )

    # feed-consumer
    feed_parser = subparsers.add_parser(
        "feed-consumer", help="Export comparison bundle into structured reasoning fact feed."
    )
    feed_parser.add_argument(
        "--bundle", required=True, type=Path, help="Path to comparison bundle JSON."
    )
    feed_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )

    # feed-doctor
    doctor_parser = subparsers.add_parser(
        "feed-doctor", help="Export comparison bundle(s) into diagnostic profile feed for doctor-agent."
    )
    doctor_parser.add_argument(
        "--bundle", required=True, type=Path, help="Path to comparison bundle or list of bundles JSON."
    )
    doctor_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )

    # feed-koru
    koru_parser = subparsers.add_parser(
        "feed-koru", help="Export comparison bundle(s) into remediation intent feed for semcod/koru."
    )
    koru_parser.add_argument(
        "--bundle", required=True, type=Path, help="Path to comparison bundle or list of bundles JSON."
    )
    koru_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )
    koru_parser.add_argument(
        "--ticket", type=str, default=None, help="Optional ticket identifier."
    )

    # validate-envelope
    env_parser = subparsers.add_parser(
        "validate-envelope", help="Validate a Subactor delegation envelope file (text or JSON)."
    )
    env_parser.add_argument(
        "--envelope", required=True, type=Path, help="Path to delegation envelope file."
    )
    env_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )

    # simulate-healing
    heal_parser = subparsers.add_parser(
        "simulate-healing", help="Simulate a DETECT->PLAN->EXECUTE->VERIFY->HEAL closed loop."
    )
    heal_parser.add_argument(
        "--query", required=True, type=Path, help="Path to query JSON."
    )
    heal_parser.add_argument(
        "--left", required=True, type=Path, help="Path to left observation JSON."
    )
    heal_parser.add_argument(
        "--right", required=True, type=Path, help="Path to right observation JSON."
    )
    heal_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )

    # batch
    batch_parser = subparsers.add_parser(
        "batch",
        help="Compare a batch of queries against observation collections deterministically.",
    )
    batch_parser.add_argument(
        "--queries", required=True, type=Path, help="Path to queries JSON."
    )
    batch_parser.add_argument(
        "--left", required=True, type=Path, help="Path to left observations JSON."
    )
    batch_parser.add_argument(
        "--right", required=True, type=Path, help="Path to right observations JSON."
    )
    batch_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )
    batch_parser.add_argument(
        "--format", choices=["json", "markdown"], default="json", help="Output format (json | markdown)."
    )

    # generate-query
    gen_parser = subparsers.add_parser(
        "generate-query",
        help="Generate a canonical autogrammar.data2dsl/query/v0 query template.",
    )
    gen_parser.add_argument(
        "--source", required=True, help="Source adapter kind (e.g. sumd, oql, markdown, planfile, github)."
    )
    gen_parser.add_argument(
        "--metric", required=True, help="Metric identifier."
    )
    gen_parser.add_argument(
        "--value-kind", default="integer", help="Value kind (integer, float, percentage, string, string-set)."
    )
    gen_parser.add_argument(
        "--equality", default="exact", help="Equality policy."
    )
    gen_parser.add_argument(
        "--output", type=Path, default=None, help="Optional output JSON path."
    )

    return parser


def run_self_test() -> int:
    from data2dsl_contract_v0.validate import self_test

    self_test()
    print("data2dsl CLI self-test passed.")
    return 0


def _emit(args: argparse.Namespace, output_str: str) -> None:
    if args.output:
        args.output.write_text(output_str + "\n", encoding="utf-8")
    else:
        print(output_str)


def _emit_json(args: argparse.Namespace, obj: Any) -> None:
    _emit(args, json.dumps(obj, indent=2, ensure_ascii=False))


def _emit_json_or_markdown(args: argparse.Namespace, doc: Any) -> None:
    if getattr(args, "format", "json") == "markdown":
        from data2dsl_batch import format_markdown_report

        _emit(args, format_markdown_report(doc))
    else:
        _emit_json(args, doc.to_dict() if hasattr(doc, "to_dict") else doc)


def _cmd_compare(args: argparse.Namespace) -> int:
    left_doc = json.loads(args.left.read_text(encoding="utf-8"))
    right_doc = json.loads(args.right.read_text(encoding="utf-8"))
    if args.query:
        query = json.loads(args.query.read_text(encoding="utf-8"))
    else:
        query = {
            "schema": "autogrammar.data2dsl/query/v0",
            "query_id": left_doc.get("query_id", "query:cli:default"),
            "subject": left_doc["subject"],
            "metric": left_doc["metric"],
            "window": left_doc["window"],
            "left_source": {"id": "source:left", "kind": "markdown"},
            "right_source": {"id": "source:right", "kind": "github"},
            "comparison": {
                "equality": "integer-exact",
                "delta_direction": "right-minus-left",
                "missing_is_zero": False,
            },
        }
    bundle = compare_observations(query, left_doc, right_doc)
    validate_document(bundle)
    _emit_json_or_markdown(args, bundle)
    return 0


def _compare_golden_query(github_data: dict, actor_clean: str, repo_uri: str) -> dict:
    return {
        "schema": "autogrammar.data2dsl/query/v0",
        "query_id": f"query:compare-golden:{actor_clean}",
        "subject": {
            "repository": repo_uri,
            "actor": f"github:{actor_clean.lower()}",
        },
        "metric": {
            "id": "git.commit.count",
            "version": "v1",
            "value_kind": "integer",
            "unit": "count",
        },
        "window": {
            "start": github_data["time_window_start"],
            "end": github_data["time_window_end"],
            "semantics": "half-open-utc",
        },
        "left_source": {"id": "source:work-summary", "kind": "markdown"},
        "right_source": {"id": "source:diagit:github", "kind": "github"},
        "comparison": {
            "equality": "integer-exact",
            "delta_direction": "right-minus-left",
            "missing_is_zero": False,
        },
    }


def _cmd_compare_golden(args: argparse.Namespace) -> int:
    md_text = args.markdown.read_text(encoding="utf-8")
    github_data = json.loads(args.github_response.read_text(encoding="utf-8"))

    raw_actor = github_data.get("actor", "alice")
    actor_clean = raw_actor.replace("github:", "").strip()
    repo = github_data.get("repository", "autogrammar/data2dsl")
    repo_uri = repo if repo.startswith("https://") else f"https://github.com/{repo}"

    query = _compare_golden_query(github_data, actor_clean, repo_uri)

    adapter = WorkSummaryMarkdownAdapter()
    claim = adapter.extract_commit_claim(
        markdown_text=md_text,
        actor=actor_clean,
        path=str(args.markdown),
        repository_uri=repo_uri,
    )

    resp = DiagitCommitMetricResponse(
        status=github_data.get("status", "OK"),
        commit_count=github_data.get("commit_count"),
        error_message=github_data.get("error_message"),
    )
    left_obs = adapter.normalize(query, claim, side="left")
    right_obs = GitHubDiagitAdapter().normalize(query, resp, side="right")

    bundle = compare_observations(query, left_obs, right_obs)
    validate_document(bundle)
    _emit_json(args, bundle)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    bundle_doc = json.loads(args.bundle.read_text(encoding="utf-8"))
    validate_document(bundle_doc)
    print(f"VALID: {args.bundle}")
    return 0


def _cmd_discover(args: argparse.Namespace) -> int:
    from data2dsl_discovery import DiscoveryError, discover_data_network

    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        envelope = json.loads(raw)
        if not isinstance(envelope, dict) or set(envelope) - {"sources", "query"}:
            raise DiscoveryError("discovery_envelope_invalid")
        sources = envelope.get("sources")
        if not isinstance(sources, list):
            raise DiscoveryError("discovery_sources_invalid")
        graph = discover_data_network(sources, query=envelope.get("query"))
    except (DiscoveryError, json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        error = {
            "status": "ERROR",
            "error_code": "DISCOVERY_INVALID",
            "message": str(exc),
        }
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 2
    _emit_json(args, graph)
    return 0


def _feed_command(args: argparse.Namespace, render) -> int:
    bundle_doc = json.loads(args.bundle.read_text(encoding="utf-8"))
    _emit_json(args, render(bundle_doc))
    return 0


def _cmd_feed_consumer(args: argparse.Namespace) -> int:
    from data2dsl_consumer import ConsumerFactFeed

    return _feed_command(
        args, lambda doc: ConsumerFactFeed.export_reasoning_payload(doc).to_dict()
    )


def _cmd_feed_doctor(args: argparse.Namespace) -> int:
    from data2dsl_doctor import format_diagnostic_profile

    return _feed_command(args, format_diagnostic_profile)


def _cmd_feed_koru(args: argparse.Namespace) -> int:
    from data2dsl_remediation import format_remediation_intent

    return _feed_command(
        args, lambda doc: format_remediation_intent(doc, ticket_id=args.ticket)
    )


def _cmd_validate_envelope(args: argparse.Namespace) -> int:
    from data2dsl_subactor import validate_delegation_envelope

    content = args.envelope.read_text(encoding="utf-8")
    envelope = validate_delegation_envelope(content)
    _emit_json(args, envelope.to_dict())
    return 0 if envelope.valid else 2


def _cmd_simulate_healing(args: argparse.Namespace) -> int:
    from data2dsl_subactor import simulate_self_healing_cycle

    query_doc = json.loads(args.query.read_text(encoding="utf-8"))
    left_doc = json.loads(args.left.read_text(encoding="utf-8"))
    right_doc = json.loads(args.right.read_text(encoding="utf-8"))
    result = simulate_self_healing_cycle(query_doc, left_doc, right_doc)
    _emit_json(args, result)
    return 0 if result.get("status") == "HEALED" else 1


def _obs_list(data: Any, key: str) -> list[Any]:
    """Normalize a JSON payload into an observations/queries list."""
    if isinstance(data, dict) and key in data:
        return list(data[key])
    if isinstance(data, list):
        return list(data)
    return [data]


def _cmd_batch(args: argparse.Namespace) -> int:
    from data2dsl_batch import BatchMultiQueryComparator

    batch_queries = _obs_list(json.loads(args.queries.read_text(encoding="utf-8")), "queries")
    batch_left_obs = _obs_list(json.loads(args.left.read_text(encoding="utf-8")), "observations")
    batch_right_obs = _obs_list(json.loads(args.right.read_text(encoding="utf-8")), "observations")

    report = BatchMultiQueryComparator().compare_batch(
        batch_queries, batch_left_obs, batch_right_obs
    )
    _emit_json_or_markdown(args, report)
    return 0 if report.summary.is_clean else 1


def _cmd_generate_query(args: argparse.Namespace) -> int:
    from data2dsl_generator import generate_query_template

    query = generate_query_template(
        source_kind=args.source,
        metric_id=args.metric,
        value_kind=args.value_kind,
        equality=args.equality,
    )
    _emit_json(args, query)
    return 0


_COMMAND_HANDLERS = {
    "compare": _cmd_compare,
    "compare-golden": _cmd_compare_golden,
    "validate": _cmd_validate,
    "discover": _cmd_discover,
    "feed-consumer": _cmd_feed_consumer,
    "feed-doctor": _cmd_feed_doctor,
    "feed-koru": _cmd_feed_koru,
    "validate-envelope": _cmd_validate_envelope,
    "simulate-healing": _cmd_simulate_healing,
    "batch": _cmd_batch,
    "generate-query": _cmd_generate_query,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    handler = _COMMAND_HANDLERS.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
