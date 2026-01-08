from typing import List, Optional, Dict, Any, Union
from mcp.server.fastmcp import FastMCP
from ..sdk.core import FoodAgentSDK

# Initialize MCP server
mcp = FastMCP("food-agent")

# Initialize SDK
sdk = FoodAgentSDK()

@mcp.tool()
async def log_meal(
    food_entries: List[dict],
    entry_date: Optional[str] = None
) -> dict[str, Any]:
    """
    Log one or more food items as a meal for a specific date.
    
    IMPORTANT: The client agent (YOU) must follow this strict protocol before calling this tool:
    1.  **Catalog First:** Always search the existing catalog for a "non-fuzzy, confident match" 
        to use as the source of truth for nutrition info.
    2.  **Web Verification:** If the item is not in the catalog, perform a live web search 
        to find the official standard serving size and nutrition facts (e.g., from the manufacturer).
    3.  **Precise Calculation:** Calculate the nutrition for the specific amount consumed based 
        on the established standard serving data. Faithfully capture the actual results of your 
        calculation without any manual rounding. This ensures that server-side daily totals do not 
        suffer from an accumulation of rounding errors. The system will handle FDA-compliant 
        rounding when data is retrieved for display.
    4.  **Catalog Update:** If you had to look up new nutrition info and are "uber confident" 
        in its accuracy, you should ALSO call 'add_food_to_catalog' to save it for future use.

    **CRITICAL HABIT PROTOCOL:**
    If there is ANY indication that the user eats a particular food frequently (daily, weekly, or as a habit),
    it is CRITICAL to retrieve solid, authoritative nutritional information for that item FIRST before
    calling this tool. You MUST ensure this accurate info is stored in the catalog (via 'add_food_to_catalog')
    correctly. A mistake here could have a broad ongoing impact on misrepresenting the health impacts of 
    the user's diet. If necessary, triage with the user to ensure the most accurate data is cataloged 
    for such an item.

    Args:
        food_entries: A list of food objects. Each object MUST follow this schema:
            {
              "food_name": "Standard Name",
              "user_description": "User's exact words",
              "standard_serving": {
                "size": { "amount": number, "unit": "string" },
                "nutrition": { "calories": number, "protein": number, "carbs": number, "fat": number, ... }
              },
              "consumed": {
                "size": { "amount": number, "unit": "string" },
                "standard_servings": number,
                "nutrition": { 
                    "calories": number, "protein": number, "carbs": number, "fat": number, ... 
                    # IMPORTANT: Capture the actual results of your calculation faithfully 
                    # without rounding (e.g. preserve decimals if they exist).
                },
                "verified_calculation": boolean
              },
              "confidence_score": number (0-10),
              "source_notes": "string"
            }
        entry_date: Optional date string in "YYYY-MM-DD" format. 
                    Defaults to 'effective today' (adjusts for early morning cutoff).
    
    Returns:
        A dictionary indicating success and the path to the updated log file.
        IMPORTANT: After a successful log, you should call get_food_log() to retrieve 
        and display the updated daily totals and all items logged for that day 
        (including the one(s) just added) to the user.
    """
    return sdk.log_food(food_entries, entry_date)

@mcp.tool()
async def get_food_log(
    entry_date: Optional[str] = None,
    include: str = "all",
    filter: Optional[Union[str, List[str]]] = None,
    use_regex: bool = False
) -> dict[str, Any]:
    """
    Retrieve food log entries for a specific date.
    Nutritional totals (calories and macros) are always included and calculated 
    based on the items returned (post-filter).
    
    Args:
        entry_date: Optional date string (YYYY-MM-DD). 
                    Defaults to 'effective today' (adjusts for early morning cutoff).
        include: Options: 
                 'all' (both items and totals - DEFAULT),
                 'totals' (only the nutritional totals).
        filter: Optional string or list of strings to filter entries by name or description.
                Supports wildcards (e.g. '*coffee*') or regex if use_regex is True.
        use_regex: If True, treat filter strings as regular expressions.

    Returns:
        The requested food log data including totals and optionally items.
    """
    return sdk.get_food_log(entry_date, include, filter, use_regex)

@mcp.tool()
async def show_food_catalog(
    filter: Optional[Union[str, List[str]]] = None,
    use_regex: bool = False
) -> dict[str, Any]:
    """
    Retrieve items from the food catalog, optionally filtering by name.

    Args:
        filter: Optional string or list of strings to filter food names by (case-insensitive).
                If a list is provided, items matching ANY of the strings are returned.
                Supports wildcards (e.g. '*milk*') or regex if use_regex is True.
        use_regex: If True, treat filter strings as regular expressions.

    Returns:
        A list of catalog entries.
    """
    return sdk.get_catalog(filter, use_regex)

@mcp.tool()
async def add_food_to_catalog(food_item: Dict) -> dict[str, Any]:
    """
    Add a new verified food item to the catalog.
    
    CRITICAL: Only add items that have been verified against official, accurate 
    nutrition information (e.g., from a web search of the product's official label). 
    The 'standard_serving' MUST reflect the official serving size as published 
    by the manufacturer or a reliable authority. If verified, accurate info 
    is not available, do NOT add the item to the catalog.
    
    If the official source provides more precise (unrounded) nutritional data 
    than a standard label, prefer that precision to improve long-term tracking 
    accuracy for frequently consumed items.

    Args:
        food_item: A food item object following the schema (must have 'food_name', 'standard_serving', etc.).

    Returns:
        Success status.
    """
    return sdk.add_to_catalog(food_item)

@mcp.tool()
async def update_food_in_catalog(food_name: str, updates: Dict) -> dict[str, Any]:
    """
    Update an existing food item in the catalog.
    
    CRITICAL: Ensure that updates use verified, accurate nutrition information 
    from official sources. The 'standard_serving' should always reflect the 
    official serving size as published by the manufacturer.
    
    Prefer precise, unrounded values if available from authoritative sources 
    to prevent the accumulation of rounding errors in daily totals.

    Args:
        food_name: The name of the food item to update.
        updates: A dictionary of fields to update.

    Returns:
        Success status.
    """
    return sdk.update_catalog_item(food_name, updates)

@mcp.tool()
async def remove_food_from_catalog(food_name: str) -> dict[str, Any]:
    """
    Remove a food item from the catalog.

    Args:
        food_name: The name of the food item to remove.

    Returns:
        Success status.
    """
    return sdk.remove_from_catalog(food_name)

@mcp.tool()
async def set_food_log_data_folder(path: Optional[str] = None) -> dict[str, Any]:
    """
    Set the folder where food logs and catalog are stored.
    This updates the settings.json file in the config directory.

    Args:
        path: The absolute path to the data folder. 
              Pass an empty string or null to reset to default (XDG Data Home).

    Returns:
        Success status.
    """
    return sdk.set_data_folder(path)

def run_server():
    """Run the MCP server with stdio transport."""
    mcp.run()