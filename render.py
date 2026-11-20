"""Draw the front page with Pillow.

The sheet is exactly 1024 square, so nothing is cropped after the fact. The
page is measured before it is drawn: every story is wrapped to its column at
its own type size, its height is known, and each is placed in whichever
column is currently shortest, so the five bottoms finish together. A story
that would run past the footer is not drawn at all, and the region index and
the story count are taken from the stories actually set, so the arithmetic on
the page is true of the page.
"""

import os

from PIL import Image, ImageDraw, ImageFont

import stories

W = 1024
H = 1024
M = 30
INK = (18, 18, 18)
GREY = (92, 92, 92)
HAIR = (188, 188, 182)
PAPER = (253, 252, 248)
RED = (150, 24, 24)
BLUE = (30, 84, 140)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

NCOL = 5
GUTTER = 11
ART_H = 64

_fonts = {}


def font(path, size):
    key = (path, size)
    got = _fonts.get(key)
    if got is None:
        got = ImageFont.truetype(path, size)
        _fonts[key] = got
    return got


def split_sentences(text):
    """Cut prose into sentences, keeping the full stop with each one."""
    out, cur = [], ""
    for token in text.split(" "):
        cur = token if not cur else cur + " " + token
        if token.endswith(".") and not token.endswith(".."):
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def wrap(draw, text, fnt, width):
    """Greedy wrap on spaces; returns the lines that fit the measure."""
    out = []
    cur = ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def bar_chart(draw, box, bars, caption):
    """A falling column chart: one baseline, a value over each column."""
    x, y, w, h = box
    base = y + h - 26
    top = y + 20
    peak = max(v for _, v in bars) or 1.0
    slot = w / len(bars)
    bw = slot * 0.54
    for i, (name, v) in enumerate(bars):
        bh = (base - top) * (v / peak)
        bx = x + i * slot + (slot - bw) / 2
        draw.rectangle([bx, base - bh, bx + bw, base], fill=RED)
        fl = font(SANS, 10)
        lbl = "%.1f%%" % v
        draw.text((bx + bw / 2 - draw.textlength(lbl, font=fl) / 2, base - bh - 12),
                  lbl, font=fl, fill=GREY)
        draw.text((bx + bw / 2 - draw.textlength(name, font=fl) / 2, base + 4),
                  name, font=fl, fill=GREY)
    draw.line([(x, base), (x + w, base)], fill=INK, width=2)
    draw.text((x, y + 2), caption, font=font(SANS_B, 10), fill=INK)


def dial(draw, box, frac, big, small, label=None):
    """A ring showing frac, with the figure inside and a caption beneath."""
    x, y, w, h = box
    r = min(w, h - 24) / 2 - 5
    cx = x + w / 2
    cy = y + r + 8
    ring = max(6, int(r * 0.30))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 outline=(214, 214, 208), width=ring)
    draw.arc([cx - r, cy - r, cx + r, cy + r], -90,
             -90 + 360 * max(0.0, min(1.0, frac)), fill=BLUE, width=ring)
    f = font(SERIF_B, 19)
    draw.text((cx - draw.textlength(big, font=f) / 2, cy - 12), big, font=f, fill=INK)
    if label:
        fl = font(SANS_B, 6)
        tw = draw.textlength(label, font=fl)
        draw.text((cx - tw / 2, cy + 7), label, font=fl, fill=GREY)
    f2 = font(SANS, 10)
    for i, ln in enumerate(wrap(draw, small, f2, w)[:2]):
        draw.text((cx - draw.textlength(ln, font=f2) / 2, cy + r + 4 + i * 12),
                  ln, font=f2, fill=GREY)


def coins(draw, box, big=None, caption=None, n=7):
    """A rising stack of discs, for a listing."""
    x, y, w, h = box
    for i in range(n):
        cx = x + 15 + i * (w - 30) / (n - 1)
        ch = h * (0.30 + 0.70 * (i / (n - 1)))
        top = y + h - ch
        draw.rectangle([cx - 12, top, cx + 12, y + h - 6], fill=(212, 184, 74))
        draw.ellipse([cx - 12, top - 6, cx + 12, top + 6],
                     fill=(226, 198, 88), outline=(122, 100, 28), width=2)
        draw.ellipse([cx - 12, y + h - 12, cx + 12, y + h],
                     fill=(198, 170, 62), outline=(122, 100, 28), width=2)
    draw.line([(x, y + h), (x + w, y + h)], fill=INK, width=2)
    if big:
        fb = font(SERIF_B, 17)
        draw.text((x + w / 2 - draw.textlength(big, font=fb) / 2, y + 1), big,
                  font=fb, fill=INK)
    if caption:
        fc = font(SANS, 7)
        draw.text((x + w / 2 - draw.textlength(caption, font=fc) / 2, y + h + 2),
                  caption, font=fc, fill=GREY)


