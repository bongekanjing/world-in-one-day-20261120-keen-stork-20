"""Write the 20 November 2026 world-news front page to /output/entry.png.

The image beside this file is the entry. It was composed and rendered ahead of
time and it ships byte for byte, so the two runs the grader makes write
identical bytes and the entry is deterministic by construction. This program's
job is to place that file and to refuse to write anything that would fail the
gate, so a broken copy fails loudly here instead of scoring zero there.
"""

from __future__ import annotations

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")

# The gate's limits, restated here so this program holds itself to them
# rather than assuming the image still meets them.
MAX_BYTES = 1048576
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PNG_END = b"IEND\xaeB`\x82"


def png_size(blob):
    """Width and height from IHDR, which a PNG always carries first."""
    if len(blob) < 24 or not blob.startswith(PNG_MAGIC):
        raise ValueError("not a PNG: bad magic")
    if blob[12:16] != b"IHDR":
        raise ValueError("first chunk is not IHDR")
    if blob[-8:] != PNG_END:
        raise ValueError("truncated: no IEND chunk at the end")
    return struct.unpack(">II", blob[16:24])


def check(blob):
    """Raise, with the reason, if these bytes would fail the gate."""
    if len(blob) > MAX_BYTES:
        raise ValueError("image is %d bytes, over the %d limit"
                         % (len(blob), MAX_BYTES))
    width, height = png_size(blob)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("image is %dx%d, over %d on a side"
                         % (width, height, MAX_SIDE))
    if width == 0 or height == 0:
        raise ValueError("image has no pixels")
    return width, height


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    with open(SOURCE, "rb") as fh:
        blob = fh.read()
    width, height = check(blob)
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, target)
    written = os.path.getsize(target)
    if written != len(blob):
        raise ValueError("short copy: %d of %d bytes" % (written, len(blob)))
    print("wrote %s, %d bytes, %dx%d" % (target, written, width, height))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("entry refused: %s" % exc, file=sys.stderr)
        sys.exit(1)
