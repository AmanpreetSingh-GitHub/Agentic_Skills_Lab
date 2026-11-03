# Agentic Skills Lab
**One logical agent · Three Agent Skills · Two MCP tools · Five workflow stages**

A reproducible architectural proof of concept using **Microsoft Agent Framework (MAF)**, **Agent Skills**, and the **Model Context Protocol (MCP)** to analyze a fictional supplier agreement.

This repository accompanies **The Agentic Evolution Paradox, Episode 1: Will Agent Skills Change How We Architect Multi-Agent Systems?**

## Development Approach: AI-Assisted Engineering
This project embraces **AI-assisted software engineering** as a deliberate development approach.

**OpenAI Codex and ChatGPT** were extensively used for implementation, debugging, code refinement, and documentation.

The architectural hypothesis, design decisions, experimental approach, and interpretation of results were human-directed, with AI serving as an engineering accelerator.

The objective was not to demonstrate manual coding proficiency, but to explore an architectural question through a working implementation, while maintaining human ownership of technical decisions and validation.

## The question
**Does every specialized task need its own agent, or can we separate reusable expertise from agent identity?**

This experiment demonstrates one possible design: a single MAF agent configuration is reused for specialist work, while a deterministic workflow controls the sequence, stage inputs, and validation. It is **not** a benchmark against multi-agent systems and does not establish that one agent is generally better.

## Architecture
```text
                   MAF WorkflowBuilder
                           |
                           v
  [1] Agreement Retrieval  -- MCP: get_agreement
                           |
                           v
  [2] Clause Extraction    -- Skill: clause-extraction
                           |
                           v
  [3] Financial Risk       -- Skill: financial-risk
                           |  MCP: calculate_financial_exposure
                           |       (when inputs are available)
                           v
  [4] Compliance Analysis  -- Skill: compliance-analysis
                           |
                           v
  [5] Final Report         -- Deterministic Python (no LLM call)
                           |
                           v
                 AgreementAnalysisReport
```

**Important architectural distinctions:**

- **One logical agent configuration:** The retrieval and three specialist stages reuse the same agent object. They are not four independently configured specialist agents.

- **Fresh sessions:** Each agent-driven stage creates a new conversational session; relevant prior results are passed explicitly in structured handoffs. This limits conversation carryover, but is **not** a security or runtime isolation guarantee.

- **Workflow-directed Skills:** The workflow prompts each specialist stage to load its named Skill. This experiment does **not** demonstrate autonomous Skill routing or discovery among competing Skills.

- **MCP tools:** The MCP server exposes agreement retrieval and an illustrative financial calculator. The agent can invoke the available tools; telemetry records observed calls.

- **Deterministic final stage:** Python assembles and revalidates the final report without another model call.

### Stage responsibilities
| Stage | Execution | Output / control |
| --- | --- | --- |
| Agreement Retrieval | Agent + `get_agreement` MCP tool | Original agreement text |
| Clause Extraction | Agent + `clause-extraction` Skill | Referenced clauses, checked against source text |
| Financial Risk | Agent + `financial-risk` Skill; calculator when inputs exist | Risks and optional hypothetical exposure; reference and arithmetic checks |
| Compliance Analysis | Agent + `compliance-analysis` Skill | Potential concerns and gaps; section-reference checks |
| Final Report | Python executor | Consolidated Pydantic report and final validation |

## Repository layout
```text
agentic-skills-lab/
├── app/
│   ├── __init__.py
│   ├── agent_factory.py      # Shared agent configuration and tool-call tracing
│   ├── executors.py          # Five workflow executors and structured handoffs
│   ├── models.py             # Pydantic data contracts
│   ├── telemetry.py          # Per-stage execution traces
│   ├── validators.py         # Deterministic checks
│   └── workflow.py           # MAF WorkflowBuilder entry point
├── data/
│   └── supplier_agreement.txt
├── skills/
│   ├── clause-extraction/SKILL.md
│   ├── financial-risk/SKILL.md
│   └── compliance-analysis/SKILL.md
├── mcp_server.py
├── requirements.txt
└── README.md
```

## Prerequisites and setup
- **Python 3.11** (the development environment used for this project).

