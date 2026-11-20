"""Compose the page once, off the clock. Not shipped in the entry.

    python3 build.py            # writes entry/entry.png
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import render  # noqa: E402
import stories  # noqa: E402


def main():
    items, numbers, tabs = stories.build()
    out = os.path.join(HERE, "entry.png")
    n, tops, cap = render.render(items, numbers, out)
    print("wrote %s, %d bytes" % (out, os.path.getsize(out)))
    print("%d stories placed at %d body lines each; columns end at %s "
          "(footer %d)" % (n, cap, tops, 1024 - 28))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
