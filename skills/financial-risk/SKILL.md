---
name: financial-risk
description: Analyze financial and commercial risks in enterprise agreements, including payment obligations, liability caps, and financial exposure.
---

# Financial Risk Analysis Skill

## Purpose

Identify and explain financial risks in an agreement.

## Instructions

1. Read the original agreement and understand the analysis objective.

2. Use the clauses supplied by the Clause Extraction stage.
   Do not invent additional contractual obligations.

3. Analyze relevant financial and commercial risks, including:
   - Payment terms and deadlines
   - Pricing and price increases
   - Penalties and financial commitments
   - Liability caps and limitations
   - Minimum commitments
   - Termination costs and financial consequences

4. For each relevant clause:
   - Identify the financial risk.
   - Explain its potential business impact and the basis for the assessment.
   - Assign a risk level: Low, Medium, High, or Undetermined.
   - Recommend a practical action.

5. When the agreement provides sufficient numerical inputs
   for a financial exposure calculation:
   - Use the MCP tool `calculate_financial_exposure`.
   - Extract the numerical inputs from the original agreement.
   - Pass those values to the tool.
   - Use the tool's returned calculation in the analysis.

6. Distinguish contractual facts from hypothetical scenarios.
   If financial figures are explicitly hypothetical, label
   the resulting exposure as hypothetical.

7. If required financial inputs are missing, do not invent
   values or perform a fabricated calculation.
   Set `exposure` to null and explain why it cannot be quantified.
   Do not call the calculator.

## Rules

- Base contractual findings only on the supplied agreement.
- Preserve the section identifiers supplied by Clause Extraction.
- Never invent clauses, obligations, financial amounts, or tool results.
- Do not substitute unsupported inputs into the calculator.
- Do not present hypothetical figures as actual financial losses.
- Do not treat missing information as proof that a protection is absent.
- If evidence is insufficient, mark the risk level as Undetermined.
- Do not provide definitive legal conclusions.
- Leave compliance assessment to the Compliance Analysis skill.

## Output

For each financial risk, provide:

- Clause section identifier
- Risk identified
- Potential business impact
- Risk level: Low, Medium, High, or Undetermined
- Recommended action

Use the `business_impact` field to explain the assessment basis;
there is no separate reasoning field in the structured output.

For financial exposure, provide:

- Fees paid during the previous 12 months
- Estimated loss
- Liability cap
- Amount above the liability cap
- Currency
- Whether the figures are hypothetical
- Explanation of the calculation and its limitations

If inputs are insufficient, return `exposure: null` and explain the limitation
in `exposure_explanation`.
