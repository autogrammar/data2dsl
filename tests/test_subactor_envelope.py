import json
import pytest
from pathlib import Path

from data2dsl_subactor import (
    SubactorDelegationEnvelope,
    parse_delegation_envelope_text,
    validate_delegation_envelope,
)
from data2dsl_cli import main as cli_main


VALID_TEXT_ENVELOPE = """
ROLE: supervisor
GOAL: przywróć niezawodne przyjmowanie wiadomości e-mail do kolejki zadań
SCOPE: konektor inbound-email i jego zależności; bez zmian DNS
ACCEPTANCE: testowa wiadomość tworzy dokładnie jeden ticket, a receipt i readback potwierdzają tę samą korelację
AUTHORITY: plan + dry-run; poproś o grant przed apply
LIMITS: bez odczytu lub ujawniania sekretów; eskaluj brak poświadczenia
REPORT: ticket, diagnoza, plan_hash, wynik dry-run, wymagany grant
"""

VALID_JSON_ENVELOPE = {
    "role": "supervisor",
    "goal": "Synchronize telemetry metrics and repair discrepancies",
    "scope": "oqlos telemetry adapter and comparator",
    "acceptance": "Deterministic comparison produces zero conflicts and full EQL pass",
    "authority": "observe, plan, dry-run, apply:grant-001",
    "limits": "no mutation outside test directory; max runtime 10 minutes",
    "report": "ticket-051, plan_hash, receipt, readback",
}


def test_parse_delegation_envelope_text():
    parsed = parse_delegation_envelope_text(VALID_TEXT_ENVELOPE)
    assert parsed["role"] == "supervisor"
    assert "przywróć" in parsed["goal"]
    assert "inbound-email" in parsed["scope"]
    assert "plan + dry-run" in parsed["authority"]
    assert "sekretów" in parsed["limits"]
    assert "plan_hash" in parsed["report"]


def test_validate_valid_text_envelope():
    env = validate_delegation_envelope(VALID_TEXT_ENVELOPE)
    assert isinstance(env, SubactorDelegationEnvelope)
    assert env.valid is True
    assert len(env.errors) == 0
    assert env.role == "supervisor"

    text_out = env.to_text()
    assert "ROLE: supervisor" in text_out
    assert "GOAL:" in text_out


def test_validate_valid_json_envelope():
    env = validate_delegation_envelope(VALID_JSON_ENVELOPE)
    assert env.valid is True
    assert len(env.errors) == 0
    assert env.role == "supervisor"
    assert "grant-001" in env.authority


def test_validate_missing_required_fields():
    invalid_text = """
    ROLE: supervisor
    GOAL: test goal
    """
    env = validate_delegation_envelope(invalid_text)
    assert env.valid is False
    codes = [e.code for e in env.errors]
    assert "COMM-ENVELOPE-001" in codes


def test_validate_invalid_role():
    data = dict(VALID_JSON_ENVELOPE)
    data["role"] = "autonomous_god_agent"
    env = validate_delegation_envelope(data)
    assert env.valid is False
    assert any(e.code == "COMM-ROLE-001" for e in env.errors)


def test_validate_invalid_authority():
    data = dict(VALID_JSON_ENVELOPE)
    data["authority"] = "full_unrestricted_root_access"
    env = validate_delegation_envelope(data)
    assert env.valid is False
    assert any(e.code == "COMM-AUTH-001" for e in env.errors)


def test_cli_validate_envelope_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    envelope_path = tmp_path / "envelope.txt"
    envelope_path.write_text(VALID_TEXT_ENVELOPE.strip(), encoding="utf-8")

    out_json = tmp_path / "envelope_out.json"
    code = cli_main(["validate-envelope", "--envelope", str(envelope_path), "--output", str(out_json)])
    assert code == 0
    assert out_json.exists()

    result = json.loads(out_json.read_text(encoding="utf-8"))
    assert result["valid"] is True
    assert result["role"] == "supervisor"


def test_cli_validate_envelope_failure(tmp_path: Path):
    envelope_path = tmp_path / "invalid_envelope.json"
    envelope_path.write_text(json.dumps({"role": "invalid"}), encoding="utf-8")

    code = cli_main(["validate-envelope", "--envelope", str(envelope_path)])
    assert code == 2
