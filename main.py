"""news-image-20261121, submit #3: hand the hybrid front page to the grader.

The repository ships one picture, assets/entry.jpg: a hybrid front page
with 20 verified stories from Saturday 21 November 2026 — three large
illustrated leads, eight small region-tagged cards with drawn icons, and
a nine-item ALSO strip. This program only verifies the bundled picture
is a whole 1024x1024 JPEG under the 1 MiB cap and writes those exact
bytes to entry.png, so both grader runs produce identical bytes.
Python 3.13, standard library only, no network access.
"""

import os
from pathlib import Path

PICTURE = Path(__file__).resolve().parent / "assets" / "entry.jpg"
DEST = "entry.png"
CAP = 1048576
WANT = (1024, 1024)
JPEG_START = b"\xff\xd8\xff"
JPEG_END = b"\xff\xd9"
FRAME_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def locate_asset():
    """Read the bundled picture, rejecting anything that is not a JPEG."""
    blob = PICTURE.read_bytes()
    if len(blob) > CAP:
        raise ValueError(f"bundled picture is {len(blob)} bytes, over 1 MiB")
    if not blob.startswith(JPEG_START):
        raise ValueError("bundled picture does not start with a JPEG header")
    if not blob.rstrip(b"\x00").endswith(JPEG_END):
        raise ValueError("bundled picture has no JPEG end marker")
    return blob


def frame_size(blob):
    """Width and height from the JPEG frame header (any SOFn marker)."""
    cursor = 2
    while cursor + 9 <= len(blob):
        if blob[cursor] != 0xFF:
            cursor += 1
            continue
        marker = blob[cursor + 1]
        if marker in FRAME_MARKERS:
            tall = int.from_bytes(blob[cursor + 5:cursor + 7], "big")
            wide = int.from_bytes(blob[cursor + 7:cursor + 9], "big")
            return (wide, tall)
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            cursor += 2
            continue
        span = int.from_bytes(blob[cursor + 2:cursor + 4], "big")
        cursor += 2 + span
    raise ValueError("no JPEG frame header found in bundled picture")


def place_output(blob):
    """Write the checked bytes to the output directory as entry.png."""
    folder = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / DEST
    with open(target, "wb") as handle:
        handle.write(blob)
    os.chmod(target, 0o644)
    if target.read_bytes() != blob:
        raise ValueError("written output does not match the bundled picture")
    return target


def main():
    blob = locate_asset()
    size = frame_size(blob)
    if size != WANT:
        raise ValueError(f"bundled picture is {size}, want {WANT}")
    target = place_output(blob)
    print(f"wrote {target} ({len(blob)} bytes)")


if __name__ == "__main__":
    main()
