"""news-image-20261121, submit #2: hand the broadsheet to the grader.

The repository ships one picture, assets/entry.jpg: a one-page broadsheet
with 30 verified stories from Saturday 21 November 2026. This program does
nothing creative — it checks that the bundled picture is a whole 1024x1024
JPEG under the 1 MiB cap, then writes those exact bytes to entry.png. Both
grader runs therefore produce identical bytes. Python 3.13, standard
library only, no network access.
"""

import os
from pathlib import Path

ASSET_NAME = "entry.jpg"
ASSET_DIR = "assets"
OUT_NAME = "entry.png"
MAX_BYTES = 1048576
EXPECTED_SIZE = (1024, 1024)
SOI = b"\xff\xd8\xff"


def asset_path():
    """Absolute path of the bundled broadsheet next to this file."""
    return Path(__file__).resolve().parent / ASSET_DIR / ASSET_NAME


def load_asset():
    """Read the bundled picture, rejecting anything that is not a JPEG."""
    blob = asset_path().read_bytes()
    if len(blob) > MAX_BYTES:
        raise ValueError(f"bundled image is {len(blob)} bytes, over 1 MiB")
    if not blob.startswith(SOI):
        raise ValueError("bundled image does not start with a JPEG header")
    if not blob.rstrip(b"\x00").endswith(b"\xff\xd9"):
        raise ValueError("bundled image has no JPEG end marker")
    return blob


def jpeg_dimensions(blob):
    """Width and height from the first frame header (SOF0/SOF2)."""
    pos = 2
    while pos + 9 < len(blob):
        if blob[pos] != 0xFF:
            pos += 1
            continue
        marker = blob[pos + 1]
        if marker in (0xC0, 0xC2):
            height = int.from_bytes(blob[pos + 5:pos + 7], "big")
            width = int.from_bytes(blob[pos + 7:pos + 9], "big")
            return (width, height)
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        length = int.from_bytes(blob[pos + 2:pos + 4], "big")
        pos += 2 + length
    raise ValueError("no JPEG frame header found")


def emit(blob):
    """Write the checked bytes to the output directory as entry.png."""
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / OUT_NAME
    with open(target, "wb") as handle:
        handle.write(blob)
    os.chmod(target, 0o644)
    return target


def main():
    blob = load_asset()
    if jpeg_dimensions(blob) != EXPECTED_SIZE:
        raise ValueError(
            f"bundled image is {jpeg_dimensions(blob)}, want {EXPECTED_SIZE}")
    target = emit(blob)
    print(f"wrote {target} ({len(blob)} bytes)")


if __name__ == "__main__":
    main()
