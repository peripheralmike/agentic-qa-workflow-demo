import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server = StdioServerParameters(
        command=sys.executable, args=["-m", "qa_workflow.server"]
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            names = [t.name for t in (await session.list_tools()).tools]
            assert set(names) == {
                "read_requirement",
                "run_demo_suite",
                "get_run_results",
            }
            requirement = await session.call_tool("read_requirement", {})
            assert not requirement.isError
            result = await session.call_tool("run_demo_suite", {"seeded_bug": False})
            assert not result.isError
            data = json.loads(result.content[0].text)
            assert data["passed"] == data["total"]
            evidence = await session.call_tool(
                "get_run_results", {"run_id": data["run_id"]}
            )
            assert not evidence.isError
            print(
                json.dumps(
                    {"tools": names, "run": data, "retrieved_results": True}, indent=2
                )
            )


if __name__ == "__main__":
    asyncio.run(main())
