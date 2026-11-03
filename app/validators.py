"""Deterministic checks for agreement-analysis stage outputs.

These checks verify source references and calculation consistency, not
legal correctness or the accuracy of model-generated interpretations.
"""

import math
import re

from app.models import (
    AgreementAnalysisReport,
    AgreementDocument,
    ClauseExtractionResult,
    ComplianceAnalysisResult,
    FinancialRiskResult,
)


def normalize_text(value: str) -> str:
    """Normalize whitespace and common quotation differences."""
    value = value.replace("\u2018", "'").replace("\u2019", "'")
    value = value.replace("\u201c", '"').replace("\u201d", '"')
    return " ".join(value.split()).casefold()


def validate_clauses(
    agreement: AgreementDocument,
    result: ClauseExtractionResult,
) -> None:
    """Check extracted clause text and section references against the source."""
    source = normalize_text(agreement.content)

    for clause in result.clauses:
        if normalize_text(clause.original_text) not in source:
            raise ValueError(
                f"Clause {clause.section}: original text "
                "was not found in the agreement."
            )

        section_pattern = rf"\bSection\s+{re.escape(clause.section)}\b"
        if not re.search(
            section_pattern,
            agreement.content,
            flags=re.IGNORECASE,
        ):
            raise ValueError(
                f"Clause {clause.section}: section reference "
                "was not found in the agreement."
            )


def validate_financial_risks(
    clauses: ClauseExtractionResult,
    result: FinancialRiskResult,
) -> None:
    """Check referenced sections and exposure arithmetic."""
    known_sections = {clause.section for clause in clauses.clauses}

    for risk in result.risks:
        if risk.section not in known_sections:
            raise ValueError(
                f"Financial risk references unknown section: {risk.section}"
            )

    exposure = result.exposure
    if exposure is None:
        return

    amounts = (
        exposure.fees_paid_last_12_months,
        exposure.estimated_loss,
        exposure.liability_cap,
        exposure.amount_above_cap,
    )
    if not all(math.isfinite(amount) for amount in amounts):
        raise ValueError("Financial exposure contains non-finite amounts.")

    expected_cap = exposure.fees_paid_last_12_months
    expected_above_cap = max(0, exposure.estimated_loss - expected_cap)

    if not math.isclose(
        exposure.liability_cap,
        expected_cap,
        rel_tol=1e-9,
        abs_tol=0.01,
    ):
        raise ValueError("Liability cap does not match the calculation inputs.")

    if not math.isclose(
        exposure.amount_above_cap,
        expected_above_cap,
        rel_tol=1e-9,
        abs_tol=0.01,
    ):
        raise ValueError("Amount above cap is mathematically incorrect.")


def validate_compliance(
    clauses: ClauseExtractionResult,
    result: ComplianceAnalysisResult,
) -> None:
    """Check that referenced clause sections exist."""
    known_sections = {clause.section for clause in clauses.clauses}

    for finding in result.findings:
        if finding.section is not None and finding.section not in known_sections:
            raise ValueError(
                f"Compliance finding references unknown section: {finding.section}"
            )


def validate_report(report: AgreementAnalysisReport) -> None:
    """Re-run stage validations on the assembled report."""
    validate_clauses(report.agreement, report.clauses)
    validate_financial_risks(report.clauses, report.financial_risks)
    validate_compliance(report.clauses, report.compliance)
