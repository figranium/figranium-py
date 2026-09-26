import os

from figranium import Figranium, FigraniumError, Task, actions, variable

task: Task = {
    "name": "Example search",
    "description": "Searches a page and extracts its visible content",
    "url": "https://example.com",
    "mode": "agent",
    "variables": {"query": {"type": "string", "value": "figranium"}},
    "actions": [
        actions.wait_for("body"),
        actions.set("activeQuery", variable("query")),
        actions.get_content("body", "pageText"),
    ],
}

try:
    with Figranium(
        base_url=os.getenv("FIGRANIUM_BASE_URL", "http://localhost:11345"),
        api_key=os.getenv("FIGRANIUM_API_KEY", ""),
    ) as client:
        saved = client.tasks.save(task)
        result = client.run_task(saved["id"], {"variables": {"query": "browser automation"}})
        print(result.get("data"))
except FigraniumError as error:
    print(error.status, error.code, str(error))