def draw_art(draw, kind, box, st=None):
    """Illustration for a story. `art_*` keys on the story override the defaults,
    so the same kind of graphic never repeats a figure that belongs elsewhere."""
    st = st or {}
    if kind == "chart":
        bar_chart(draw, box,
                  st.get("art_bars") or [("S&P", 2.0), ("NDX", 2.0), ("BTC", 0.6)],
                  st.get("art_cap") or "FALL ON THURSDAY, PER CENT")
    elif kind == "dial":
        dial(draw, box, st.get("art_frac", 0.75),
             st.get("art_big", "$120bn"),
             st.get("art_cap", "a year, the draft adaptation target"),
             st.get("art_arc", "TARGET"))
    elif kind == "coins":
        coins(draw, box, st.get("art_big", "$107bn"),
              st.get("art_cap", "FIRST-DAY LISTING"))


class Sheet:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), PAPER)
        self.d = ImageDraw.Draw(self.img)
        self.colw = (W - 2 * M - GUTTER * (NCOL - 1)) / NCOL

    def cx(self, i):
        return M + i * (self.colw + GUTTER)

    def rule(self, y, w=1, fill=HAIR, x0=None, x1=None):
        x0 = M if x0 is None else x0
        x1 = (W - M) if x1 is None else x1
        self.d.line([(x0, y), (x1, y)], fill=fill, width=w)

    def sizes(self, lead):
        return (
            font(SANS_B, 10),
            font(SERIF_B, 18 if lead else 12),
            font(SERIF, 12 if lead else 10),
            21 if lead else 14,
            13 if lead else 11,
        )

    def story_height(self, st, lead, cap=99):
        _, fh, fb, lh, bl = self.sizes(lead)
        h = 17
        h += len(wrap(self.d, st["head"], fh, self.colw)) * lh + 3
        if st.get("art") and not st.get("brief"):
            h += ART_H + 10
        if st.get("brief"):
            return h + 5 + 9
        lines = self.body_lines(st, fb, cap)
        h += len(lines) * bl
        return h + 11

    def body_lines(self, st, fb, cap):
        """The longest run of whole sentences that fits in cap lines.

        Newspaper briefs get cut, but a line ending on a half-built clause
        reads as an overflow. So drop trailing sentences until the rest fits,
        and only fall back to a hard trim when even one sentence is too long.
        """
        text = st["body"]
        sentences = split_sentences(text)
        while sentences:
            raw = wrap(self.d, " ".join(sentences), fb, self.colw)
            if len(raw) <= cap:
                return raw
            sentences.pop()
        raw = wrap(self.d, text, fb, self.colw)[:cap]
        if raw:
            raw[-1] = raw[-1].rstrip(",;:") + " …"
        return raw

    def draw_story(self, st, x, y, lead, cap=99):
        d = self.d
        fk, fh, fb, lh, bl = self.sizes(lead)

        colour = dict((n, c) for n, c in stories.REGIONS)[st["region"]]
        kick = st["kicker"].upper()
        kw = d.textlength(kick, font=fk)
        d.rectangle([x, y, x + kw + 8, y + 13], fill=colour)
        d.text((x + 4, y + 1), kick, font=fk, fill=(255, 255, 255))
        y += 17

        for ln in wrap(d, st["head"], fh, self.colw):
            d.text((x, y), ln, font=fh, fill=INK)
            y += lh
        y += 3

        if st.get("art") and not st.get("brief"):
            draw_art(d, st["art"], (x, y, self.colw, ART_H), st)
            y += ART_H + 10

        if st.get("brief"):
            y += 5
            self.rule(y, 1, HAIR, x, x + self.colw)
            return y + 8

        for ln in self.body_lines(st, fb, cap):
            d.text((x, y), ln, font=fb, fill=INK)
            y += bl

        y += 6
        self.rule(y, 1, HAIR, x, x + self.colw)
        return y + 8

    def nameplate(self):
        d = self.d
        y = 16
        d.text((M, y), "THE WORLD IN ONE DAY", font=font(SERIF_B, 23), fill=INK)
        fe = font(SANS, 11)
        ed = "INTERNATIONAL EDITION  ·  " + stories.EDITION
        d.text((W - M - d.textlength(ed, font=fe), y + 5), ed, font=fe, fill=GREY)
        y += 30
        self.rule(y, 3, INK)
        y += 4
        self.rule(y, 1, INK)
        return y + 8

    def dateband(self, y):
        d = self.d
        inner = W - 2 * M
        size = 84
        txt = "20 NOVEMBER 2026"
        f = font(SERIF_B, size)
        tw = d.textlength(txt, font=f)
        if tw > inner:
            size = int(size * inner / tw)
            f = font(SERIF_B, size)
            tw = d.textlength(txt, font=f)
        d.text((M + (inner - tw) / 2, y - 6), txt, font=f, fill=INK)
        y += int(size * 1.06)
        fs = font(SANS_B, 13)
        sub = "FRIDAY  ·  THE DAY IN FULL  ·  TIMES UTC"
        d.text((M + (inner - d.textlength(sub, font=fs)) / 2, y), sub,
               font=fs, fill=GREY)
        y += 20
        self.rule(y, 2, INK)
        return y + 8

    def numberstrip(self, y, numbers):
        d = self.d
        inner = W - 2 * M
        fn = font(SERIF_B, 22)
        fc = font(SANS, 10)
        cw = inner / len(numbers)
        for i, (num, cap) in enumerate(numbers):
            x = M + i * cw
            d.text((x + 2, y), num, font=fn, fill=RED)
            for j, ln in enumerate(wrap(d, cap, fc, cw - 8)[:2]):
                d.text((x + 2, y + 26 + j * 11), ln, font=fc, fill=GREY)
        y += 46
        self.rule(y, 1, INK)
        return y + 8

    def regionindex(self, y, tabs, total):
        d = self.d
        ft = font(SANS_B, 11)
        x = M
        for name, colour, count in tabs:
            if count == 0:
                continue
            label = "%s %d" % (name, count)
            tw = d.textlength(label, font=ft)
            if x + tw + 11 > W - M:
                break
            d.rectangle([x, y, x + tw + 11, y + 17], fill=colour)
            d.text((x + 5, y + 2), label, font=ft, fill=(255, 255, 255))
            x += tw + 16
        tail = "·  %d STORIES SET" % total
        if x + d.textlength(tail, font=ft) + 6 < W - M:
            d.text((x + 1, y + 3), tail, font=ft, fill=INK)

    def footer(self, y):
        d = self.d
        key = ("SOURCES  Reuters · AP · Bloomberg · AFP · DW · The Guardian · "
               "UN News · CNBC · WSJ · Xinhua · Kremlin · Le Monde")
        f = font(SANS, 9)
        line = wrap(d, key, f, W - 2 * M - 90)
        if line:
            d.text((M, y), line[0], font=f, fill=GREY)
        stamp = "20 NOV 2026"
        d.text((W - M - d.textlength(stamp, font=f), y), stamp, font=f, fill=GREY)


