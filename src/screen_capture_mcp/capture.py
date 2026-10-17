"""Screen capture via mss. Each call opens a fresh mss handle so nothing is held between requests."""

from __future__ import annotations

from dataclasses import dataclass

import mss
from PIL import Image

from . import imaging, monitors
from .monitors import Monitor


@dataclass(frozen=True)
class Capture:
    data: bytes
    image_format: str
    monitor: Monitor
    sent_size: tuple[int, int]

    def caption(self) -> str:
        w, h = self.sent_size
        return f"Captured {self.monitor.describe()}; sent as {w}x{h} {self.image_format.upper()}."


def detect_monitors() -> tuple[Monitor, list[Monitor]]:
    with mss.MSS() as sct:
        return monitors.from_mss(sct.monitors)


def capture(selector: str, max_dimension: int, image_format: str) -> Capture:
    fmt = imaging.normalize_format(image_format)
    with mss.MSS() as sct:
        virtual, physical = monitors.from_mss(sct.monitors)
        target = monitors.resolve(selector, virtual, physical)
        shot = sct.grab(target.region)

    image = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
    image = imaging.downscale(image, max_dimension)
    return Capture(
        data=imaging.encode(image, fmt),
        image_format=fmt,
        monitor=target,
        sent_size=image.size,
    )
