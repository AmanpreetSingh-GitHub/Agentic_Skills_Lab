---
name: compliance-analysis
description: Analyze compliance obligations, contractual protections, and potential compliance gaps in enterprise agreements, including privacy, security, audit rights, and regulatory requirements.
---

# Compliance Analysis Skill

## Purpose

Identify evidence-based compliance obligations and potential contractual protection gaps in the supplied agreement.

## Instructions

1. Read the original agreement. If a specific compliance question is provided, focus on it; otherwise perform a general review.
2. Use the extracted clauses when available, and check the original agreement for supporting evidence.
3. Consider relevant areas such as privacy, confidentiality, information security, audit rights, recordkeeping, subcontractors, regulatory obligations, and compliance reporting.
4. Distinguish explicit obligations, unclear provisions, and protections not addressed in the supplied text. Missing provisions are potential contractual gaps, **not** proof of a legal or regulatory violation.
5. For each finding, explain the concern, potential business impact, and a practical follow-up action. Include supporting agreement text when available.
6. For findings tied to a clause, use its numeric section identifier (for example, `7.2`), and ensure it refers to a section present in the extracted clauses.
7. For protections absent from the supplied agreement, set both `section` and `supporting_text` to `null`. Do not invent supporting text.
8. Provide an overall compliance assessment that clearly identifies uncertainty and limits of the available evidence.
9. Do not perform financial risk scoring or exposure calculations; those belong to the Financial Risk Skill.

## Output

Return findings containing:

- `section`: numeric section identifier or `null`
- `concern`: evidence-based compliance concern or potential gap
- `supporting_text`: agreement text or `null`
- `potential_impact`: potential business impact
- `recommended_action`: practical follow-up

Also return `overall_assessment`.

## Rules

- Base findings on the supplied agreement and available evidence.
- Never invent regulations, obligations, clauses, or supporting text.
- Do not equate missing contractual provisions with established non-compliance.
- Do not treat hypothetical financial figures as contractual obligations.
- Do not make definitive legal conclusions.
