from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from data2dsl_cli_commands import _COMMAND_HANDLERS


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

    handler = _COMMAND_HANDLERS.get(args.command)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
