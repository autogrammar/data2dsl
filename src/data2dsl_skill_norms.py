"""Per-source-type raw normalization handlers for data2dsl skill."""

from __future__ import annotations

from typing import Any, Dict

from data2dsl_adapters import (
    Code2LogicAdapter,
    Code2LogicMetricResponse,
    Code2SchemaAdapter,
    Code2SchemaMetricResponse,
    CurllmAdapter,
    CurllmMetricResponse,
    CurllmPageEvidence,
    DetaAdapter,
    DetaServiceEvidence,
    DetaTopologyResponse,
    DiagitCommitMetricResponse,
    DiagitPageEvidence,
    GitHubDiagitAdapter,
    IntentContractAdapter,
    IntentContractResponse,
    OqlScenarioSpecResponse,
    OqlTelemetryAdapter,
    OqlTelemetryLogResponse,
    PlanfileAdapter,
    PlanfileMetricResponse,
    PlanfileTicketEvidence,
    SUMDAdapter,
    SUMDMetricResponse,
    WorkSummaryMarkdownAdapter,
)


def _coalesce_numeric(*values: Any) -> Any:
    """Return first non-None value, treating 0/0.0 as valid."""
    for v in values:
        if v is not None:
            return v
    return None


def _norm_markdown(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    md_adapter = WorkSummaryMarkdownAdapter()
    claim = md_adapter.extract_commit_claim(
        markdown_text=raw.get("markdown_content", ""),
        actor=query["subject"]["actor"],
        path=raw.get("path", "work-summary.md"),
        source_uri=raw.get("source_uri"),
        source_revision=raw.get("source_revision"),
    )
    return md_adapter.normalize(query, claim, side=side)


def _diagit_pages(raw: Dict[str, Any]) -> tuple:
    pages_obj: list[DiagitPageEvidence] = []
    for p in raw.get("pages", ()):
        if isinstance(p, DiagitPageEvidence):
            pages_obj.append(p)
        elif isinstance(p, dict):
            pages_obj.append(DiagitPageEvidence(
                page=p.get("page", 1),
                cursor=p.get("cursor"),
                digest_sha256=p.get("digest_sha256", ""),
                source_revision=p.get("source_revision", ""),
                endpoint=p.get("endpoint", "/commits"),
                media_type=p.get("media_type", "application/json"),
                source_uri=p.get("source_uri", "https://api.github.com"),
            ))
    return tuple(pages_obj)


def _norm_github(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    gh_adapter = GitHubDiagitAdapter()
    resp = raw.get("response")
    if not isinstance(resp, DiagitCommitMetricResponse):
        resp = DiagitCommitMetricResponse(
            status=raw.get("status", "OK" if raw.get("commit_count") is not None else "NOT_FOUND"),
            commit_count=raw.get("commit_count"),
            pages=_diagit_pages(raw),
            error_message=raw.get("error_message"),
        )
    return gh_adapter.normalize(query, resp, side=side)


def _curllm_pages(raw: Dict[str, Any]) -> tuple:
    pages_obj: list[CurllmPageEvidence] = []
    for p in raw.get("pages", ()):
        if isinstance(p, CurllmPageEvidence):
            pages_obj.append(p)
        elif isinstance(p, dict):
            pages_obj.append(CurllmPageEvidence(
                url=p.get("url", ""),
                digest_sha256=p.get("digest_sha256", ""),
                page=p.get("page", 1),
                endpoint=p.get("endpoint", "web-page"),
                source_revision=p.get("source_revision"),
                media_type=p.get("media_type", "text/html"),
            ))
    return tuple(pages_obj)


def _norm_curllm(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    curllm_adapter = CurllmAdapter()
    resp = raw.get("response")
    if not isinstance(resp, CurllmMetricResponse):
        resp = CurllmMetricResponse(
            status=raw.get("status", "OK" if raw.get("value") is not None else "ERROR"),
            value=raw.get("value"),
            pages=_curllm_pages(raw),
            error_message=raw.get("error_message"),
        )
    return curllm_adapter.normalize(query, resp, side=side)


def _norm_code2logic(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    c2l_adapter = Code2LogicAdapter()
    resp = raw.get("response")
    if not isinstance(resp, Code2LogicMetricResponse):
        resp = Code2LogicMetricResponse(
            status=raw.get("status", "OK" if raw.get("value") is not None else "ERROR"),
            value=raw.get("value"),
            error_message=raw.get("error_message"),
        )
    return c2l_adapter.normalize(query, resp, side=side)


def _norm_code2schema(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    c2s_adapter = Code2SchemaAdapter()
    resp = raw.get("response")
    if not isinstance(resp, Code2SchemaMetricResponse):
        resp = Code2SchemaMetricResponse(
            status=raw.get("status", "OK" if raw.get("entities") is not None else "ERROR"),
            entities=raw.get("entities", ()),
            error_message=raw.get("error_message"),
        )
    return c2s_adapter.normalize(query, resp, side=side)


def _planfile_tickets(raw: Dict[str, Any]) -> tuple:
    tickets_obj = []
    for t in raw.get("tickets", ()):
        if isinstance(t, PlanfileTicketEvidence):
            tickets_obj.append(t)
        elif isinstance(t, dict):
            tickets_obj.append(PlanfileTicketEvidence(
                ticket_id=t.get("ticket_id", ""),
                title=t.get("title", ""),
                status=t.get("status", "OPEN"),
                path=t.get("path", "planfile.yaml"),
                start_line=t.get("start_line", 1),
                end_line=t.get("end_line", 1),
                digest_sha256=t.get("digest_sha256"),
                media_type=t.get("media_type", "application/yaml"),
            ))
    return tuple(tickets_obj)


def _norm_planfile(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    planfile_adapter = PlanfileAdapter()
    resp = raw.get("response")
    if not isinstance(resp, PlanfileMetricResponse):
        resp = PlanfileMetricResponse(
            status=raw.get("status", "OK"),
            count=raw.get("count") if raw.get("count") is not None else raw.get("value"),
            tickets=_planfile_tickets(raw),
            path=raw.get("path", "planfile.yaml"),
            error_message=raw.get("error_message"),
        )
    return planfile_adapter.normalize(query, resp, side=side)


def _deta_services(raw: Dict[str, Any]) -> tuple:
    services_obj = []
    for s in raw.get("services", ()):
        if isinstance(s, DetaServiceEvidence):
            services_obj.append(s)
        elif isinstance(s, dict):
            services_obj.append(DetaServiceEvidence(
                name=s.get("name", ""),
                service_type=s.get("service_type", "service"),
                ports=s.get("ports", ()),
                manifest_path=s.get("manifest_path", "compose.yml"),
                start_line=s.get("start_line", 1),
                end_line=s.get("end_line", 1),
                digest_sha256=s.get("digest_sha256"),
            ))
    return tuple(services_obj)


def _norm_deta(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    deta_adapter = DetaAdapter()
    resp = raw.get("response")
    if not isinstance(resp, DetaTopologyResponse):
        service_cnt = raw.get("service_count") if raw.get("service_count") is not None else raw.get("value")
        resp = DetaTopologyResponse(
            status=raw.get("status", "OK"),
            service_count=service_cnt,
            services=_deta_services(raw),
            ports=tuple(raw.get("ports", ())),
            manifest_path=raw.get("manifest_path", "compose.yml"),
            error_message=raw.get("error_message"),
        )
    return deta_adapter.normalize(query, resp, side=side)


def _norm_intent(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    intent_adapter = IntentContractAdapter()
    resp = raw.get("response")
    if not isinstance(resp, IntentContractResponse):
        resp = IntentContractResponse(
            status=raw.get("status", "OK"),
            parties=raw.get("parties", ()),
            deliverables=raw.get("deliverables", ()),
            obligations=raw.get("obligations", ()),
            error_message=raw.get("error_message"),
        )
    return intent_adapter.normalize(query, resp, side=side)


def _norm_sumd(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    sumd_adapter = SUMDAdapter()
    resp = raw.get("response")
    if not isinstance(resp, SUMDMetricResponse):
        md_text = raw.get("markdown_content", "") or raw.get("text", "")
        metric_id = query.get("metric", {}).get("id", "metric")
        resp = sumd_adapter.extract_table_metric(
            markdown_text=md_text,
            metric_id=metric_id,
            path=raw.get("path", "document.sumd.md"),
            source_uri=raw.get("source_uri"),
            source_revision=raw.get("source_revision"),
        )
    return sumd_adapter.normalize(query, resp, side=side)


def _oql_telemetry_response(raw: Dict[str, Any]) -> OqlTelemetryLogResponse:
    return OqlTelemetryLogResponse(
        status=raw.get("status", "OK"),
        log_id=raw.get("log_id", "oql-telemetry-001"),
        path=raw.get("path", "logs/sensor.jsonl"),
        start_line=raw.get("start_line", 1),
        end_line=raw.get("end_line", 1),
        avg_sample_rate_hz=_coalesce_numeric(raw.get("avg_sample_rate_hz"), raw.get("sample_rate_hz"), raw.get("sample_rate")),
        peak_temperature_celsius=_coalesce_numeric(raw.get("peak_temperature_celsius"), raw.get("max_temperature_celsius"), raw.get("temperature")),
        observed_frequency_mhz=_coalesce_numeric(raw.get("observed_frequency_mhz"), raw.get("frequency_mhz")),
        avg_packet_throughput=_coalesce_numeric(raw.get("avg_packet_throughput"), raw.get("packet_throughput"), raw.get("throughput")),
        active_pins=raw.get("active_pins", ()),
        active_buses=raw.get("active_buses") or raw.get("buses", ()),
        error_message=raw.get("error_message"),
    )


def _oql_spec_response(raw: Dict[str, Any]) -> OqlScenarioSpecResponse:
    return OqlScenarioSpecResponse(
        status=raw.get("status", "OK"),
        scenario_id=raw.get("scenario_id", "oql-scenario-001"),
        path=raw.get("path", "scenarios/sensor.oql.json"),
        start_line=raw.get("start_line", 1),
        end_line=raw.get("end_line", 1),
        sample_rate_hz=_coalesce_numeric(raw.get("sample_rate_hz"), raw.get("sample_rate")),
        max_temperature_celsius=_coalesce_numeric(raw.get("max_temperature_celsius"), raw.get("temperature")),
        frequency_mhz=raw.get("frequency_mhz"),
        packet_throughput=_coalesce_numeric(raw.get("packet_throughput"), raw.get("throughput")),
        active_pins=raw.get("active_pins", ()),
        buses=raw.get("buses", ()),
        error_message=raw.get("error_message"),
    )


def _norm_oql(st: str, raw: Dict[str, Any], query: Dict[str, Any], side: str) -> Dict[str, Any]:
    oql_adapter = OqlTelemetryAdapter()
    is_telemetry = (
        st in ("oql_telemetry", "oqlos")
        or raw.get("kind") == "telemetry"
        or "log_id" in raw
        or "avg_sample_rate_hz" in raw
        or "peak_temperature_celsius" in raw
        or side == "right"
    )
    if is_telemetry and (raw.get("kind") != "spec" and "scenario_id" not in raw):
        resp = _oql_telemetry_response(raw)
    else:
        resp = _oql_spec_response(raw)
    return oql_adapter.normalize(query, resp, side=side)


_NORMALIZERS = {
    "markdown": _norm_markdown,
    "github": _norm_github,
    "curllm": _norm_curllm,
    "code2logic": _norm_code2logic,
    "code2schema": _norm_code2schema,
    "planfile": _norm_planfile,
    "deta": _norm_deta,
    "intent_contract": _norm_intent,
    "subactor_intent_contract": _norm_intent,
    "intentcontract": _norm_intent,
    "sumd": _norm_sumd,
    "oql": _norm_oql,
    "oqlos": _norm_oql,
    "oql_telemetry": _norm_oql,
    "oql_spec": _norm_oql,
}


