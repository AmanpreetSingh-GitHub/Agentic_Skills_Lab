# Agentic Skills Lab

### One Agent. Three Skills. Two MCP Tools. Five Workflow Stages.

A practical demonstration of how **Microsoft Agent Framework (MAF)**, **Agent Skills**, and **Model Context Protocol (MCP)** can work together to analyze supplier agreements through a controlled workflow.

This repository supports Episode 1 of **The Agentic Evolution Paradox**.

## 1. Purpose

This experiment explores a central architectural question:

**How much specialized work can one AI agent perform using reusable skills, MCP tools, and controlled execution before separate specialized agents become necessary?**

The goal is to demonstrate a working design, not to prove that a single-agent architecture is universally better than a multi-agent architecture.

## 2. Architecture

The application uses:

- One logical MAF agent
- Three specialized Agent Skills
- Two MCP tools
- Five sequential workflow stages
- Fresh agent sessions for analysis stages
- Structured Pydantic handoffs
- Deterministic validation
- Stage-level telemetry
- A final report assembled without an additional LLM call

### Workflow

```text
                ONE LOGICAL MAF AGENT
                          |
                   MAF WorkflowBuilder
                          |
                          v
                Agreement Retrieval
                   MCP: get_agreement
                          |
                          v
                  Clause Extraction
                Skill: clause-extraction
                          |
                          v
                   Financial Risk
                  Skill: financial-risk
              MCP: calculate_financial_exposure
                          |
                          v
                 Compliance Analysis
                Skill: compliance-analysis
                          |
                          v
                     Final Report
                Deterministic Python
                          |
                          v
              AgreementAnalysisReport
```

The agent performs specialized tasks by loading the appropriate skills. MAF WorkflowBuilder controls stage execution and handoffs.

The final reporting stage does not create another agent or make an additional LLM call.

## 3. Project Structure

```text
agentic-skills-lab/
|-- app/
|   |-- __init__.py
|   |-- agent_factory.py
|   |-- executors.py
|   |-- models.py
|   |-- telemetry.py
|   |-- validators.py
|   `-- workflow.py
|-- data/
|   `-- supplier_agreement.txt
|-- skills/
|   |-- clause-extraction/
|   |   `-- SKILL.md
|   |-- financial-risk/
|   |   `-- SKILL.md
|   `-- compliance-analysis/
|       `-- SKILL.md
|-- mcp_server.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

## 4. Technologies

- Python 3.11
- Microsoft Agent Framework
- OpenAI integration for MAF
- Agent Skills
- Model Context Protocol
- Pydantic structured models
- MAF WorkflowBuilder

Dependency versions are pinned in `requirements.txt`.

## 5. Setup

Create a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Configure the OpenAI API key:

```powershell
$env:OPENAI_API_KEY = "YOUR_API_KEY"
```

Configure an available OpenAI model according to the application's model configuration.

Never commit API keys or other secrets.

## 6. Run the Workflow

From the project root:

```powershell
python -m app.workflow
```

The workflow will:

1. Discover the available MCP tools.
2. Retrieve the supplier agreement.
3. Load the Clause Extraction skill and extract relevant clauses.
4. Load the Financial Risk skill and assess financial implications.
5. Invoke the financial exposure calculator when appropriate.
6. Load the Compliance Analysis skill and identify supported concerns.
7. Assemble a structured final report.
8. Display stage-level execution telemetry.

## 7. Agent Skills

### Clause Extraction

Identifies contractual clauses and preserves their original wording and section references.

### Financial Risk

Assesses contractual financial risks, business impacts, and potential exposure.

### Compliance Analysis

Identifies potential compliance concerns while distinguishing missing contractual provisions from proven violations.

Each skill provides specialized instructions to the same logical agent.

## 8. MCP Tools

### get_agreement

Retrieves the sample supplier agreement from the local data directory.

### calculate_financial_exposure

Calculates illustrative financial exposure using supported numerical inputs.

For the supplied example:

- Fees paid during the previous 12 months: INR 2,000,000
- Estimated loss: INR 3,500,000
- Amount above the liability cap: INR 1,500,000

These values are hypothetical. The calculation does not establish actual legal recoverability.

## 9. Structured Handoffs and Validation

The workflow uses Pydantic models to exchange structured outputs between stages.

Key models include:

- AgreementDocument
- ClauseExtractionResult
- FinancialRiskResult
- ComplianceAnalysisResult
- AgreementAnalysisReport

Handoff models preserve the validated outputs required by subsequent stages.

Deterministic validation checks stage results before they proceed through the workflow.

## 10. Execution Telemetry

The application records:

- Stage execution status
- Stage duration
- Observed Agent Skill loading
- Observed MCP tool calls
- Execution failures

Telemetry provides visibility into how the workflow executed.

It does not independently prove the factual accuracy of every model-generated conclusion.

## 11. Demonstrated Results

A successful five-stage execution produced:

| Stage | Result |
|---|---|
| Agreement Retrieval | PASS |
| Clause Extraction | PASS |
| Financial Risk | PASS |
| Compliance Analysis | PASS |
| Final Report | PASS |

The final report included the original agreement, extracted clauses, financial risk findings, hypothetical financial exposure, and compliance assessment.

The Final Report stage completed without additional Agent Skill or MCP tool calls.

Earlier exploratory runs also demonstrated that the agent could avoid invoking the financial calculator when required numerical inputs were unavailable.

## 12. Design Decisions

**One logical agent:** Specialized behavior is supplied through reusable skills rather than separate agent identities.

**Controlled workflow:** MAF WorkflowBuilder determines stage sequencing.

**Fresh sessions:** Each agent-driven stage uses a fresh session to limit conversational context carryover.

**Structured handoffs:** Pydantic models carry validated information between stages.

**Deterministic validation:** Python checks structured results rather than relying exclusively on model self-assessment.

**MCP tool integration:** Tools are discovered and exposed to the agent, which invokes them according to the task.

**Deterministic final report:** Python assembles previously validated outputs without another model invocation.

## 13. Limitations

This is an architectural proof of concept, not a production contract-review system.

It does not establish:

- Statistical reliability across large contract datasets
- Superiority over specialized multi-agent systems
- Independent agent identities
- Production-grade security and access controls
- Comprehensive legal or regulatory analysis
- Persistent audit storage
- Human approval workflows

The demonstration uses a limited sample agreement and should not be treated as legal advice.

## 14. Related Series

**The Agentic Evolution Paradox**

Exploring when additional agents, tools, and architectural complexity improve outcomes, and when simpler architectures can provide similar capabilities.

Episode 1 investigates **one agent with multiple skills and MCP tools** as a foundation for future architectural comparisons.