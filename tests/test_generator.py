import json
from pathlib import Path

from data2dsl_generator import generate_query_template, VALID_SOURCE_KINDS
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
    assert q["metric"]["version"] == "v1"
    assert q["comparison"]["equality"] == "integer-exact"
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
    assert q["metric"]["version"] == "v1"
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
    assert q["metric"]["version"] == "v1"
    assert q["comparison"]["equality"] == "string-set-exact"


def test_generate_query_template_float():
    q = generate_query_template(
        source_kind="oql",
        metric_id="oql.sample_rate",
        value_kind="float",
    )
    assert q["metric"]["version"] == "v1"
    assert q["comparison"]["equality"] == "float-exact"
    assert q["metric"]["unit"] == "hz"


def test_generate_query_template_string():
    q = generate_query_template(
        source_kind="code2logic",
        metric_id="function_name",
        value_kind="string",
    )
    assert q["metric"]["version"] == "v1"
    assert q["comparison"]["equality"] == "string-exact"


def test_generate_query_template_dynamic_window():
    """Window should not be hardcoded to Aug 2026."""
    q = generate_query_template(
        source_kind="markdown",
        metric_id="git.commit.count",
    )
    # Window end should be today or recent, not hardcoded
    assert "start" in q["window"]
    assert "end" in q["window"]
    assert q["window"]["semantics"] == "half-open-utc"
    # Should be valid ISO 8601 format
    assert q["window"]["start"].endswith("Z")
    assert q["window"]["end"].endswith("Z")


def test_generate_query_template_explicit_window():
    """Explicit window should be preserved."""
    q = generate_query_template(
        source_kind="markdown",
        metric_id="git.commit.count",
        window_start="2026-01-01T00:00:00Z",
        window_end="2026-01-31T00:00:00Z",
    )
    assert q["window"]["start"] == "2026-01-01T00:00:00Z"
    assert q["window"]["end"] == "2026-01-31T00:00:00Z"


def test_generate_query_template_right_source_defaults():
    """Right source should be a valid source kind from the contract."""
    for src in VALID_SOURCE_KINDS:
        q = generate_query_template(source_kind=src, metric_id="test.metric")
        r_kind = q["right_source"]["kind"]
        assert r_kind in VALID_SOURCE_KINDS, (
            f"right_source kind '{r_kind}' for left '{src}' is not in contract"
        )


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
    assert q_data["metric"]["version"] == "v1"


def test_generated_query_passes_contract_validation():
    """AC-04: generate_query_template() output for every adapter passes the
    contract schema validator.

    This is the key acceptance test from audit finding F02: the generator
    must produce queries that the comparison contract actually accepts.
    """
    # Import schema and jsonschema here to keep the test self-contained
    import jsonschema

    schema_path = Path(__file__).resolve().parent.parent / "src" / "data2dsl_contract_v0" / "comparison.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    query_schema = schema["$defs"]["query"]
    # Build a resolver so $ref works
    resolver = jsonschema.RefResolver.from_schema(schema)

    # Test matrix: every source kind × representative value_kind
    test_cases = [
        ("markdown", "git.commit.count", "integer"),
        ("github", "git.commit.count", "integer"),
        ("code2logic", "cfg.complexity", "integer"),
        ("code2schema", "schema.entity.count", "integer"),
        ("code2schema", "schema.entities", "string-set"),
        ("curllm", "page.metric", "string"),
        ("planfile", "open_tickets", "integer"),
        ("planfile", "ticket_ids", "string-set"),
        ("deta", "active_ports", "string-set"),
        ("deta", "service_count", "integer"),
        ("intent_contract", "party_count", "integer"),
        ("intent_contract", "parties", "string-set"),
        ("oql", "oql.sample_rate", "float"),
        ("oql", "oql.thermal_load", "percentage"),
        ("oql", "oql.pinout", "string-set"),
        ("sumd", "tasks_completed", "integer"),
        ("sumd", "task_ids", "string-set"),
    ]

    errors = []
    for src, metric, vk in test_cases:
        q = generate_query_template(
            source_kind=src,
            metric_id=metric,
            value_kind=vk,
        )
        try:
            jsonschema.validate(q, query_schema, resolver=resolver)
        except jsonschema.ValidationError as e:
            errors.append(f"{src}/{metric}/{vk}: {e.message}")

    assert not errors, "Generated queries failed contract validation:\n" + "\n".join(errors)


def test_legacy_exact_equality_mapped():
    """The old 'exact' and 'set-exact' values must be mapped to contract forms."""
    q1 = generate_query_template(
        source_kind="markdown",
        metric_id="git.commit.count",
        equality="exact",
    )
    assert q1["comparison"]["equality"] == "integer-exact"

    q2 = generate_query_template(
        source_kind="deta",
        metric_id="active_ports",
        value_kind="string-set",
        equality="set-exact",
    )
    assert q2["comparison"]["equality"] == "string-set-exact"
