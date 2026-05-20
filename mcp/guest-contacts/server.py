"""
Guest Contacts MCP Server

Exposes guest contact lookup and communication preference tools.
Start with: python3 mcp/guest-contacts/server.py

Wire up in Claude Code settings:
  .claude/settings.json → mcpServers → guest-contacts
"""

import json
import sys


GUEST_CONTACTS = {
    1: {"name": "Margaret Thornton", "email": "margaret.thornton@email.com", "preferred_channel": "email", "loyalty_tier": "Bronze"},
    2: {"name": "Carlos Reyes", "email": "creyes@email.com", "preferred_channel": "sms", "loyalty_tier": "Silver"},
    3: {"name": "Patricia Kim", "email": "pkim@email.com", "preferred_channel": "email", "loyalty_tier": "Silver"},
    4: {"name": "James Okafor", "email": "jokafor@email.com", "preferred_channel": "push", "loyalty_tier": "Silver"},
    5: {"name": "Susan Nakamura", "email": "snakamura@email.com", "preferred_channel": "email", "loyalty_tier": "Silver", "opted_in": False},
    6: {"name": "Robert Vasquez", "email": "rvasquez@email.com", "preferred_channel": "sms", "loyalty_tier": "Silver"},
    7: {"name": "Linda Chen", "email": "lchen@email.com", "preferred_channel": "email", "loyalty_tier": "Gold"},
    8: {"name": "William Osei", "email": "wosei@email.com", "preferred_channel": "email", "loyalty_tier": "Gold"},
}


def handle_lookup_guest(guest_id: int) -> dict:
    contact = GUEST_CONTACTS.get(guest_id)
    if not contact:
        return {"error": f"Guest {guest_id} not found"}
    return {"guest_id": guest_id, **contact}


def handle_get_communication_preferences(guest_id: int) -> dict:
    contact = GUEST_CONTACTS.get(guest_id)
    if not contact:
        return {"error": f"Guest {guest_id} not found"}
    return {
        "guest_id": guest_id,
        "preferred_channel": contact["preferred_channel"],
        "opted_in": contact.get("opted_in", True),
        "can_send_promotional": contact.get("opted_in", True) and contact.get("loyalty_tier") in ("Silver", "Gold"),
    }


TOOLS = [
    {
        "name": "lookup_guest",
        "description": "Look up a guest by ID to retrieve their contact details and loyalty tier",
        "inputSchema": {
            "type": "object",
            "properties": {
                "guest_id": {"type": "integer", "description": "Guest ID"},
            },
            "required": ["guest_id"],
        },
    },
    {
        "name": "get_communication_preferences",
        "description": "Get a guest's communication channel preferences and opt-in status",
        "inputSchema": {
            "type": "object",
            "properties": {
                "guest_id": {"type": "integer"},
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
                    "serverInfo": {"name": "guest-contacts", "version": "1.0.0"},
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
            if tool_name == "lookup_guest":
                result = handle_lookup_guest(**args)
            elif tool_name == "get_communication_preferences":
                result = handle_get_communication_preferences(**args)
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
