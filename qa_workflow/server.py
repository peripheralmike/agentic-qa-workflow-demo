"""MCP tool boundary. Never executes generated Python or publishes reports."""

import json
from mcp.server.fastmcp import FastMCP
from .workflow import ROOT, run, run_path

mcp = FastMCP("Reviewed QA demo")


@mcp.tool()
def read_requirement() -> str:
    """Read the synthetic payment requirement and its unresolved question."""
    return (ROOT / "requirements/change-request.md").read_text()


@mcp.tool()
def run_demo_suite(seeded_bug: bool = False) -> dict:
    """Run the schema-validated offline plan against the local fixture; no model or external service calls."""
    return run(mode="offline", seeded_bug=seeded_bug)


@mcp.tool()
def get_run_results(run_id: str) -> dict:
    """Read immutable-by-convention evidence for a validated local run id."""
    folder = run_path(run_id)
    return {
        "review": json.loads((folder / "review.json").read_text()),
        "results": json.loads((folder / "results.json").read_text()),
    }


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
