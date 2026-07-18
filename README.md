# AD Forge

Runtime-agnostic MCP server for data-driven solution architecture, with bundled Hermes skills.

Works with any MCP stdio client (Claude Desktop, Hermes, OpenClaw, etc.). The core logic is also importable as plain Python packages.

Authors: Amirthanathan R (`amirth300324@gmail.com`) and Dhivya GL (`gldhivya1@gmail.com`).

## Project Structure

```
├── pyproject.toml              # Package metadata, deps, tool config
├── README.md                   # This file
├── CLAUDE.md                   # Guidance for Claude Code
├── .env.example                # Template for local env vars
├── Makefile                    # Common development targets
├── src/
│   └── adforge/
│       ├── __init__.py
│       ├── server.py           # MCP stdio server wiring
│       ├── models/             # Pydantic domain models
│       │   ├── problem.py
│       │   ├── solution.py
│       │   ├── sub_problem.py
│       │   ├── dag.py
│       │   └── cost.py
│       ├── persistence/        # SQLite repositories + migrations
│       │   ├── db.py
│       │   ├── migrations/
│       │   └── repositories/
│       ├── pricing/            # Cloud/role pricing provider wrappers
│       │   ├── aws.py
│       │   ├── azure.py
│       │   ├── gcp.py
│       │   ├── databricks.py
│       │   ├── roles.py
│       │   ├── cache.py (in repositories)
│       │   └── manager.py
│       ├── tools/              # MCP tool modules
│       │   ├── problem.py
│       │   ├── solution.py
│       │   ├── decompose.py
│       │   ├── cost.py
│       │   └── solution_cost.py
│       ├── prompts/            # MCP prompt modules
│       │   └── problem_decomposition.py
│       └── utils/
│           └── logging.py
├── skills/
│   └── solution-architect/
│       └── SKILL.md            # Hermes skill for architecture work
└── tests/
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
python -m adforge.server
# or
adforge-mcp
```

Run tests:

```bash
uv run pytest tests/ -q
```

## Workflow

1. **Capture a problem** — `create_problem(title, description, tags_csv)`.
2. **Decompose it** — use the `problem_decomposition` prompt, then call `decompose_problem(...)` to create sub-problems and a DAG.
3. **Create a solution** — `create_solution(problem_id, title, body)`.
4. **Attach costs** — `attach_cost_to_solution(...)` for each service/role/region.
5. **Summarize** — `summarize_solution_cost(solution_id)`.
6. **Review** — `add_solution_comment`, `add_solution_review`, `update_solution_status`.

## Pricing Sources

- **aws** — public AWS Price List Query API (`us-east-1`), no credentials required.
- **azure** — Azure Retail Prices API, no credentials required.
- **gcp** / **databricks** — stub providers; supply `manual_rate` in `parameters_json`.
- **role** — public/free role-pricing defaults; override with `manual_rate`.

## Hermes Skill

The `skills/solution-architect/SKILL.md` is a Hermes-compatible skill. To use it:

- Copy or symlink it into `~/.hermes/skills/solution-architect/SKILL.md`, or
- Keep it in-repo and load it directly if your agent supports in-repo skills.

## MCP Configuration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "adforge": {
      "command": "uvx",
      "args": ["adforge"]
    }
  }
}
```

Or for local development:

```yaml
mcp_servers:
  adforge:
    command: "uv"
    args: ["run", "python", "-m", "adforge.server"]
```

## Environment Variables

Copy `.env.example` to `.env` and adjust:

- `ADFORGE_DB_PATH` — SQLite file path.
- `ADFORGE_CACHE_TTL` — pricing cache TTL in seconds.
- `AWS_PRICING_REGION` — AWS region for pricing queries.
- `LOG_LEVEL`, `MCP_SERVER_NAME`.
