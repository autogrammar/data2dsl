from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

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

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
