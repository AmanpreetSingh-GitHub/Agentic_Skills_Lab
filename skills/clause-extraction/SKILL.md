---
name: clause-extraction
description: Extract relevant clauses from enterprise agreements, including financial, liability, termination, and compliance clauses.
---

# Clause Extraction Skill

## Purpose

Identify relevant clauses in an agreement so they can be used by other analysis skills.

## Instructions

1. Read the complete agreement provided.
2. Identify the analysis objective:
   - If a specific question is provided, select clauses relevant to it.
   - If no specific question is provided, identify material contractual
     clauses relevant to financial, liability, termination, compliance,
     and operational analysis.
3. Classify each selected clause into one category:
   - Financial
   - Liability
   - Termination
   - Compliance
   - Operational
   - Other
4. Extract only operative contractual clauses that establish
   rights, obligations, restrictions, or contractual protections.
5. Exclude illustrative examples, assumptions, and hypothetical
   financial scenarios from extracted clauses, even if they contain
   figures useful for later analysis.
6. Preserve the exact original wording of each selected clause.
7. Record only the numeric section identifier in the `section` field
   (for example, "4.1", not "Section 4.1").
8. Briefly explain why each selected clause is relevant.
9. Leave risk scoring, financial calculations, and compliance assessment
   to the other skills.


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
