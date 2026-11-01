
# Agentic Skills Lab

### One Agent. Multiple Skills. Multiple MCP Tools.

A practical demonstration of how **Microsoft Agent Framework (MAF)**, **Agent Skills**, and **Model Context Protocol (MCP)** can work together to analyze supplier agreements.

This repository supports Episode 1 of The Agentic Evolution Paradox and provides a foundation for future agentic architecture experiments.

## 1. What This Demo Shows

The project uses:

- One MAF agent
- Three specialized Agent Skills
- Two MCP tools
- A deterministic, sequential workflow
- Agent-driven MCP tool invocation

The goal is to demonstrate how one agent can perform multiple specialized tasks without requiring a separate agent for every task.

## 2. Architecture

```text
                 ONE MAF AGENT
                       |
              MCP Tool Discovery
                       |
          +------------+------------+
          |                         |
     get_agreement        calculate_financial_exposure
          |                         |
          +------------+------------+
                       |
                Agreement Retrieval
                       |
                       v
              Clause Extraction
              [clause-extraction]
                       |
                       v
               Financial Risk
               [financial-risk]
                       |
                       v
             Compliance Analysis
             [compliance-analysis]
                       |
                       v
               Final Report
```

Python controls the stage sequence. The agent loads the named skill for each stage and decides whether to invoke an available MCP tool.

Both MCP tools are made available to each stage. Tool availability does not mean a tool is automatically executed.

## 3. Project Structure

```text
agentic-skills-lab/
├── main.py
├── mcp_server.py
├── requirements.txt
├── .gitignore
├── README.md
├── data/
│   └── supplier_agreement.txt
└── skills/
    ├── clause-extraction/
    │   └── SKILL.md
    ├── financial-risk/
    │   └── SKILL.md
    └── compliance-analysis/
        └── SKILL.md
```

## 4. Technologies

- Python
- Microsoft Agent Framework
- OpenAI integration for MAF
- Agent Skills
- Model Context Protocol (MCP)

Tested package versions are pinned in `requirements.txt`.

## 5. Setup

Create and activate a Python virtual environment.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Configure your OpenAI API key in your environment:

```powershell
$env:OPENAI_API_KEY = "YOUR_API_KEY"
```

Replace `YOUR_API_KEY` with your own key. Never commit an actual API key to GitHub.

The demo requires access to the OpenAI model configured in your environment or application.

## 6. Run the Demo

```powershell
python main.py
```

The application will:

1. Connect to the local MCP server and discover its tools.
2. Retrieve the sample supplier agreement using an agent-selected MCP tool.
3. Load the Clause Extraction skill and extract contractual clauses.
4. Load the Financial Risk skill and assess financial implications.
5. Invoke the financial exposure calculator when sufficient numerical inputs are available.
6. Load the Compliance Analysis skill and identify supported concerns.
7. Produce a consolidated agreement analysis report.

## 7. Agent Skills

### Clause Extraction

Identifies relevant contractual clauses, preserving their section references and supporting text.

### Financial Risk

Evaluates financial implications and uses the MCP calculator when the required inputs are available.

### Compliance Analysis

Identifies potential compliance concerns without treating missing information as proof of a violation.

## 8. MCP Tools

### get_agreement

Retrieves a supplier agreement from the local `data` directory.

### calculate_financial_exposure

Calculates the difference between an estimated loss and a liability cap based on fees paid during the previous 12 months.

The calculation is illustrative and does not determine legal recoverability.

## 9. Demonstrated Behavior

Two scenarios were tested.

**Scenario A: Financial inputs missing**

The agent loaded the Financial Risk skill but did not invoke the calculator because the required numerical inputs were unavailable.

**Scenario B: Financial inputs available**

The sample agreement included explicitly hypothetical financial values:

- Fees paid in the previous 12 months: INR 2,000,000
- Estimated loss: INR 3,500,000
- Amount above the liability cap: INR 1,500,000

The agent invoked `calculate_financial_exposure` and distinguished the hypothetical calculation from actual contractual exposure.

These tests demonstrate observed behavior in the sample runs. They do not establish statistical reliability or production readiness.

## 10. Design Decisions

**One agent, multiple skills**

Specialized analysis is organized into reusable skills rather than separate agents.

**Deterministic workflow**

Python controls the order of the stages to ensure predictable execution.

**Agent-driven tool invocation**

Both MCP tools are discovered and made available. The agent determines which tool to invoke based on its task.

**Explicit workflow state**

A Python dictionary passes outputs between stages. Fresh MAF sessions isolate the conversational context of each stage.

**No long-term memory requirement**

The demo does not require persistent agent memory or a vector database.

## 11. Limitations

This is an educational proof of concept, not a production-grade contract review system.

It does not include:

- A comprehensive legal or regulatory knowledge base
- Human approval and review workflows
- Persistent audit storage
- Large-scale evaluation
- Production security and access controls

Outputs should not be treated as legal advice.

## 12. Related Series

**The Agentic Evolution Paradox**

Exploring when adding more agents, tools, and architectural complexity improves outcomes, and when simpler designs may be more effective.

Episode 1 focuses on the relationship between **one agent, multiple skills, and MCP tools**.
