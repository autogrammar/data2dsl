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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if args.command == "compare":
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
        if getattr(args, "format", "json") == "markdown":
            from data2dsl_batch import format_markdown_report

            output_str = format_markdown_report(bundle)
        else:
            output_str = json.dumps(bundle, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0

    if args.command == "compare-golden":
        md_text = args.markdown.read_text(encoding="utf-8")
        github_data = json.loads(args.github_response.read_text(encoding="utf-8"))

        raw_actor = github_data.get("actor", "alice")
        actor_clean = raw_actor.replace("github:", "").strip()
        repo = github_data.get("repository", "autogrammar/data2dsl")
        repo_uri = repo if repo.startswith("https://") else f"https://github.com/{repo}"

        query = {
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
        output_str = json.dumps(bundle, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0

    if args.command == "validate":
        bundle_doc = json.loads(args.bundle.read_text(encoding="utf-8"))
        validate_document(bundle_doc)
        print(f"VALID: {args.bundle}")
        return 0

    if args.command == "discover":
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
        output_str = json.dumps(graph, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0

    if args.command == "feed-consumer":
        from data2dsl_consumer import ConsumerFactFeed

        bundle_doc = json.loads(args.bundle.read_text(encoding="utf-8"))
        payload = ConsumerFactFeed.export_reasoning_payload(bundle_doc)
        output_str = json.dumps(payload.to_dict(), indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0

    if args.command == "feed-doctor":
        from data2dsl_doctor import format_diagnostic_profile

        bundle_doc = json.loads(args.bundle.read_text(encoding="utf-8"))
        profile = format_diagnostic_profile(bundle_doc)
        output_str = json.dumps(profile, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0

    if args.command == "feed-koru":
        from data2dsl_remediation import format_remediation_intent

        bundle_doc = json.loads(args.bundle.read_text(encoding="utf-8"))
        intent = format_remediation_intent(bundle_doc, ticket_id=args.ticket)
        output_str = json.dumps(intent, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0

    if args.command == "validate-envelope":
        from data2dsl_subactor import validate_delegation_envelope

        content = args.envelope.read_text(encoding="utf-8")
        envelope = validate_delegation_envelope(content)
        result = envelope.to_dict()
        output_str = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0 if envelope.valid else 2

    if args.command == "simulate-healing":
        from data2dsl_subactor import simulate_self_healing_cycle

        query_doc = json.loads(args.query.read_text(encoding="utf-8"))
        left_doc = json.loads(args.left.read_text(encoding="utf-8"))
        right_doc = json.loads(args.right.read_text(encoding="utf-8"))

        result = simulate_self_healing_cycle(query_doc, left_doc, right_doc)
        output_str = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0 if result.get("status") == "HEALED" else 1

    if args.command == "batch":
        from data2dsl_batch import BatchMultiQueryComparator

        queries_data = json.loads(args.queries.read_text(encoding="utf-8"))
        batch_queries: list[Any]
        if isinstance(queries_data, dict) and "queries" in queries_data:
            batch_queries = list(queries_data["queries"])
        elif isinstance(queries_data, list):
            batch_queries = list(queries_data)
        else:
            batch_queries = [queries_data]

        batch_left_obs: list[Any]
        left_data = json.loads(args.left.read_text(encoding="utf-8"))
        if isinstance(left_data, dict) and "observations" in left_data:
            batch_left_obs = list(left_data["observations"])
        elif isinstance(left_data, list):
            batch_left_obs = list(left_data)
        else:
            batch_left_obs = [left_data]

        batch_right_obs: list[Any]
        right_data = json.loads(args.right.read_text(encoding="utf-8"))
        if isinstance(right_data, dict) and "observations" in right_data:
            batch_right_obs = list(right_data["observations"])
        elif isinstance(right_data, list):
            batch_right_obs = list(right_data)
        else:
            batch_right_obs = [right_data]

        batch_cmp = BatchMultiQueryComparator()
        report = batch_cmp.compare_batch(batch_queries, batch_left_obs, batch_right_obs)
        if getattr(args, "format", "json") == "markdown":
            from data2dsl_batch import format_markdown_report

            output_str = format_markdown_report(report)
        else:
            output_str = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0 if report.summary.is_clean else 1

    if args.command == "generate-query":
        from data2dsl_generator import generate_query_template

        query = generate_query_template(
            source_kind=args.source,
            metric_id=args.metric,
            value_kind=args.value_kind,
            equality=args.equality,
        )
        output_str = json.dumps(query, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(output_str + "\n", encoding="utf-8")
        else:
            print(output_str)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
