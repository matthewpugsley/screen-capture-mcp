"""MCP server exposing on-demand screenshots over stdio."""

from __future__ import annotations

from mcp.server.mcpserver import Image, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from . import capture as screen
from .imaging import DEFAULT_MAX_DIMENSION

server = MCPServer(
    name="screen-capture",
    instructions=(
        "Takes single still screenshots of the user's monitors. Only capture when the user "
        "asks you to look at their screen; never capture speculatively or repeatedly. "
        "Monitors are numbered left to right starting at 1. If the user has more than one "
        "monitor and it's unclear which they mean, call list_monitors first or ask."
    ),
)

_READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False)


@server.tool(annotations=_READ_ONLY)
def list_monitors() -> str:
    """List connected monitors with their numbers, resolutions, positions, and which is primary."""
    try:
        virtual, physical = screen.detect_monitors()
    except Exception as exc:
        raise ToolError(f"Could not detect monitors: {exc}") from exc
    lines = [m.describe() for m in physical]
    lines.append(f"'all' = {virtual.describe()}")
    return "\n".join(lines)


@server.tool(annotations=_READ_ONLY)
def capture_screen(
    monitor: str = "primary",
    max_dimension: int = DEFAULT_MAX_DIMENSION,
    image_format: str = "jpeg",
) -> list[str | Image]:
    """Take one screenshot of a monitor and return it as an image.

    Args:
        monitor: "primary", "all" (every screen stitched together), or a monitor number
            (1 = leftmost). See list_monitors.
        max_dimension: Longest edge of the returned image in pixels (256-4096). The default
            balances legibility and token cost; raise it only when small text is unreadable.
        image_format: "jpeg" (smaller, default) or "png" (lossless, crisper small text).
    """
    try:
        shot = screen.capture(monitor, max_dimension, image_format)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    except Exception as exc:
        raise ToolError(f"Screen capture failed: {exc}") from exc
    return [shot.caption(), Image(data=shot.data, format=shot.image_format)]


def main() -> None:
    server.run("stdio")


if __name__ == "__main__":
    main()
