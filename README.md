# Food Agent

A specialized MCP agent for logging food consumption and managing a personal nutrition catalog.

## Overview

This project provides a Model Context Protocol (MCP) server that enables an AI assistant (like Gemini CLI) to:
1.  **Log Daily Meals:** Capture detailed nutritional data for food consumption.
2.  **Manage a Personal Catalog:** distinct from generic databases, this allows you to curate a list of frequently eaten foods with verified nutritional info.
3.  **Local Data Storage:** All data is stored in local JSON files, following XDG standards by default, with support for custom locations (e.g., for syncing).

## Installation

This project uses `pipx` for clean, isolated installation.

### Prerequisites
*   Python 3.10+
*   `pipx`

### Setup Steps

1.  **Install the Package:**
    Run the following command to install the agent in editable mode:
    ```bash
    make install
    ```
    *(Or manually: `pipx install -e . --force`)*

2.  **Verify Installation:**
    Before registering, verify that the server starts correctly. It should run without error (it waits for input, so we use `timeout` to stop it after 2 seconds):
    ```bash
    timeout 2s food-agent
    ```
    If this command fails (e.g., "command not found"), ensure your `pipx` bin folder is in your PATH.

3.  **Register with Gemini:**
    Add the MCP server to your Gemini configuration:
    ```bash
    make register
    ```
    *(Or manually: `gemini mcp add food-agent food-agent --stdio`)*

4.  **Restart Gemini:**
    If Gemini is already running, you must restart it to load the new tool:
    *   Type `/quit` to exit.
    *   Restart with `gemini -r` (to restore your session) or just `gemini`.

5.  **Final Verification:**
    Check that the tool is connected:
    ```bash
    gemini mcp list
    ```
    You should see `food-agent` listed with status `Connected`.
    
    **Try it out:** Once restarted, describe something you've eaten today (e.g., "I had a cup of coffee and a bagel") to verify the agent is working and to log your first entry!

## Quick Start (Repository Users & Contributors)

If you are using this repository directly or testing contributions, use these workflows to interact with the agent:

| Goal | Action |
| :--- | :--- |
| **Log a Meal** | "I had 2 scrambled eggs and a piece of whole wheat toast" |
| **Check Today's Log** | "Show me my food log for today" |
| **Search Catalog** | `gemini call food-agent show_food_catalog --filter "*milk*"` |
| **Set Data Path** | `gemini call food-agent set_food_log_data_folder --path "~/my-logs"` |

## Configuration

By default, data is stored in your XDG Data Home (`~/.local/share/food-agent`).

To change this (e.g., to a synced folder):
```bash
# Use the MCP tool
gemini call food-agent set_food_log_data_folder --path "~/Dropbox/FoodLogs"
```

Or manually set the `FOOD_AGENT_DATA` environment variable.

## Day Cutoff Logic

To accommodate users who stay up late, the agent supports a configurable "day cutoff" hour. If the current time is between midnight and this cutoff hour, the agent defaults to the previous calendar day when no date is specified.

This is configured in `food_agent/app.yaml`:
```yaml
day_cutoff_hour: 4  # New day starts at 4:00 AM
```

## Usage

Once registered, you can interact with the agent naturally:

> "I had a bowl of oatmeal with blueberries for breakfast."

The agent will:
1.  Check your personal catalog for "oatmeal" and "blueberries".
2.  If missing, search for nutritional data.
3.  Log the entry to `YYYY-MM-DD_food-log.json`.
4.  Optionally ask to save the new items to your catalog.

## Tools

### `log_meal`
Logs one or more food items as a meal for a specific date.
- **Args:** `food_entries` (List), `entry_date` (Optional String YYYY-MM-DD)

### `get_food_log`
Retrieves food log entries for a specific date. Nutritional totals are always included.
- **Args:** `entry_date` (String YYYY-MM-DD), `include` (String: 'all', 'totals'), `filter` (String or List)

### Catalog Management
- `show_food_catalog(filter)`: Search known foods (supports wildcards/lists).
- `add_food_to_catalog(food_item)`: Add a new verified food item.
- `update_food_in_catalog(food_name, updates)`: Update an existing entry.
- `remove_food_from_catalog(food_name)`: Remove an entry.

### Settings Management
- `set_food_log_data_folder(path)`: Set or reset the data storage path.

## Development

*   **Structure:**
    *   `food_agent/sdk/`: Core business logic and configuration.
    *   `food_agent/mcp/`: MCP server implementation.
*   **Commands:**
    *   `make clean`: Remove build artifacts.
