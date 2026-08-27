import json
from pathlib import Path

from data2dsl_generator import generate_query_template
from data2dsl_cli import main as cli_main


def test_generate_query_template_integer():
    q = generate_query_template(
        source_kind="sumd",
        metric_id="tasks_completed",
        value_kind="integer",
    )
    assert q["schema"] == "autogrammar.data2dsl/query/v0"
    assert q["query_id"] == "query:sumd:tasks_completed"
    assert q["metric"]["value_kind"] == "integer"
    assert q["metric"]["unit"] == "count"
    assert q["comparison"]["equality"] == "exact"
    assert q["left_source"]["kind"] == "sumd"
    assert q["subject"]["actor"] == "antigravity"


def test_generate_query_template_percentage():
    q = generate_query_template(
        source_kind="oql",
        metric_id="thermal_load",
        value_kind="percentage",
    )
    assert q["schema"] == "autogrammar.data2dsl/query/v0"
    assert q["metric"]["value_kind"] == "percentage"
    assert q["metric"]["unit"] == "percent"
    assert q["comparison"]["equality"] == "percentage-exact"


def test_generate_query_template_string_set():
    q = generate_query_template(
        source_kind="deta",
        metric_id="active_ports",
        value_kind="string-set",
    )
    assert q["schema"] == "autogrammar.data2dsl/query/v0"
    assert q["metric"]["value_kind"] == "string-set"
    assert q["metric"]["unit"] == "set"
    assert q["comparison"]["equality"] == "set-exact"


def test_generate_query_cli(tmp_path: Path):
    output_file = tmp_path / "generated_query.json"

    exit_code = cli_main([
        "generate-query",
        "--source", "planfile",
        "--metric", "open_tickets",
        "--value-kind", "integer",
        "--output", str(output_file),
    ])

    assert exit_code == 0
    assert output_file.exists()
    q_data = json.loads(output_file.read_text(encoding="utf-8"))
    assert q_data["schema"] == "autogrammar.data2dsl/query/v0"
    assert q_data["query_id"] == "query:planfile:open_tickets"
    assert q_data["metric"]["id"] == "open_tickets"
    assert q_data["metric"]["value_kind"] == "integer"
