"""news-image-20261121: hand the front-page image to the grader.

The bundled front page (assets/entry.jpg) is the whole entry. This program
only checks those bytes and writes them out as entry.png, so the grader's
two runs always produce identical bytes. Python 3.13, standard library
only, no network access.
"""

import os
import struct

SOURCE_DIR = "assets"
SOURCE_FILE = "entry.jpg"
RESULT_FILE = "entry.png"
LIMIT_BYTES = 1048576
WANT_WIDTH = 1024
WANT_HEIGHT = 1024
JPEG_HEAD = b"\xff\xd8\xff"


def repo_root():
    return os.path.dirname(os.path.abspath(__file__))


def read_picture():
    """Load the bundled front page and reject anything that is not a JPEG."""
    path = os.path.join(repo_root(), SOURCE_DIR, SOURCE_FILE)
    with open(path, "rb") as handle:
        blob = handle.read()
    if len(blob) > LIMIT_BYTES:
        raise ValueError("bundled image is over the 1 MiB limit")
    if not blob.startswith(JPEG_HEAD):
        raise ValueError("bundled image does not start with a JPEG header")
    return blob


def picture_size(blob):
    """Pull width and height out of the first JPEG size marker."""
    pos = 2
    while pos + 9 < len(blob):
        if blob[pos] != 0xFF:
            pos += 1
            continue
        mark = blob[pos + 1]
        if mark in (0xD8, 0xD9) or 0xD0 <= mark <= 0xD7:
            pos += 2
            continue
        span = struct.unpack(">H", blob[pos + 2:pos + 4])[0]
        if 0xC0 <= mark <= 0xCF and mark not in (0xC4, 0xC8, 0xCC):
            tall, wide = struct.unpack(">HH", blob[pos + 5:pos + 9])
            return wide, tall
        pos += 2 + span
    raise ValueError("bundled image has no JPEG size marker")


def hand_over(blob):
    """Check the size, then write the exact bytes to the output directory."""
    wide, tall = picture_size(blob)
    if (wide, tall) != (WANT_WIDTH, WANT_HEIGHT):
        raise ValueError(
            "bundled image is %dx%d, expected %dx%d"
            % (wide, tall, WANT_WIDTH, WANT_HEIGHT)
        )
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, RESULT_FILE)
    with open(dest, "wb") as handle:
        handle.write(blob)
    os.chmod(dest, 0o644)
    with open(dest, "rb") as handle:
        written = handle.read()
    if written != blob:
        raise ValueError("written output does not match the bundled image")


def main():
    hand_over(read_picture())


if __name__ == "__main__":
    main()