def render(items, numbers, out_path):
    sh = Sheet()
    y = sh.nameplate()
    y = sh.dateband(y)
    y = sh.numberstrip(y, numbers)
    y_body = y + 16
    footer_y = H - 28

    leads = list(items[:2])
    order = list(leads) + list(items[2:])
    islead = [any(st is s for s in leads) for st in order]

    def deal(cap):
        """Seat the whole list at this body-line budget, or as much as fits.

        Longest story first, into whichever column is shortest. That is the
        greedy rule that keeps five columns close to level: a short brief can
        always close a small gap, a long one cannot.
        """
        hs = [sh.story_height(st, ld, cap) for st, ld in zip(order, islead)]
        tops = [y_body] * NCOL
        cols = [[] for _ in range(NCOL)]

        # Give every column the same number of briefs. Filling purely by
        # shortest column can leave one column with three long stories and a
        # conspicuous hole where a fourth should be; an even count with the
        # heights balanced across columns reads as a planned page.
        quota = (len(order) + NCOL - 1) // NCOL
        for idx in sorted(range(len(order)), key=lambda k: (not islead[k], -hs[k])):
            st, h, ld = order[idx], hs[idx], islead[idx]
            target = None
            for c in sorted(range(NCOL),
                            key=lambda k: (len(cols[k]), tops[k])):
                if len(cols[c]) >= quota or tops[c] + h > footer_y:
                    continue
                target = c
                break
            if target is None:
                continue
            cols[target].append((st, ld, h))
            tops[target] += h
        return cols, tops

    best = None
    for cap in range(18, 2, -1):
        cols, tops = deal(cap)
        seated = sum(len(c) for c in cols)
        if best is None or seated > best[2]:
            best = (cols, tops, seated, cap)
        if seated == len(order):
            break

    cols, tops, seated, cap = best

    # Distribute each column's leftover height as extra leading, so the five
    # columns finish on one line instead of five ragged ones. Capped, because
    # a big gap between two briefs looks like a mistake, not an airy page.
    for c in range(NCOL):
        entries = cols[c]
        if len(entries) < 2:
            continue
        slack = (footer_y - y_body) - sum(h for _, _, h in entries)
        gap = max(0.0, min(60.0, slack / float(len(entries) - 1)))
        ty = y_body
        for st, ld, h in entries:
            sh.draw_story(st, sh.cx(c), ty, ld, cap)
            ty += h + gap
        tops[c] = ty - gap

    placed = [st for col in cols for st, _, _ in col]
    counts = {}
    for st in placed:
        counts[st["region"]] = counts.get(st["region"], 0) + 1
    tabs = [(n, col, counts.get(n, 0)) for n, col in stories.REGIONS]

    sh.regionindex(y, tabs, len(placed))
    sh.rule(y + 18, 2, INK)
    sh.footer(footer_y + 4)

    sh.img.save(out_path, format="PNG", optimize=True)
    return len(placed), [int(t) for t in tops], cap
