---
name: compliance-analysis
description: Analyze compliance obligations, contractual protections, and potential compliance gaps in enterprise agreements, including privacy, security, audit rights, and regulatory requirements.
---

# Compliance Analysis Skill

## Purpose

Identify compliance-related obligations, missing protections,
and potential compliance gaps in an agreement.

## Instructions

1. Read the original agreement and understand the analysis objective.

2. If a specific compliance question is provided, focus on that question.
   Otherwise, perform a general compliance review of the supplied agreement.

3. Use extracted clauses from the Clause Extraction stage when available.
   Refer to the original agreement to verify supporting evidence.

4. Examine relevant areas, including:
   - Regulatory and contractual compliance obligations
   - Data protection and privacy
   - Confidentiality
   - Information security
   - Audit rights and recordkeeping
   - Subcontractor obligations
   - Compliance reporting

5. Identify:
   - Explicit compliance-related contractual obligations
   - Unclear or incomplete compliance provisions
   - Important protections not addressed in the supplied text

6. Distinguish missing provisions from proven violations.
   A missing clause is a potential contractual gap, not evidence
   that either party has violated a law or regulation.

7. For each finding:
   - Explain the concern in clear business language.
   - Identify the supporting agreement text when available.
   - Explain the potential business impact.
   - Recommend a practical follow-up action.

8. For findings tied to a specific clause, use only its numeric
   section identifier, such as "7.2".

9. For findings about protections absent from the supplied agreement,
   use null for both section and supporting_text.

10. Do not perform financial risk scoring or financial calculations.
    Leave those responsibilities to the Financial Risk skill.

## Output

For each compliance finding, provide:

- Section identifier, or null
- Compliance concern
- Supporting agreement text, or null
- Potential business impact
- Recommended action

Also provide an overall compliance assessment.

## Rules

- Base findings only on the supplied agreement and available evidence.
- Never invent regulations, obligations, clauses, or supporting text.
- Do not assume a missing clause means legal non-compliance.
- Distinguish potential risks from established violations.
- If the agreement provides insufficient evidence, say so.
- Do not make definitive legal conclusions.
- Do not treat hypothetical financial figures as contractual obligations.
