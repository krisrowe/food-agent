# Contributing to Food Agent

## Architecture

### SDK-first

All business logic lives in `food_agent/sdk/`. MCP tools and CLI commands are thin wrappers that call SDK methods and return the result.

```
food_agent/
  __init__.py         # APP_NAME constant
  sdk/
    core.py           # Food logging, catalog, entry management
    config.py         # Timezone, paths, XDG resolution, app config
    context.py        # User identity (re-exports from app-user)
    rounding.py       # FDA nutrition rounding
  mcp/
    server.py         # MCP tool definitions — one-liner wrappers
  cli/
    main.py           # Click CLI commands
  app.yaml            # Timezone and day boundary config
```

If you're writing logic in an MCP tool or CLI command, stop and move it to the SDK.

### SDK returns dicts

SDK methods return JSON-serializable dicts. Both MCP tools and CLI commands use the same return values. MCP tools return them directly. CLI formats for humans.

### User identity

User identity flows via `current_user_id` ContextVar (re-exported from `app_user.context`). In HTTP mode, app-user's middleware sets it from the JWT `sub` claim. In stdio mode, it defaults to `"default"` (single user). The SDK reads it — never imports FastMCP.

## Adding Features

1. **SDK first** — implement the feature in `sdk/core.py` or a new SDK module
2. **MCP tool** — add a thin async wrapper in `mcp/server.py` that calls the SDK method
3. **CLI command** (optional) — add a Click command in `cli/` that calls the SDK method
4. **Tests** — add sociable unit tests in `tests/unit/`

## Testing

### Sociable unit tests

- No mocks unless needed for network I/O
- Isolate via temp dirs and env vars (`FOOD_AGENT_DATA`, `FOOD_AGENT_CONFIG`)
- Tests use the same env vars the solution reads in production
- `tmp_path` fixture for data isolation

### Test names

Describe scenario + outcome:
- Good: `test_logs_food_to_current_date_directory`
- Bad: `test_returns_true_when_file_exists`

### Running tests

```bash
python -m pytest tests/unit/ -v
```

Integration tests in `tests/integration/` are excluded from default runs.

## Multi-User Auth

Food-agent uses [app-user](https://github.com/krisrowe/app-user) for JWT-based multi-user auth. The integration is in `mcp/server.py`:

- `FileSystemUserDataStore` — per-user directory storage
- `DataStoreAuthAdapter` — bridges auth store to data store
- `create_app()` — composes MCP + auth + admin into one ASGI app

Admin endpoints live at `/admin` on the running server. Users never see them — only MCP tools are visible to end users.

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `FOOD_AGENT_DATA` | Base data directory | `~/.local/share/food-agent/` |
| `FOOD_AGENT_CONFIG` | Config directory | `~/.config/food-agent/` |
| `SIGNING_KEY` | JWT signing key (HTTP mode) | `dev-key` |
| `JWT_AUD` | Token audience validation | None (skip) |
| `APP_USERS_PATH` | Per-user data directory | `~/.local/share/food-agent/users/` |
| `MCP_PATH` | MCP endpoint path | `/` |

## Code Conventions

- Python 3.10+
- Type hints on public methods
- Docstrings on MCP tools (user-centric, describe inputs/outputs/behavior)
- No hardcoded absolute paths — use env vars with XDG fallback
- DNS rebinding protection disabled (Cloud Run requirement)
