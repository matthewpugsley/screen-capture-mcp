# screen-capture-mcp

A small local [MCP](https://modelcontextprotocol.io) server that lets an AI assistant (e.g. Claude Code) take a **single still screenshot** of one of your monitors, only when you ask it to.

- No web server, no background capture, no video stream. The assistant launches it over stdio and it grabs one frame per tool call.
- Images are downscaled (default 1568px on the long edge) to keep token cost reasonable while keeping text legible.
- Works on Windows, macOS, and Linux (via [`mss`](https://github.com/BoboTiG/python-mss)).

## Tools

| Tool | What it does |
|---|---|
| `list_monitors` | Lists monitors numbered **left to right** (1 = leftmost), with resolution, position, and which is primary. |
| `capture_screen` | Captures one monitor. `monitor`: `"primary"` (default), `"all"`, or a number. Optional `max_dimension` (256-4096) and `image_format` (`"jpeg"` default, or `"png"`). |

## Install

Requires [uv](https://docs.astral.sh/uv/).

```sh
git clone <this-repo-url> screen-capture-mcp
cd screen-capture-mcp
uv sync
```

### Register with Claude Code (all projects)

Substitute the absolute path to your clone:

```sh
claude mcp add --scope user screen-capture -- uv run --directory /absolute/path/to/screen-capture-mcp screen-capture-mcp
```

Restart Claude Code, then ask something like *"take a look at my left monitor."*

Claude Code asks permission before each tool call by default. To skip the prompt, allow `mcp__screen-capture__capture_screen` in your permissions.

## Notes

- **Games:** use *borderless fullscreen* or *windowed* mode. Exclusive fullscreen can produce black captures.
- **macOS:** grant your terminal the *Screen Recording* permission.
- **Privacy:** captures go to whatever model your client uses. Nothing is saved to disk.

## Development

```sh
uv run screen-capture-mcp   # runs the stdio server
```
