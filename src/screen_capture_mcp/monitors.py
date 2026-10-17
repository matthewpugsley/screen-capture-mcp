"""Monitor discovery and selection.

Monitors are numbered by physical layout (left to right, then top to bottom)
rather than by the OS enumeration order, which is arbitrary and often puts
the right-hand screen first.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PRIMARY = "primary"
ALL = "all"


@dataclass(frozen=True)
class Monitor:
    number: int  # 1-based, in layout order; 0 means the combined virtual screen
    left: int
    top: int
    width: int
    height: int
    is_primary: bool
    name: str

    @property
    def region(self) -> dict[str, int]:
        """The bounding box in the shape mss.grab() expects."""
        return {"left": self.left, "top": self.top, "width": self.width, "height": self.height}

    def describe(self) -> str:
        label = "all screens combined" if self.number == 0 else f"monitor {self.number}"
        primary = " (primary)" if self.is_primary else ""
        return f"{label}{primary}: {self.width}x{self.height} at ({self.left}, {self.top})"


def from_mss(raw_monitors: list[dict[str, Any]]) -> tuple[Monitor, list[Monitor]]:
    """Convert mss's monitor list into (virtual_screen, physical_monitors_in_layout_order).

    mss puts the combined virtual screen at index 0 and physical monitors after it.
    """
    if len(raw_monitors) < 2:
        raise RuntimeError("No monitors detected.")

    virtual_raw, physical_raw = raw_monitors[0], raw_monitors[1:]
    ordered = sorted(physical_raw, key=lambda m: (m["left"], m["top"]))
    monitors = [_to_monitor(raw, number) for number, raw in enumerate(ordered, start=1)]

    # Some platforms don't report is_primary; treat the monitor at the origin as primary.
    if not any(m.is_primary for m in monitors):
        monitors = [
            Monitor(**{**m.__dict__, "is_primary": (m.left, m.top) == (0, 0)}) for m in monitors
        ]

    virtual = _to_monitor(virtual_raw, 0)
    return virtual, monitors


def resolve(selector: str, virtual: Monitor, monitors: list[Monitor]) -> Monitor:
    """Pick a monitor from a user-facing selector: 'primary', 'all', or a layout number."""
    key = selector.strip().lower()
    if key == ALL or key == "0":
        return virtual
    if key == PRIMARY:
        return next((m for m in monitors if m.is_primary), monitors[0])
    if key.isdigit():
        number = int(key)
        for m in monitors:
            if m.number == number:
                return m
    valid = ", ".join([PRIMARY, ALL] + [str(m.number) for m in monitors])
    raise ValueError(f"Unknown monitor {selector!r}. Valid choices: {valid}.")


def _to_monitor(raw: dict[str, Any], number: int) -> Monitor:
    return Monitor(
        number=number,
        left=int(raw["left"]),
        top=int(raw["top"]),
        width=int(raw["width"]),
        height=int(raw["height"]),
        is_primary=bool(raw.get("is_primary", False)),
        name=str(raw.get("name", "")),
    )
