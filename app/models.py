"""Pydantic contracts for agreement analysis and workflow handoffs."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkflowModel(BaseModel):
    """Reject unexpected fields in workflow data."""

    model_config = ConfigDict(extra="forbid")


class AgreementDocument(WorkflowModel):
    filename: str = Field(min_length=1)
    content: str = Field(min_length=1)


class ContractClause(WorkflowModel):
    section: str = Field(min_length=1)
    category: str = Field(min_length=1)
    original_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class ClauseExtractionResult(WorkflowModel):
    clauses: list[ContractClause] = Field(min_length=1)


class FinancialRisk(WorkflowModel):
    section: str = Field(min_length=1)
    risk: str = Field(min_length=1)
    business_impact: str = Field(min_length=1)
    risk_level: Literal["Low", "Medium", "High", "Undetermined"]
    recommended_action: str = Field(min_length=1)


class FinancialExposure(WorkflowModel):
    fees_paid_last_12_months: float = Field(ge=0)
    estimated_loss: float = Field(ge=0)
    liability_cap: float = Field(ge=0)
    amount_above_cap: float = Field(ge=0)
    currency: str = Field(min_length=1)
    hypothetical: bool


class FinancialRiskResult(WorkflowModel):
    risks: list[FinancialRisk]
    exposure: FinancialExposure | None = None
    exposure_explanation: str = Field(min_length=1)


class ComplianceFinding(WorkflowModel):
    section: str | None = None
    concern: str = Field(min_length=1)
    supporting_text: str | None = None
    potential_impact: str = Field(min_length=1)
    recommended_action: str = Field(min_length=1)


class ComplianceAnalysisResult(WorkflowModel):
    findings: list[ComplianceFinding]
    overall_assessment: str = Field(min_length=1)


class AgreementAnalysisReport(WorkflowModel):
    agreement: AgreementDocument
    clauses: ClauseExtractionResult
    financial_risks: FinancialRiskResult
    compliance: ComplianceAnalysisResult


class ClauseExtractionHandoff(WorkflowModel):
    """Carry the agreement and extracted clauses to Financial Risk."""

    agreement: AgreementDocument
    clauses: ClauseExtractionResult


class FinancialRiskHandoff(WorkflowModel):
    """Carry validated findings to Compliance Analysis."""

    agreement: AgreementDocument
    clauses: ClauseExtractionResult
    financial_risks: FinancialRiskResult


class ComplianceAnalysisHandoff(WorkflowModel):
    """Carry all stage outputs to final report assembly."""

    agreement: AgreementDocument
    clauses: ClauseExtractionResult
    financial_risks: FinancialRiskResult
    compliance: ComplianceAnalysisResult
