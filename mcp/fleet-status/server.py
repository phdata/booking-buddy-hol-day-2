"""
Fleet Status MCP Server

Exposes ship availability and cabin pricing as MCP tools.
Start with: python3 mcp/fleet-status/server.py

Wire up in Claude Code settings:
  .claude/settings.json → mcpServers → fleet-status
"""

import json
import sys


SHIPS = {
    1: {"name": "Black Pearl", "status": "active", "home_port": "New York, NY"},
    2: {"name": "Flying Dutchman", "status": "active", "home_port": "Los Angeles, CA"},
    3: {"name": "Queen Anne's Revenge", "status": "active", "home_port": "Seattle, WA"},
    4: {"name": "Wicked Wench", "status": "active", "home_port": "Miami, FL"},
}

CABIN_RATES = {
    "interior": 129.0,
    "ocean_view": 179.0,
    "balcony": 249.0,
    "suite": 549.0,
}

# Guest sailing assignments — duplicates contact info from guest-contacts intentionally
# to create tool sprawl (the point of Act 3b)
GUEST_SAILINGS = {
    1: {"guest_name": "Margaret Thornton", "email": "margaret.thornton@email.com", "ship_id": 1, "sailing_date": "2026-06-15", "cabin_category": "balcony"},
    2: {"guest_name": "Carlos Reyes", "email": "creyes@email.com", "ship_id": 2, "sailing_date": "2026-07-01", "cabin_category": "ocean_view"},
    3: {"guest_name": "Patricia Kim", "email": "pkim@email.com", "ship_id": 3, "sailing_date": "2026-06-22", "cabin_category": "suite"},
    4: {"guest_name": "James Okafor", "email": "jokafor@email.com", "ship_id": 1, "sailing_date": "2026-07-10", "cabin_category": "interior"},
}


def handle_list_ships() -> dict:
    return {"ships": [{"ship_id": sid, **info} for sid, info in SHIPS.items()]}


def handle_get_ship_availability(ship_id: int, sailing_date: str) -> dict:
    ship = SHIPS.get(ship_id)
    if not ship:
        return {"error": f"Ship {ship_id} not found"}
    return {
        "ship_id": ship_id,
        "ship_name": ship["name"],
        "sailing_date": sailing_date,
        "available_cabins": {
            "interior": 42,
            "ocean_view": 18,
            "balcony": 11,
            "suite": 3,
        },
    }


def handle_get_cabin_pricing(ship_id: int, category: str, sailing_date: str) -> dict:
    if category not in CABIN_RATES:
        return {"error": f"Unknown category: {category}"}
    base_rate = CABIN_RATES[category]
    return {
        "ship_id": ship_id,
        "category": category,
        "sailing_date": sailing_date,
        "base_rate_usd": base_rate,
        "taxes_fees_usd": round(base_rate * 0.15, 2),
        "total_per_night_usd": round(base_rate * 1.15, 2),
    }


def handle_get_guest_sailing_info(guest_id: int) -> dict:
    info = GUEST_SAILINGS.get(guest_id)
    if not info:
        return {"error": f"No sailing found for guest {guest_id}"}
    ship = SHIPS.get(info["ship_id"])
    return {
        "guest_id": guest_id,
        "guest_name": info["guest_name"],
        "email": info["email"],
        "ship": ship["name"] if ship else "Unknown",
        "sailing_date": info["sailing_date"],
        "cabin_category": info["cabin_category"],
    }


TOOLS = [
    {
        "name": "list_ships",
        "description": "List all ships in the fleet with their status and home port",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_ship_availability",
        "description": "Check cabin availability for a specific ship and sailing date",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ship_id": {"type": "integer", "description": "Ship ID (1-4)"},
                "sailing_date": {"type": "string", "description": "Sailing date (YYYY-MM-DD)"},
            },
            "required": ["ship_id", "sailing_date"],
        },
    },
    {
        "name": "get_cabin_pricing",
        "description": "Get pricing for a cabin category on a specific ship and sailing date",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ship_id": {"type": "integer", "description": "Ship ID (1-4)"},
                "category": {"type": "string", "enum": ["interior", "ocean_view", "balcony", "suite"], "description": "Cabin category"},
                "sailing_date": {"type": "string", "description": "Sailing date (YYYY-MM-DD)"},
            },
            "required": ["ship_id", "category", "sailing_date"],
        },
    },
    {
        "name": "get_guest_sailing_info",
        "description": "Get a guest's contact details and current sailing assignment",
        "inputSchema": {
            "type": "object",
            "properties": {
                "guest_id": {"type": "integer", "description": "Guest ID"},
            },
            "required": ["guest_id"],
        },
    },
]


def main():
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
        except json.JSONDecodeError:
            continue

        method = request.get("method")
        req_id = request.get("id")

        if req_id is None:
            continue

        if method == "initialize":
            response = {
                "jsonrpc": "2.0", "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "fleet-status", "version": "1.0.0"},
                    "capabilities": {"tools": {}},
                },
            }
        elif method == "tools/list":
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
        elif method == "ping":
            response = {"jsonrpc": "2.0", "id": req_id, "result": {}}
        elif method == "tools/call":
            tool_name = request["params"]["name"]
            args = request["params"].get("arguments", {})
            if tool_name == "list_ships":
                result = handle_list_ships()
            elif tool_name == "get_ship_availability":
                result = handle_get_ship_availability(**args)
            elif tool_name == "get_cabin_pricing":
                result = handle_get_cabin_pricing(**args)
            elif tool_name == "get_guest_sailing_info":
                result = handle_get_guest_sailing_info(**args)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            response = {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
            }
        else:
            response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