- An **OpenAI API key**, with access to a compatible model supported by the installed MAF OpenAI integration.

- Internet access for model requests. The MCP server and sample agreement are local.

The repository pins `agent-framework-core==1.24.0`, `agent-framework-openai==1.18.0`, `mcp==2.3.0`, and `tenacity==9.2.1` in `requirements.txt`. Other packages may be installed transitively.

From the repository root, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENAI_API_KEY = "YOUR_API_KEY"
python -m app.workflow
```

The code constructs `OpenAIChatClient()` without explicitly specifying a model. **Configure a supported model using the installed client's supported configuration mechanism** before running if your environment does not already provide one. The exact model-setting environment variable is not established by this repository, so this README intentionally does not invent one.

The workflow currently starts with `supplier_agreement.txt`, as specified in `app/workflow.py`. The MCP server reads it from `data/`.

## Sample agreement and calculation
The included agreement is fictional and contains payment, liability, and termination provisions plus a **separately identified illustrative financial scenario**. The Clause Extraction Skill excludes that scenario from operative contractual clauses; Financial Risk may use its explicitly hypothetical inputs for the demonstration.

| Illustrative input or output | Amount |
| --- | ---: |
| Fees paid in previous 12 months | INR 2,000,000 |
| Estimated loss | INR 3,500,000 |
| Illustrative liability cap | INR 2,000,000 |
| Estimated amount above cap | INR 1,500,000 |

The calculator applies the **sample agreement's simplified assumption** that the liability cap equals fees paid during the preceding 12 months. The amount above the cap is a mathematical illustration, **not** a determination of liability, recoverability, or legal outcome.

If sufficient inputs are missing, the Financial Risk Skill instructs the agent to leave `exposure` as `null` and explain the limitation. The executor requires an observed calculator call **when a calculated exposure is reported**. It does not independently verify that the model copied every calculator result faithfully.

## Validation and telemetry
The implementation uses several distinct checks:

1. **Pydantic contracts:** Validate required fields, types, permitted risk levels, and reject unexpected fields.

2. **Clause evidence checks:** Require extracted clause text and section references to appear in the supplied agreement.

3. **Financial checks:** Require risk section references to exist and verify the illustrative calculation's arithmetic and finite values.

4. **Compliance checks:** Require non-null section references to correspond to extracted clauses.

5. **Skill verification:** Check whether the required Skill load was observed during each specialist stage.

6. **Final validation:** Reapply report-level checks before emitting the consolidated report.

Stage telemetry reports **PASS/FAIL**, duration, observed Skill loads, observed MCP calls, and errors. These are execution checks, **not** independent assessments of legal interpretation, financial risk accuracy, or production reliability.

The retrieval executor also checks that a `get_agreement` invocation was observed and rejects obvious tool-error text. This is a safeguard, **not a cryptographic guarantee** that the agent returned the exact original tool payload.

## What the experiment demonstrated
In **one previously observed successful execution**, all five workflow stages completed:

| Stage | Observed result |
| --- | --- |
| Agreement Retrieval | PASS |
| Clause Extraction | PASS |
| Financial Risk | PASS |
| Compliance Analysis | PASS |
| Final Report | PASS |

The observed run included agreement retrieval, specialist Skill loading, an MCP-based financial calculation, structured handoffs, and deterministic final report assembly.

**What it does not prove:**

- Lower cost, latency, or higher accuracy than a multi-agent alternative.

- Statistical reliability across contracts, prompts, or model versions.

- Autonomous Skill selection or cross-agent Skill portability.

- Independent agent permissions, identity, or security boundaries.

- Production-grade governance, human approvals, persistent audit storage, or legal correctness.

## Architectural takeaway
**Skills package specialist instructions. MCP tools expose capabilities. Workflows coordinate execution. Agents provide model-driven execution and, where required, distinct operational boundaries.** These are complementary design choices, not interchangeable concepts.

The architectural question is therefore not simply *how many agents can we remove?* It is **where independent agent boundaries are genuinely needed**, and where reusable Skills plus explicit orchestration are sufficient.

This is an educational proof of concept, **not legal advice or a production contract-review solution**.
