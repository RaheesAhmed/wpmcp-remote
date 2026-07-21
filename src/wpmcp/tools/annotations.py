"""Reusable MCP safety annotations for model planning."""

READ_ONLY_TOOL = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}

WRITE_TOOL = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": False,
}

DESTRUCTIVE_TOOL = {
    "readOnlyHint": False,
    "destructiveHint": True,
    "idempotentHint": False,
    "openWorldHint": False,
}

# Gateway tools dispatch both reads and writes, so they are neither purely
# read-only nor purely destructive. Mark them as open-world (they call remote
# WordPress installs) and non-idempotent.
GATEWAY_TOOL = {
    "readOnlyHint": False,
    "destructiveHint": False,
    "idempotentHint": False,
    "openWorldHint": True,
}
