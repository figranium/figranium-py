import asyncio
import os

from figranium import AsyncFigranium


async def main() -> None:
    async with AsyncFigranium(
        base_url=os.getenv("FIGRANIUM_BASE_URL", "http://localhost:11345"),
        api_key=os.getenv("FIGRANIUM_API_KEY", ""),
    ) as client:
        result = await client.run_task("example-task", {"variables": {"query": "Python SDK"}})
        print(result.get("data"))


if __name__ == "__main__":
    asyncio.run(main())
