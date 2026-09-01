"""Adapters for acquiring and normalizing facts from external sources into data2dsl observations."""

from data2dsl_adapter_parts.code2 import (
    Code2LogicAdapter,
    Code2LogicMetricResponse,
    Code2SchemaAdapter,
    Code2SchemaMetricResponse,
)
from data2dsl_adapter_parts.common import (
    DEFAULT_CODE2LOGIC_EXTRACTOR,
    DEFAULT_CODE2SCHEMA_EXTRACTOR,
    DEFAULT_CURLLM_EXTRACTOR,
    DEFAULT_DETA_EXTRACTOR,
    DEFAULT_DIAGIT_EXTRACTOR,
    DEFAULT_INTENT_CONTRACT_EXTRACTOR,
    DEFAULT_MDFLOW_EXTRACTOR,
    DEFAULT_OQL_EXTRACTOR,
    DEFAULT_PLANFILE_EXTRACTOR,
    DEFAULT_SUMD_EXTRACTOR,
    SCHEMA_OBSERVATION,
    compute_sha256,
)
from data2dsl_adapter_parts.curllm import CurllmAdapter, CurllmMetricResponse, CurllmPageEvidence
from data2dsl_adapter_parts.deta import DetaAdapter, DetaServiceEvidence, DetaTopologyResponse
from data2dsl_adapter_parts.diagit import (
    DiagitCommitMetricResponse,
    DiagitPageEvidence,
    GitHubDiagitAdapter,
    build_github_commit_observation,
)
from data2dsl_adapter_parts.intent import IntentContractAdapter, IntentContractResponse
from data2dsl_adapter_parts.markdown import MarkdownClaim, WorkSummaryMarkdownAdapter
from data2dsl_adapter_parts.oql import OqlScenarioSpecResponse, OqlTelemetryAdapter, OqlTelemetryLogResponse
from data2dsl_adapter_parts.planfile import PlanfileAdapter, PlanfileMetricResponse, PlanfileTicketEvidence
from data2dsl_adapter_parts.sumd import SUMDAdapter, SUMDMetricResponse

__all__ = [
    "DEFAULT_CODE2LOGIC_EXTRACTOR",
    "DEFAULT_CODE2SCHEMA_EXTRACTOR",
    "DEFAULT_CURLLM_EXTRACTOR",
    "DEFAULT_DETA_EXTRACTOR",
    "DEFAULT_DIAGIT_EXTRACTOR",
    "DEFAULT_INTENT_CONTRACT_EXTRACTOR",
    "DEFAULT_MDFLOW_EXTRACTOR",
    "DEFAULT_OQL_EXTRACTOR",
    "DEFAULT_PLANFILE_EXTRACTOR",
    "DEFAULT_SUMD_EXTRACTOR",
    "SCHEMA_OBSERVATION",
    "Code2LogicAdapter",
    "Code2LogicMetricResponse",
    "Code2SchemaAdapter",
    "Code2SchemaMetricResponse",
    "CurllmAdapter",
    "CurllmMetricResponse",
    "CurllmPageEvidence",
    "DetaAdapter",
    "DetaServiceEvidence",
    "DetaTopologyResponse",
    "DiagitCommitMetricResponse",
    "DiagitPageEvidence",
    "GitHubDiagitAdapter",
    "IntentContractAdapter",
    "IntentContractResponse",
    "MarkdownClaim",
    "OqlScenarioSpecResponse",
    "OqlTelemetryAdapter",
    "OqlTelemetryLogResponse",
    "PlanfileAdapter",
    "PlanfileMetricResponse",
    "PlanfileTicketEvidence",
    "SUMDAdapter",
    "SUMDMetricResponse",
    "WorkSummaryMarkdownAdapter",
    "build_github_commit_observation",
    "compute_sha256",
]
