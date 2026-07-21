"""Ad-hoc verification of the WPMCP server surface (not part of the package)."""

import asyncio

from fastmcp import Client

import wpmcp.server as server


async def main() -> None:
    async with Client(server.mcp) as client:
        tools = await client.list_tools()
        print(f"TOOLS ({len(tools)}):")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}".rstrip())

        resources = await client.list_resources()
        print(f"\nRESOURCES ({len(resources)}):")
        for resource in resources:
            print(f"  - {resource.uri}: {resource.name}")

        prompts = await client.list_prompts()
        print(f"\nPROMPTS ({len(prompts)}):")
        for prompt in prompts:
            print(f"  - {prompt.name}: {prompt.description}")

        discovery = await client.call_tool("wp_discover", {})
        sc = discovery.structured_content
        domains = sc["result"] if isinstance(sc, dict) and "result" in sc else sc
        total_actions = sum(len(d.get("actions", [])) for d in domains)
        print(f"\nwp_discover: {len(domains)} domain catalogs, {total_actions} total actions")
        for d in domains:
            print(f"  - {d.get('tool')}: {len(d.get('actions', []))} actions")


if __name__ == "__main__":
    asyncio.run(main())
