# solution-architect-spl

MCP server for solution architecture tasks, with bundled Hermes skills.

## Project Structure

```
├── pyproject.toml              # Package metadata, deps, tool config
├── main.py                     # CLI entry point (delegates to server)
├── README.md                   # This file
├── .env.example                # Template for local env vars
├── src/
│   └── solution_architect_spl/
│       ├── __init__.py
│       ├── server.py           # MCP stdio server wiring
│       ├── tools/
│       │   ├── __init__.py     # ToolRegistry
│       │   └── hello.py        # Example tool
│       ├── resources/
│       │   ├── __init__.py     # ResourceRegistry
│       │   └── principles.py   # Example resource
│       ├── prompts/
│       │   ├── __init__.py     # PromptRegistry
│       │   └── design_review.py # Example prompt
│       └── utils/
│           ├── __init__.py
│           └── logging.py      # structlog wrapper
├── skills/
│   └── solution-architect/
│       └── SKILL.md            # Hermes skill for architecture work
├── tests/
│   ├── test_tools.py
│   └── test_server.py
└── scripts/
    └── run_tests.sh            # ./scripts/run_tests.sh
```

## Quick Start

Install dependencies (uses `uv` or `pip`):

```bash
uv pip install -e ".[dev]"
# or
pip install -e ".[dev]"
```

Run the server manually:

```bash
python -m solution_architect_spl.server
# or
solution-architect-mcp
```

Run tests:

```bash
./scripts/run_tests.sh
```

## Adding a New Tool

1. Create a module under `src/solution_architect_spl/tools/<my_tool>.py`
2. Import the `registry` from `.` and call `registry.register(tool, handler)`
3. Add a test under `tests/`

The same pattern applies to resources (`resources/`) and prompts (`prompts/`).

## Hermes Skill

The `skills/solution-architect/SKILL.md` is a Hermes-compatible skill. To use it:

- Copy or symlink it into `~/.hermes/skills/solution-architect/SKILL.md`, or
- Keep it in-repo and load it directly if your agent supports in-repo skills.

## MCP Configuration

Add to your MCP client config (e.g. Claude Desktop or Hermes `config.yaml`):

```json
{
  "mcpServers": {
    "solution-architect": {
      "command": "uvx",
      "args": ["solution-architect-spl"]
    }
  }
}
```

Or for local development:

```yaml
mcp_servers:
  solution-architect:
    command: "python"
    args: ["-m", "solution_architect_spl.server"]
```
