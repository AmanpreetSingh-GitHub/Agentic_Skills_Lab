---
name: clause-extraction
description: Extract relevant clauses from enterprise agreements, including financial, liability, termination, and compliance clauses.
---

# Clause Extraction Skill

## Purpose

Identify relevant clauses in an agreement so they can be used by other analysis skills.

## Instructions

1. Read the agreement text provided.
2. Understand the user's question.
3. Identify clauses relevant to the question.
4. Classify each clause into a category:
   - Financial
   - Liability
   - Termination
   - Compliance
   - Operational
   - Other
5. Preserve the original clause wording.
6. Record the clause number or section reference, if available.
7. Explain briefly why each clause is relevant.

## Output

For each relevant clause, return:

- Clause reference
- Category
- Original clause text
- Reason for selection

## Rules

- Never invent clauses or references.
- Never change the meaning of a clause.
- Do not treat missing information as proof that a clause does not exist.
- If the agreement is not provided, request it.
- Do not perform financial calculations or legal risk scoring.
- Leave risk assessment to other skills.
