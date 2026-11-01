---
name: financial-risk
description: Analyze financial risks in enterprise agreements, including payment obligations, pricing, penalties, liability caps, and financial exposure. Use when the user asks about financial or commercial risks.
---

# Financial Risk Analysis Skill

## Purpose

Identify and explain financial risks in an agreement.

## Instructions

1. Read the agreement and understand the user's question.
2. Identify clauses that create financial obligations or exposure.
3. Use relevant clauses identified by the Clause Extraction Skill when available.
4. Analyze risks involving:
   - Payment terms
   - Pricing and price increases
   - Penalties
   - Liability limits
   - Minimum commitments
   - Termination costs
5. Explain each risk in simple business language.
6. Identify missing information that could affect the assessment.

## Output

For each financial risk, provide:

- Clause reference
- Risk identified
- Why it matters
- Risk level: Low, Medium, or High
- Recommended action

## Rules

- Base findings only on the agreement provided.
- Never invent financial values or contractual obligations.
- Explain the reason for each risk level.
- Do not treat a missing clause as proof that a protection is absent.
- If evidence is insufficient, mark the risk level as Undetermined.
- Do not provide definitive legal conclusions.
