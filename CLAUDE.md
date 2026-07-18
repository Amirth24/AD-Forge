# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

**AD Forge** (`adforge`) is a runtime-agnostic MCP (Model Context Protocol) server for data-driven solution architecture, written in Python 3.13 and managed with `uv`. It is designed to work with Claude Desktop, Hermes, OpenClaw, and any other MCP stdio client.

It ships with:
- An MCP stdio server exposing tools, resources, and prompts.
- A Hermes-compatible skill under `skills/solution-architect/SKILL.md`.
- Plain importable Python packages (`models`, `persistence`, `pricing`) so other agents can reuse the logic directly without running the MCP server.

Authors: Amirthanathan R (`amirth300324@gmail.com`) and Dhivya GL (`gldhivya1@gmail.com`).

## Common commands

Use `uv run` for all project-local Python commands. It resolves the locked environment from `uv.lock`.

- **Install dev dependencies and editable package:** `uv pip install -e ".[dev]"`
- **Run the server locally:** `uv run python -m adforge.server`
- **Run the console-script entry point:** `uv run adforge-mcp`
- **Run all tests:** `uv run pytest tests/ -q`
- **Run a single test file:** `uv run pytest tests/test_tools.py -v`
- **Lint:** `uv run ruff check src/ tests/`
- **Format:** `uv run ruff format src/ tests/`
- **Type check:** `uv run mypy src/`

The `Makefile` provides the same targets (`install-dev`, `test`, `test-verbose`, `lint`, `format`, `check`, `clean`), but the project default is `uv run`.

To configure the server, copy `.env.example` to `.env`. Useful variables:
- `ADFORGE_DB_PATH` — SQLite file path (default: project root `adforge.db`).
- `ADFORGE_CACHE_TTL` — pricing cache TTL in seconds (default: 86400).
- `AWS_PRICING_REGION` — AWS region for pricing queries (default: `us-east-1`).
- `LOG_LEVEL`, `MCP_SERVER_NAME`.

## Architecture

The package lives at `src/adforge/`.

- **`server.py`** is the thin MCP entry point. It creates a single `mcp.server.Server` instance and wires the decorators (`list_tools`, `call_tool`, `list_resources`, `read_resource`, `list_prompts`, `get_prompt`) to the corresponding registries. Tool/prompt modules are imported at module load time so they self-register.
- **`tools/`**, **`resources/`**, and **`prompts/`** each contain a registry (`__init__.py`) and feature modules. A feature module imports the global `registry` and calls `registry.register(mcp_object, handler)` at import time. Tool/prompt handlers are async and accept flat JSON Schema input shapes for broad agent compatibility.
- **`models/`** holds Pydantic models: `Problem`, `Solution`, `SubProblem`, `SolutionNode`/`SolutionEdge` (DAG), and `CostLineItem`/`CostSummary`.
- **`persistence/`** is a SQLite-backed repository layer using plain `sqlite3`. `db.py` handles connections and SQL migrations under `persistence/migrations/`. Repositories: `ProblemRepository`, `SolutionRepository`, `SubProblemRepository`, `DagRepository`, `CostRepository`, plus `PricingCache`.
- **`pricing/`** contains provider wrappers: `aws` (AWS Price List API, requires explicit `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` env vars to avoid `botocore[crt]` credential chains), `azure` (Azure Retail Prices API, no credentials), `gcp`/`databricks` (stubs accepting `manual_rate`), and `roles` (public/free role-pricing defaults). `PricingManager` dispatches across providers and uses the SQLite `PricingCache`.
- **`utils/logging.py`** is a thin `structlog` wrapper.

To add a new tool, resource, or prompt: create a module under the appropriate directory, import the registry, call `registry.register(...)`, and import the module in `server.py`. Add a matching test under `tests/`. Keep tool input schemas flat and JSON Schema-compatible.

## Key workflow

1. `create_problem` stores a problem statement with tags.
2. `decompose_problem` breaks it into `SubProblem`s and, if given a `solution_id`, builds a sequential DAG.
3. `create_solution` produces a PR/issue-shaped `Solution` document.
4. `attach_cost_to_solution` fetches a price (AWS/Azure/role/etc.) and stores a `CostLineItem`.
5. `summarize_solution_cost` rolls up line items and writes a `CostSummary` back to the solution.
6. `add_solution_comment`, `add_solution_review`, and `update_solution_status` mirror GitHub PR/issue interactions.

## Hermes skill

`skills/solution-architect/SKILL.md` is a Hermes-compatible skill that describes the architecture workflow, design checklist, diagram conventions, and cost heuristics. It can be copied/symlinked into `~/.hermes/skills/solution-architect/` or loaded directly by clients that support in-repo skills.

## Notes

- Python 3.13 is required (`requires-python = ">=3.13"` in `pyproject.toml`, pinned in `.python-version`).
- `pyproject.toml` configures `ruff`, `mypy` (strict), and `pytest` (asyncio mode auto).
- `ruff check src/ tests/` and `mypy src/` are expected to pass.
- The README references `main.py` and `scripts/run_tests.sh`, but neither file currently exists in the repository; use the Makefile targets or `uv run` commands above instead.
