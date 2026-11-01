# mcp_server.py
# Creates a local MCP server using MCP SDK 2.x.
# Provides a tool to retrieve supplier agreements from the data folder.
# Restricts access to .txt files inside that folder.

from pathlib import Path

from mcp.server.mcpserver import MCPServer


# Create the MCP server.
mcp = MCPServer("Agreement Tools")

# Locate the agreement files.
DATA_FOLDER = Path(__file__).parent / "data"


@mcp.tool()
def get_agreement(filename: str) -> str:
    """Retrieve a supplier agreement by filename."""

    # Reject paths outside the agreement folder.
    if Path(filename).name != filename or filename in (".", ".."):
        return "Error: Provide a filename, not a file path."

    if not filename.endswith(".txt"):
        return "Error: Only .txt agreement files are supported."

    agreement_path = DATA_FOLDER / filename

    if not agreement_path.is_file():
        return f"Error: Agreement '{filename}' was not found."

    return agreement_path.read_text(encoding="utf-8")


@mcp.tool()
def calculate_financial_exposure(
    fees_paid_last_12_months: float,
    estimated_loss: float,
) -> dict:
    """Calculate potential financial exposure above a liability cap."""

    # Reject invalid financial inputs.
    if (
        not 0 <= fees_paid_last_12_months < float("inf")
        or not 0 <= estimated_loss < float("inf")
    ):
        return {"error": "Financial amounts must be finite and non-negative."}

    # Our sample liability clause caps supplier liability at fees
    # paid during the previous 12 months.
    liability_cap = fees_paid_last_12_months

    # Calculate the portion of estimated loss above the cap.
    amount_above_cap = max(0, estimated_loss - liability_cap)

    return {
        "liability_cap": liability_cap,
        "estimated_loss": estimated_loss,
        "amount_above_cap": amount_above_cap,
        "note": (
            "Illustrative calculation only. Actual recovery depends "
            "on the full agreement and applicable law."
        ),
    }


if __name__ == "__main__":
    # The MCP client communicates with this server over stdin/stdout.
    mcp.run(transport="stdio")
