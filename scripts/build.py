#!/usr/bin/env python3
"""Generate the profile's SVG assets and the certification vault.

    python3 scripts/build.py           # rebuild assets/ and CERTIFICATIONS.md
    python3 scripts/build.py --check   # fail if the committed output is stale

Everything is generated from data/profile.toml with the standard library only,
so the output is identical on any machine. Text is measured with DejaVu Sans
metrics (a wide fallback font), so layouts that fit here also fit on macOS,
Windows and Linux.
"""
from __future__ import annotations

import argparse
import html
import math
import pathlib
import re
import sys
import tomllib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "profile.toml"
GENERATED_DIRS = ["assets"]
GENERATED_FILES = ["CERTIFICATIONS.md"]

# ---------------------------------------------------------------------------
# Text metrics (DejaVu Sans advance widths, in em)
# ---------------------------------------------------------------------------
_CHARS = (' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`'
          'abcdefghijklmnopqrstuvwxyz{|}~·—–→←↗≈★✓•≥×…’“”●○◆▸✔⟶')
_SANS = [318, 401, 460, 838, 636, 950, 780, 275, 390, 390, 500, 838, 318, 361, 318, 337, 636, 636, 636, 636,
         636, 636, 636, 636, 636, 636, 337, 337, 838, 838, 838, 531, 1000, 684, 686, 698, 770, 632, 575, 775,
         752, 295, 295, 656, 557, 863, 748, 787, 603, 787, 695, 635, 611, 732, 684, 989, 685, 611, 685, 390,
         337, 390, 838, 500, 500, 613, 635, 550, 635, 615, 352, 635, 634, 278, 278, 579, 278, 974, 634, 612,
         635, 635, 411, 521, 392, 634, 592, 818, 592, 592, 525, 636, 337, 636, 838, 318, 1000, 500, 838, 838,
         838, 838, 896, 838, 590, 838, 838, 1000, 318, 518, 518, 873, 873, 769, 502, 838, 1434]
_BOLD = [348, 456, 521, 838, 696, 1002, 872, 306, 457, 457, 523, 838, 380, 415, 380, 365, 696, 696, 696, 696,
         696, 696, 696, 696, 696, 696, 400, 400, 838, 838, 838, 580, 1000, 774, 762, 734, 830, 683, 683, 821,
         837, 372, 372, 775, 637, 995, 837, 850, 733, 850, 770, 720, 682, 812, 774, 1103, 771, 724, 725, 457,
         365, 457, 838, 500, 500, 675, 716, 593, 716, 678, 435, 716, 712, 343, 343, 665, 343, 1042, 712, 687,
         716, 716, 493, 595, 478, 712, 652, 924, 645, 652, 582, 712, 365, 712, 838, 380, 1000, 500, 838, 838,
         838, 838, 896, 838, 639, 838, 838, 1000, 380, 657, 657, 873, 873, 769, 502, 838, 1434]
SANS_W = dict(zip(_CHARS, (v / 1000 for v in _SANS)))
BOLD_W = dict(zip(_CHARS, (v / 1000 for v in _BOLD)))
MONO_W = 0.602

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


def tw(s: str, size: float, bold: bool = False, mono: bool = False, ls: float = 0.0) -> float:
    """Width of a single line of text in px."""
    if mono:
        w = len(s) * MONO_W * size
    else:
        table = BOLD_W if bold else SANS_W
        w = sum(table.get(c, 0.7 if bold else 0.64) for c in s) * size
    return w + ls * max(len(s) - 1, 0)


def wrap(s: str, size: float, maxw: float, bold=False, mono=False, ls=0.0) -> list[str]:
    """Greedy wrap. Text made of " · " segments breaks between segments first."""
    if " · " in s:
        lines, cur = [], ""
        for seg in s.split(" · "):
            trial = f"{cur} · {seg}" if cur else seg
            if tw(trial, size, bold, mono, ls) <= maxw:
                cur = trial
                continue
            if cur:
                lines.append(cur)
            if tw(seg, size, bold, mono, ls) <= maxw:
                cur = seg
            else:
                parts = wrap(seg, size, maxw, bold, mono, ls)
                lines.extend(parts[:-1])
                cur = parts[-1]
        if cur:
            lines.append(cur)
        return lines
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if not cur or tw(trial, size, bold, mono, ls) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(s: str, maxw: float, size: float, bold=False, mono=False, ls=0.0, floor=7.0) -> float:
    while size > floor and tw(s, size, bold, mono, ls) > maxw:
        size -= 0.25
    return size


def balanced(s, size, maxw, bold=False):
    """Wrap into the fewest lines, then even out a two-line break (no orphans)."""
    lines = wrap(s, size, maxw, bold)
    if len(lines) != 2 or " · " in s:
        return lines
    words = s.split()
    best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        wa, wb = tw(a, size, bold), tw(b, size, bold)
        if max(wa, wb) <= maxw and (best is None or max(wa, wb) < best[0]):
            best = (max(wa, wb), [a, b])
    return best[1] if best else lines


def fit_wrap(s, maxw, size, max_lines, bold=False, mono=False, floor=8.0):
    while True:
        lines = wrap(s, size, maxw, bold, mono)
        if (len(lines) <= max_lines and all(tw(l, size, bold, mono) <= maxw for l in lines)) or size <= floor:
            return size, lines
        size -= 0.25


def uniform(lines, maxw, size, floor=12.0, bold=False, mono=False):
    """Largest size (<= size, >= floor) at which every line fits on one line."""
    for s_ in lines:
        size = fit(s_, maxw, size, bold, mono, floor=floor)
    return size


def n(v: float) -> str:
    """Compact, deterministic number formatting."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def text(x, y, s, size, fill, weight=None, mono=False, anchor=None, ls=None, opacity=None, cls=None, extra=""):
    a = [f'x="{n(x)}"', f'y="{n(y)}"', f'font-size="{n(size)}"', f'fill="{fill}"']
    if weight:
        a.append(f'font-weight="{weight}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if ls:
        a.append(f'letter-spacing="{n(ls)}"')
    if opacity is not None:
        a.append(f'opacity="{n(opacity)}"')
    classes = " ".join(c for c in ("m" if mono else "", cls or "") if c)
    if classes:
        a.append(f'class="{classes}"')
    if extra:
        a.append(extra)
    return f'<text {" ".join(a)}>{esc(s)}</text>'


def rect(x, y, w, h, rx=0, fill="none", stroke=None, sw=1, extra=""):
    s = f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"'
    if rx:
        s += f' rx="{n(rx)}"'
    s += f' fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{n(sw)}"'
    if extra:
        s += " " + extra
    return s + "/>"


# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
THEMES = {
    "dark": dict(
        bg="#0B1120", bg2="#0F1B2E", panel="#111B2C", panel2="#15223A", line="#24354E", line2="#30486B",
        text="#EAF1FA", muted="#9DB0C7", faint="#6B819C", grid="#1B2A42",
        blue="#5EA0FF", green="#4ADE80", teal="#2DD4BF", amber="#FBBF24", violet="#A78BFA", pink="#F472B6",
        red="#F87171", tint=0.16, edge=0.5,
    ),
    "light": dict(
        bg="#FFFFFF", bg2="#F2F7FD", panel="#FFFFFF", panel2="#F4F8FD", line="#D7E1EE", line2="#BFD0E5",
        text="#0E1A2B", muted="#475A72", faint="#7A8DA6", grid="#E3EBF5",
        blue="#1F6FEB", green="#15803D", teal="#0F766E", amber="#B45309", violet="#6D28D9", pink="#BE185D",
        red="#DC2626", tint=0.12, edge=0.55,
    ),
}

# Fixed dark surfaces used by theme-neutral assets (tiles, buttons, terminal).
NEUTRAL = dict(bg="#0D1524", panel="#111C2E", line="#253751", text="#EAF1FA", muted="#9DB0C7", faint="#6B819C")
TERM = dict(dark="#080D18", light="#0F172A")

ISSUERS = {
    "microsoft": dict(label="Microsoft", short="MSFT", color="#3B82F6", dark="#82B1FF", light="#1D4ED8"),
    "google": dict(label="Google Cloud", short="GCP", color="#FACC15", dark="#FDE047", light="#A16207"),
    "snowflake": dict(label="Snowflake", short="SNOW", color="#22D3EE", dark="#67E8F9", light="#0E7490"),
    "aws": dict(label="AWS", short="AWS", color="#FB923C", dark="#FDBA74", light="#C2410C"),
    "databricks": dict(label="Databricks", short="DBX", color="#F43F5E", dark="#FB7185", light="#BE123C"),
    "anthropic": dict(label="Anthropic", short="ANTH", color="#D4A27F", dark="#E9C6A6", light="#9A5B34"),
    "mongodb": dict(label="MongoDB", short="MDB", color="#22C55E", dark="#4ADE80", light="#15803D"),
    "pending": dict(label="Pending", short="—", color="#94A3B8", dark="#CBD5E1", light="#64748B"),
}

LEVELS = {
    "fundamentals": dict(label="Fundamentals", short="FND", rank=1),
    "associate": dict(label="Associate", short="ASC", rank=2),
    "specialty": dict(label="Specialty", short="SPC", rank=3),
    "professional": dict(label="Professional", short="PRO", rank=4),
    "expert": dict(label="Expert", short="EXP", rank=5),
    "pending": dict(label="Link pending", short="···", rank=0),
}

MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def level_label(c) -> str:
    """Display name for a credential's level (an optional `label` overrides the tier name)."""
    return c.get("label") or LEVELS[c["level"]]["label"]


def level_short(c) -> str:
    label = c.get("label")
    return {"Foundations": "FDN"}.get(label, label[:3].upper()) if label else LEVELS[c["level"]]["short"]


def issued_month(c) -> str:
    y, m, _ = c["issued"].split("-")
    return f"{MONTHS[int(m) - 1]} {y}"


BASE_CSS = (
    f"text{{font-family:{SANS}}}.m{{font-family:{MONO}}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.pk{display:none}}"
)


def svg_open(w, h, title, desc, css="", defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="title desc" fill="none">'
        f'<title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc>'
        f"<style>{BASE_CSS}{css}</style>"
        f"<defs>{defs}</defs>"
    )


def frame(th, w, h, rx=22, grid=True):
    """Rounded background with gradient, dotted grid and border."""
    g = [
        rect(0, 0, w, h, rx, "url(#bgGrad)"),
    ]
    if grid:
        g.append(rect(0, 0, w, h, rx, "url(#dots)", extra='opacity="0.7"'))
    g.append(rect(0.75, 0.75, w - 1.5, h - 1.5, rx, "none", th["line"], 1.5))
    return "".join(g)


def frame_defs(th, w, h, rx=22):
    return (
        f'<linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{th["bg"]}"/><stop offset="1" stop-color="{th["bg2"]}"/></linearGradient>'
        f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="1.5" cy="1.5" r="1" fill="{th["grid"]}"/></pattern>'
        f'<clipPath id="clip"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>'
    )


def accent_grad(th, gid="acc"):
    return (
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{th["blue"]}"/><stop offset=".55" stop-color="{th["teal"]}"/>'
        f'<stop offset="1" stop-color="{th["green"]}"/></linearGradient>'
    )


def chip(x, y, label, size, fg, bg, border, h=26, pad=11, mono=False, weight=None, rx=None, bold=False):
    w = tw(label, size, bold=bold or (weight is not None and int(weight) >= 600), mono=mono) + pad * 2
    return w, (
        rect(x, y, w, h, rx if rx is not None else h / 2, bg, border, 1)
        + text(x + w / 2, y + h / 2 + size * 0.36, label, size, fg, weight, mono, "middle")
    )


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
def hero(th, d, mode):
    W, H = 1200, 500
    p = d["person"]
    trace = [
        ("$", 'ask "why did last night\'s batch job fail?"', "", ""),
        ("▸", "route", "intent → incident agent", "✓"),
        ("▸", "retrieve", "logs · tickets · runbooks  k=12", "✓"),
        ("▸", "correlate", "3 similar past incidents", "✓"),
        ("▸", "cite", "[S1] [S4] [S7] → all sources resolve", "✓"),
        ("▸", "gate", "unsupported claim? → abstain", "✓"),
        ("▸", "propose", "root cause + 4-step fix", "✓"),
        ("✔", "handoff", "a human approves · audit logged", ""),
    ]
    steps = len(trace) + 1
    css = [".ln{animation:16s ease-out infinite both}"]
    for i in range(steps):
        a = 2 + i * 3.2
        css.append(
            f"@keyframes l{i}{{0%,{n(a)}%{{opacity:0;transform:translateX(-8px)}}"
            f"{n(a + 2.5)}%,90%{{opacity:1;transform:none}}96%,100%{{opacity:0}}}}"
            f".l{i}{{animation-name:l{i}}}"
        )
    css.append(".cur{animation:blink 1.05s steps(1) infinite}@keyframes blink{50%{opacity:0}}")
    css.append(
        ".ring{animation:ring 2.4s ease-out infinite;transform-box:fill-box;transform-origin:center}"
        "@keyframes ring{0%{opacity:.75;transform:scale(1)}100%{opacity:0;transform:scale(2.8)}}"
    )
    css.append(
        ".orb{animation:orb 12s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}"
        "@keyframes orb{to{transform:translate(-60px,40px) scale(1.15)}}"
    )
    term = TERM[mode]
    CUR = 'class="cur"'
    defs = frame_defs(th, W, H, 24) + accent_grad(th) + (
        f'<radialGradient id="glowA"><stop offset="0" stop-color="{th["blue"]}" stop-opacity=".30"/>'
        f'<stop offset="1" stop-color="{th["blue"]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="glowB"><stop offset="0" stop-color="{th["teal"]}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{th["teal"]}" stop-opacity="0"/></radialGradient>'
        f'<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
        f'<feDropShadow dx="0" dy="14" stdDeviation="16" flood-color="#020617" '
        f'flood-opacity="{".55" if mode == "dark" else ".22"}"/></filter>'
    )
    desc = (
        f"{p['name']}, {p['role']} at {p['employer']} in {p['location']}. "
        "Headline: I build AI systems that prove their work. "
        "Multi-agent GenAI platforms, cite-or-abstain retrieval and guarded automation. "
        "Metrics: in production since 2022, about 20% faster turnaround, about 50% less SME dependency, "
        "74 certifications. A terminal panel animates an evidence-first run: route, retrieve, correlate, "
        "cite, gate, propose and hand off to a human."
    )
    o = [svg_open(W, H, f"{p['name']} — I build AI systems that prove their work", desc, "".join(css), defs)]
    o.append(frame(th, W, H, 24))
    o.append('<g clip-path="url(#clip)">')
    o.append('<circle class="orb" cx="1010" cy="70" r="330" fill="url(#glowA)"/>')
    o.append('<circle cx="250" cy="520" r="300" fill="url(#glowB)"/>')
    o.append("</g>")

    # status pill
    status = p["status"].upper()
    pw = tw(status, 11.5, mono=True, ls=1.2) + 46
    o.append(rect(56, 44, pw, 32, 16, th["panel"], th["line"], 1))
    o.append(f'<circle class="ring" cx="76" cy="60" r="5" fill="{th["green"]}"/>')
    o.append(f'<circle cx="76" cy="60" r="5" fill="{th["green"]}"/>')
    o.append(text(90, 64.5, status, 11.5, th["text"], 700, True, ls=1.2))

    o.append(text(54, 150, p["name"], 60, th["text"], 800, ls=-1))
    role = f"{p['role']} @ {p['employer']} · since 2022 · {p['location']}".upper()
    o.append(text(57, 186, role, fit(role, 540, 13, mono=True, ls=1.6), th["muted"], 600, True, ls=1.6))

    h1, h2 = "I build AI systems", "that prove their work."
    hs = min(fit(h1, 560, 36, bold=True), fit(h2, 560, 36, bold=True))
    o.append(text(56, 246, h1, hs, th["text"], 800, ls=-0.5))
    o.append(text(56, 246 + hs * 1.18, h2, hs, "url(#acc)", 800, ls=-0.5))

    sub = ("Multi-agent GenAI platforms, cite-or-abstain retrieval and guarded "
           "automation, from enterprise production to 18 public builds.")
    ss, sl = fit_wrap(sub, 548, 16.5, 2)
    for i, line in enumerate(sl):
        o.append(text(57, 334 + i * ss * 1.42, line, ss, th["muted"]))

    # metrics
    mx, my, mh, gap = 56, 390, 72, 10
    mw = (584 - gap * (len(d["metrics"]) - 1)) / len(d["metrics"])
    for i, m in enumerate(d["metrics"]):
        x = mx + i * (mw + gap)
        col = th[m["accent"]]
        o.append(rect(x, my, mw, mh, 14, th["panel"], th["line"], 1))
        o.append(rect(x, my + 14, 3, mh - 28, 1.5, col))
        o.append(text(x + 18, my + 33, m["value"], fit(m["value"], mw - 30, 24, bold=True), col, 800))
        o.append(text(x + 18, my + 55, m["label"], fit(m["label"], mw - 28, 14), th["muted"]))

    # terminal
    tx, ty, tW, tH = 668, 44, 488, 412
    o.append(f'<g filter="url(#shadow)">{rect(tx, ty, tW, tH, 18, term, "#22324A", 1.2)}</g>')
    o.append(f'<path d="M{tx} {ty + 40}H{tx + tW}" stroke="#1E2B40"/>')
    for i, c in enumerate(("#F87171", "#FBBF24", "#4ADE80")):
        o.append(f'<circle cx="{tx + 22 + i * 18}" cy="{ty + 20}" r="5.5" fill="{c}"/>')
    o.append(text(tx + tW / 2, ty + 25, "proof-trace — evidence-first run", 12, "#7C8DA6", 600, True, "middle"))
    lx, ly, lh = tx + 24, ty + 78, 36
    for i, (pre, kw, detail, ok) in enumerate(trace):
        y = ly + i * lh
        g = [f'<g class="ln l{i}">']
        if pre == "$":
            g.append(text(lx, y, "$", 14, "#4ADE80", 700, True))
            g.append(text(lx + 20, y, kw, fit(kw, tW - 70, 14, mono=True), "#E2E8F0", 500, True))
        else:
            pc = "#4ADE80" if pre == "✔" else "#5EA0FF"
            g.append(text(lx, y, pre, 14, pc, 700, True))
            g.append(text(lx + 20, y, kw, 14, "#7DD3FC" if pre != "✔" else "#4ADE80", 700, True))
            g.append(text(lx + 122, y, detail, fit(detail, 300, 14, mono=True), "#A9B8CC", None, True))
            if ok:
                g.append(text(tx + tW - 24, y, ok, 14, "#4ADE80", 700, True, "end"))
        g.append("</g>")
        o.append("".join(g))
    cy = ly + len(trace) * lh
    o.append(f'<g class="ln l{len(trace)}">'
             f'{text(lx, cy, "$", 13.5, "#4ADE80", 700, True)}'
             f'{rect(lx + 20, cy - 12, 8, 15, 1, "#E2E8F0", extra=CUR)}'
             "</g>")
    o.append(f'<path d="M{tx} {ty + tH - 38}H{tx + tW}" stroke="#1E2B40"/>')
    foot = "policy: cite-or-abstain · fail closed · human-in-the-loop"
    o.append(text(tx + 24, ty + tH - 15, foot, fit(foot, tW - 48, 11.5, mono=True), "#6B7E99", 600, True))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Link buttons (theme-neutral)
# ---------------------------------------------------------------------------
def glyph(kind, cx, cy, s, color, sw=1.6):
    """Small line icons drawn around (cx, cy) with half-size s."""
    k = s / 7
    if kind == "globe":
        return (f'<g stroke="{color}" stroke-width="{n(sw)}" fill="none"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(s)}"/>'
                f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(s * .45)}" ry="{n(s)}"/>'
                f'<path d="M{n(cx - s)} {n(cy)}H{n(cx + s)}"/></g>')
    if kind == "linkedin":
        return (rect(cx - s, cy - s, 2 * s, 2 * s, s * .35, "none", color, sw)
                + text(cx + .2 * k, cy + s * .48, "in", s * 1.25, color, 800, anchor="middle"))
    if kind == "mail":
        return (f'<g stroke="{color}" stroke-width="{n(sw)}" fill="none" stroke-linejoin="round">'
                f'{rect(cx - s, cy - s * .72, 2 * s, s * 1.44, s * .2)}'
                f'<path d="M{n(cx - s)} {n(cy - s * .6)}L{n(cx)} {n(cy + s * .15)}L{n(cx + s)} {n(cy - s * .6)}"/></g>')
    if kind in ("hex", "credly"):
        pts = " ".join(f"{n(cx + s * c)},{n(cy + s * r)}" for c, r in
                       ((0, -1), (.87, -.5), (.87, .5), (0, 1), (-.87, .5), (-.87, -.5)))
        inner = (f'<path d="M{n(cx - s * .38)} {n(cy + s * .02)}l{n(s * .28)} {n(s * .28)}'
                 f'l{n(s * .5)} {n(-s * .55)}" stroke="{color}" stroke-width="{n(sw)}" fill="none" '
                 f'stroke-linecap="round" stroke-linejoin="round"/>')
        return f'<polygon points="{pts}" stroke="{color}" stroke-width="{n(sw)}" fill="none" stroke-linejoin="round"/>' + inner
    if kind == "star":
        pts = []
        for i in range(10):
            r = s if i % 2 == 0 else s * .45
            a = -math.pi / 2 + i * math.pi / 5
            pts.append(f"{n(cx + r * math.cos(a))},{n(cy + r * math.sin(a))}")
        return f'<polygon points="{" ".join(pts)}" stroke="{color}" stroke-width="{n(sw)}" fill="none" stroke-linejoin="round"/>'
    if kind == "medal":
        return (f'<g stroke="{color}" stroke-width="{n(sw)}" fill="none" stroke-linejoin="round">'
                f'<path d="M{n(cx - s * .55)} {n(cy - s)}L{n(cx - s * .1)} {n(cy - s * .15)}M{n(cx + s * .55)} {n(cy - s)}'
                f'L{n(cx + s * .1)} {n(cy - s * .15)}"/>'
                f'<circle cx="{n(cx)}" cy="{n(cy + s * .32)}" r="{n(s * .62)}"/></g>'
                + text(cx, cy + s * .55, "1", s * .7, color, 800, anchor="middle"))
    if kind == "cloud":
        return (f'<path d="M{n(cx - s * .55)} {n(cy + s * .55)}H{n(cx + s * .6)}a{n(s * .42)} {n(s * .42)} 0 0 0 '
                f'{n(-s * .05)} {n(-s * .84)}a{n(s * .55)} {n(s * .55)} 0 0 0 {n(-s * 1.0)} {n(-s * .2)}'
                f'a{n(s * .44)} {n(s * .44)} 0 0 0 {n(-s * .1)} {n(s * 1.04)}Z" stroke="{color}" '
                f'stroke-width="{n(sw)}" fill="none" stroke-linejoin="round"/>')
    raise ValueError(kind)


BUTTONS = [
    ("portfolio", "Portfolio", "globe", "#5EA0FF"),
    ("linkedin", "LinkedIn", "linkedin", "#60A5FA"),
    ("email", "Email", "mail", "#4ADE80"),
    ("credly", "Credly", "credly", "#FBBF24"),
    ("codechef", "CodeChef", "star", "#C4B5FD"),
]


def button(label, icon, color):
    h, size = 44, 15
    w = 16 + 28 + 11 + tw(label, size, bold=True) + 12 + tw("↗", 13) + 16
    o = [svg_open(int(round(w)), h, label, f"{label} link button", "")]
    o.append(rect(0.75, 0.75, w - 1.5, h - 1.5, h / 2, NEUTRAL["bg"], color, 1.4))
    o.append(f'<circle cx="30" cy="22" r="14" fill="{color}" fill-opacity=".16"/>')
    o.append(glyph(icon, 30, 22, 7, color, 1.6))
    o.append(text(55, 27.5, label, size, NEUTRAL["text"], 700))
    o.append(text(w - 16, 27, "↗", 13, color, 700, anchor="end"))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Career timeline
# ---------------------------------------------------------------------------
def timeline(th, d):
    W, H = 1200, 350
    items = d["timeline"]
    kinds = {"edu": ("violet", "Education"), "work": ("blue", "Work"), "award": ("amber", "Recognition")}
    css = (".draw{stroke-dasharray:1100;animation:draw 12s ease-in-out infinite}"
           "@keyframes draw{0%{stroke-dashoffset:1100}30%,85%{stroke-dashoffset:0}100%{stroke-dashoffset:-1100}}"
           ".ring{animation:ring 2.4s ease-out infinite;transform-box:fill-box;transform-origin:center}"
           "@keyframes ring{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}")
    defs = frame_defs(th, W, H) + accent_grad(th, "acc")
    desc = "Career timeline: " + "; ".join(f"{i['when']}: {i['title']} ({i['detail']})" for i in items)
    o = [svg_open(W, H, "Career trajectory", desc, css, defs), frame(th, W, H)]
    o.append(text(40, 50, "TRAJECTORY · 2016 → NOW", 12, th["blue"], 700, True, ls=1.6))
    o.append(text(40, 84, "From microservices to multi-agent AI", 24, th["text"], 800, ls=-0.3))
    lx = W - 40
    for key in ("award", "work", "edu"):
        col, lab = kinds[key]
        wl = tw(lab, 12.5)
        o.append(text(lx, 80, lab, 12.5, th["muted"], anchor="end"))
        o.append(f'<circle cx="{n(lx - wl - 10)}" cy="76" r="4.5" fill="{th[col]}"/>')
        lx -= wl + 34
    x0, x1, y = 100, 1100, 172
    step = (x1 - x0) / (len(items) - 1)
    o.append(f'<path d="M{x0 - 50} {y}H{x1 + 50}" stroke="{th["line"]}" stroke-width="2"/>')
    o.append(f'<path class="draw" d="M{x0 - 50} {y}H{x1 + 50}" stroke="url(#acc)" stroke-width="3" stroke-linecap="round"/>')
    colw = step - 14
    for i, it in enumerate(items):
        x = x0 + i * step
        col = th[kinds[it["kind"]][0]]
        if it.get("current"):
            o.append(f'<circle class="ring" cx="{n(x)}" cy="{y}" r="9" fill="{col}" fill-opacity=".5"/>')
            nw = tw("NOW", 10, mono=True, ls=1.2) + 16
            o.append(rect(x - nw / 2, y - 64, nw, 20, 10, col))
            o.append(text(x, y - 50, "NOW", 10, th["bg"], 800, True, "middle", ls=1.2))
        o.append(f'<circle cx="{n(x)}" cy="{y}" r="10" fill="{th["bg"]}" stroke="{col}" stroke-width="3"/>')
        o.append(f'<circle cx="{n(x)}" cy="{y}" r="4" fill="{col}"/>')
        o.append(text(x, y - 24, it["when"], 14, col, 700, True, "middle"))
        ts, tl = fit_wrap(it["title"], colw, 16, 2, bold=True)
        yy = y + 40
        for line in tl:
            o.append(text(x, yy, line, ts, th["text"], 750, anchor="middle"))
            yy += ts * 1.28
        ds, dl = fit_wrap(it["detail"], colw, 13.5, 3)
        yy += 4
        for line in dl:
            o.append(text(x, yy, line, ds, th["muted"], anchor="middle"))
            yy += ds * 1.35
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Experience system map
# ---------------------------------------------------------------------------
def experience(th, d):
    W, H = 1200, 720
    e = d["experience"]
    css = (".flow{stroke-dasharray:4 7;animation:flow 1.6s linear infinite}"
           "@keyframes flow{to{stroke-dashoffset:-22}}")
    defs = frame_defs(th, W, H) + accent_grad(th, "acc") + (
        f'<marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">'
        f'<path d="M0 0L7 4L0 8Z" fill="{th["faint"]}"/></marker>')
    desc = (f"{e['title']}: {e['subtitle']} Signals from " + ", ".join(s[0] for s in e["sources"])
            + f" flow through a {e['chat'][0].lower()} and a {e['router'][0]} into specialist agents for "
            + ", ".join(a.lower() for a in e["agents"]) + ", backed by " + ", ".join(x[0] for x in e["engines"])
            + ". Outcomes: " + ", ".join(x[0].lower() for x in e["outcomes"]) + ". Impact: "
            + "; ".join(f"{a} {b}" for a, b in e["impact"]) + ".")
    o = [svg_open(W, H, e["title"], desc, css, defs), frame(th, W, H)]
    o.append(text(40, 52, e["eyebrow"], 12, th["blue"], 700, True, ls=1.6))
    o.append(text(40, 90, e["title"], 30, th["text"], 800, ls=-0.4))
    o.append(text(40, 120, e["subtitle"], fit(e["subtitle"], 1120, 15.5), th["muted"]))

    top, bot = 186, 566
    # column labels
    o.append(text(40, top - 14, "01 · SIGNALS", 11, th["faint"], 700, True, ls=1.4))
    o.append(text(300, top - 14, "02 · INTELLIGENCE FABRIC", 11, th["faint"], 700, True, ls=1.4))
    o.append(text(950, top - 14, "03 · ACTIONS", 11, th["faint"], 700, True, ls=1.4))

    def stack_boxes(x, w, rows, color_cycle):
        n_ = len(rows)
        bh, g = 50, (bot - top - 50 * n_) / (n_ - 1)
        ys = []
        for i, (name, sub) in enumerate(rows):
            y = top + i * (bh + g)
            col = th[color_cycle[i % len(color_cycle)]]
            o.append(rect(x, y, w, bh, 10, th["panel"], th["line"], 1))
            o.append(f'<circle cx="{x + 18}" cy="{n(y + bh / 2)}" r="4.5" fill="{col}"/>')
            o.append(text(x + 32, y + 22, name, fit(name, w - 42, 15.5, bold=True), th["text"], 700))
            o.append(text(x + 32, y + 39, sub, fit(sub, w - 40, 11.5, mono=True), th["muted"], None, True))
            ys.append(y + bh / 2)
        return ys

    sy = stack_boxes(40, 210, e["sources"], ("blue", "teal"))
    oy = stack_boxes(950, 210, e["outcomes"], ("green", "amber"))

    # core panel
    px, pw = 300, 600
    o.append(rect(px, top, pw, bot - top, 16, th["panel2"], th["line2"], 1.2))
    ix, iw = px + 18, pw - 36
    # chat bar
    o.append(rect(ix, top + 16, iw, 44, 10, th["panel"], th["line"], 1))
    o.append(text(ix + 16, top + 43, e["chat"][0], 16, th["text"], 750))
    o.append(text(ix + iw - 16, top + 43, e["chat"][1], fit(e["chat"][1], iw - 200, 12, mono=True),
                  th["muted"], None, True, "end"))
    o.append(f'<path d="M{px + pw / 2} {top + 62}V{top + 78}" stroke="{th["faint"]}" stroke-width="1.5" marker-end="url(#arr)"/>')
    # router
    ry = top + 82
    o.append(rect(ix, ry, iw, 50, 10, th["panel"], th["blue"], 1.4))
    o.append(text(ix + 16, ry + 22, "ROUTING LAYER", 10, th["blue"], 700, True, ls=1.4))
    o.append(text(ix + 16, ry + 40, e["router"][0], 16, th["text"], 800))
    o.append(text(ix + iw - 16, ry + 32, e["router"][1], fit(e["router"][1], iw - 262, 12, mono=True),
                  th["muted"], None, True, "end"))
    # agents
    ay = ry + 72
    aw = (iw - 3 * 12) / 4
    acols = ("blue", "violet", "green", "amber")
    for i, a in enumerate(e["agents"]):
        x = ix + i * (aw + 12)
        col = th[acols[i]]
        o.append(f'<path d="M{n(x + aw / 2)} {ry + 50}V{ay - 2}" stroke="{th["line2"]}" stroke-width="1.2"/>')
        o.append(rect(x, ay, aw, 62, 10, th["panel"], col, 1.4))
        o.append(text(x + aw / 2, ay + 24, "AGENT", 9.5, th["faint"], 700, True, "middle", ls=1.4))
        lab = a.upper()
        o.append(text(x + aw / 2, ay + 45, lab, fit(lab, aw - 14, 13.5, mono=True, ls=0.6), th["text"], 800, True,
                      "middle", ls=0.6))
    # engines
    ey = ay + 80
    for i, (name, sub) in enumerate(e["engines"]):
        x = ix + i * (aw + 12)
        o.append(rect(x, ey, aw, 62, 10, th["panel"], th["line"], 1))
        o.append(text(x + aw / 2, ey + 27, name, fit(name, aw - 12, 15, bold=True), th["text"], 750, anchor="middle"))
        o.append(text(x + aw / 2, ey + 46, sub, fit(sub, aw - 10, 11, mono=True), th["muted"], None, True, "middle"))
    # stack strip
    sy2 = ey + 80
    o.append(rect(ix, sy2, iw, 34, 9, "none", "url(#acc)", 1.6))
    o.append(text(ix + iw / 2, sy2 + 22, e["strip"], fit(e["strip"], iw - 24, 12, mono=True, ls=1), th["text"], 700,
                  True, "middle", ls=1))

    # connectors in / out
    merge_y = ry + 25
    for i, y in enumerate(sy):
        path = f"M250 {n(y)}C276 {n(y)} 274 {n(merge_y)} {px} {n(merge_y)}"
        o.append(f'<path d="{path}" stroke="{th["line2"]}" stroke-width="1.4"/>')
        o.append(f'<path class="flow" d="{path}" stroke="{th["blue"]}" stroke-width="1.6" opacity=".9"/>')
    out_y = ey + 31
    for i, y in enumerate(oy):
        path = f"M{px + pw} {n(out_y)}C{px + pw + 26} {n(out_y)} {px + pw + 24} {n(y)} 950 {n(y)}"
        o.append(f'<path d="{path}" stroke="{th["line2"]}" stroke-width="1.4"/>')
        o.append(f'<path class="flow" d="{path}" stroke="{th["green"]}" stroke-width="1.6" opacity=".9"/>')

    # impact band
    iy = 600
    cw = (W - 80 - 2 * 16) / 3
    icol = ("green", "blue", "violet")
    for i, (val, lab) in enumerate(e["impact"]):
        x = 40 + i * (cw + 16)
        col = th[icol[i]]
        o.append(rect(x, iy, cw, 84, 14, th["panel"], th["line"], 1))
        o.append(rect(x, iy + 18, 3.5, 48, 1.75, col))
        o.append(text(x + 24, iy + 42, val, 30, col, 800, ls=-0.5))
        o.append(text(x + 25, iy + 67, lab, fit(lab, cw - 44, 16), th["muted"]))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Project cards
# ---------------------------------------------------------------------------
GROUP_LABELS = {"agents": "AGENTS WITH GUARDRAILS", "products": "EVIDENCE-FIRST PRODUCTS"}


def flagship_card(th, p, idx):
    W, H = 1200, 400
    css = (".pk{animation:pk 5s linear infinite}"
           "@keyframes pk{0%{transform:translateY(0);opacity:0}6%{opacity:1}94%{opacity:1}100%{transform:translateY(240px);opacity:0}}")
    defs = frame_defs(th, W, H) + accent_grad(th, "acc") + (
        f'<radialGradient id="glow"><stop offset="0" stop-color="{th["blue"]}" stop-opacity=".18"/>'
        f'<stop offset="1" stop-color="{th["blue"]}" stop-opacity="0"/></radialGradient>')
    stats = ", ".join(f"{a} {b}" for a, b in p["stats"])
    desc = (f"{p['name']}: {p['tagline']} Pipeline: " + " → ".join(f"{a} ({b})" for a, b in p["lanes"])
            + ". " + " ".join(x + "." for x in p["points"]) + f" {stats}. Stack: " + ", ".join(p["stack"]) + ".")
    o = [svg_open(W, H, f"{p['name']} — flagship project", desc, css, defs), frame(th, W, H)]
    o.append(f'<g clip-path="url(#clip)"><circle cx="1050" cy="-40" r="380" fill="url(#glow)"/></g>')
    tag = f"FLAGSHIP · {idx:02d}"
    _, c = chip(40, 36, tag, 11, th["blue"], th["panel"], th["line"], 26, 12, True, 700)
    o.append(c)
    if p.get("site"):
        _, c2 = chip(40 + tw(tag, 11, mono=True) + 34, 36, "LIVE", 11, th["green"], th["panel"], th["line"], 26, 12, True, 700)
        o.append(c2)
    o.append(text(38, 112, p["name"], fit(p["name"], 540, 46, bold=True), th["text"], 800, ls=-1))
    ts = 19
    tl = balanced(p["tagline"], ts, 520)
    for i, line in enumerate(tl):
        o.append(text(40, 148 + i * ts * 1.35, line, ts, th["text"], 500))
    y = 148 + len(tl) * ts * 1.35 + 20
    ps = uniform(p["points"], 506, 15.5, floor=13.5)
    for pt in p["points"]:
        pl = wrap(pt, ps, 506)
        o.append(f'<circle cx="46" cy="{n(y - 5)}" r="3.2" fill="{th["teal"]}"/>')
        for j, line in enumerate(pl):
            o.append(text(60, y + j * 20, line, ps, th["muted"]))
        y += len(pl) * 20 + 10
    # stack chips
    cx, cy = 40, H - 58
    for k, s in enumerate(p["stack"]):
        w = tw(s, 11.5, mono=True) + 20
        rest = len(p["stack"]) - k - 1
        more = tw(f"+{rest}", 11.5, mono=True) + 28 if rest else 0
        if cx + w + more > 566:
            label = f"+{len(p['stack']) - k}"
            _, c = chip(cx, cy, label, 11.5, th["muted"], th["panel"], th["line"], 26, 10, True)
            o.append(c)
            break
        _, c = chip(cx, cy, s, 11.5, th["text"], th["panel"], th["line"], 26, 10, True)
        o.append(c)
        cx += w + 8

    # pipeline on the right
    rx0, ry0 = 610, 42
    o.append(rect(rx0, ry0, 550, 228, 16, th["panel2"], th["line"], 1))
    o.append(text(rx0 + 20, ry0 + 26, "HOW IT WORKS", 10.5, th["faint"], 700, True, ls=1.4))
    lane_y0 = ry0 + 52
    lh = 31
    o.append(f'<path d="M{rx0 + 30} {lane_y0}V{lane_y0 + lh * (len(p["lanes"]) - 1)}" stroke="{th["line2"]}" stroke-width="2"/>')
    o.append(f'<circle class="pk" cx="{rx0 + 30}" cy="{lane_y0}" r="4" fill="{th["teal"]}"/>')
    for i, (a, b) in enumerate(p["lanes"]):
        yy = lane_y0 + i * lh
        last = i == len(p["lanes"]) - 1
        col = th["green"] if last else th["blue"]
        o.append(f'<circle cx="{rx0 + 30}" cy="{yy}" r="7" fill="{th["panel2"]}" stroke="{col}" stroke-width="2"/>')
        o.append(text(rx0 + 50, yy + 5.5, a, fit(a, 148, 15.5, bold=True), th["text"] if not last else col, 750))
        o.append(text(rx0 + 206, yy + 5, b, fit(b, 330, 13, mono=True), th["muted"], None, True))
    # stats
    sx, sy = rx0, ry0 + 246
    sw_ = (550 - 3 * 10) / 4
    for i, (v, lab) in enumerate(p["stats"]):
        x = sx + i * (sw_ + 10)
        o.append(rect(x, sy, sw_, 70, 12, th["panel"], th["line"], 1))
        o.append(text(x + 14, sy + 32, v, fit(v, sw_ - 24, 22, bold=True), th["text"], 800))
        o.append(text(x + 14, sy + 52, lab, fit(lab, sw_ - 22, 11.5), th["muted"]))
    note = "tests run and passing for the release" if p.get("tests_run") else "test definitions counted in the repository"
    o.append(text(rx0 + 550, H - 28, note, 10.5, th["faint"], None, True, "end"))
    o.append("</svg>")
    return "".join(o)


def featured_layout(p, W=590):
    """Shared measurements so every featured card in a grid gets the same height."""
    name = p.get("short") if tw(p["name"], 28, bold=True) > W - 64 and p.get("short") else p["name"]
    ts = 16.5
    tl = balanced(p["tagline"], ts, W - 54)
    ps = uniform(p["points"], W - 78, 14.75, floor=13.25)
    pts = [wrap(pt, ps, W - 78) for pt in p["points"]]
    body = 120 + len(tl) * ts * 1.36 + 8 + sum(len(pl) * 19.5 + 9 for pl in pts)
    return dict(name=name, ts=ts, tl=tl, ps=ps, pts=pts, need=body + 92)


def featured_card(th, p, idx, H):
    W = 590
    col = th[p.get("accent", "blue")]
    L = featured_layout(p, W)
    defs = frame_defs(th, W, H, 18) + (
        f'<radialGradient id="glow"><stop offset="0" stop-color="{col}" stop-opacity=".20"/>'
        f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
    desc = (f"{p['name']}: {p['tagline']} " + " ".join(x + "." for x in p["points"]) + " "
            + ", ".join(f"{a} {b}" for a, b in p["stats"]) + ". Stack: " + ", ".join(p["stack"]) + ".")
    o = [svg_open(W, H, p["name"], desc, "", defs), frame(th, W, H, 18)]
    o.append(f'<g clip-path="url(#clip)"><circle cx="560" cy="0" r="210" fill="url(#glow)"/></g>')
    o.append(rect(0, 26, 4, 48, 2, col))
    label = GROUP_LABELS[p["group"]]
    o.append(text(28, 43, f"{idx:02d} · {label}", 11.5, col, 700, True, ls=1.3))
    o.append(text(W - 26, 47, "↗", 19, th["faint"], 700, anchor="end"))
    o.append(text(26, 86, L["name"], fit(L["name"], W - 60, 28, bold=True), th["text"], 800, ls=-0.4))
    y = 117
    for line in L["tl"]:
        o.append(text(27, y, line, L["ts"], th["text"], 500))
        y += L["ts"] * 1.36
    y += 12
    for pl in L["pts"]:
        o.append(f'<path d="M30 {n(y - 5.5)}l3.8 3.8l7 -7.6" stroke="{col}" stroke-width="2.2" fill="none" '
                 'stroke-linecap="round" stroke-linejoin="round"/>')
        for j, line in enumerate(pl):
            o.append(text(52, y + j * 19.5, line, L["ps"], th["muted"]))
        y += len(pl) * 19.5 + 9
    stack = " · ".join(p["stack"])
    o.append(text(27, H - 66, stack, fit(stack, W - 54, 12.5, mono=True), th["faint"], 600, True))
    cx = 26
    for v, lab in p["stats"]:
        w = tw(v, 13.5, bold=True) + tw(" " + lab, 13.5) + 24
        o.append(rect(cx, H - 50, w, 31, 15.5, th["panel"], th["line"], 1))
        o.append(f'<text x="{n(cx + w / 2)}" y="{n(H - 29.5)}" font-size="13.5" fill="{th["muted"]}" '
                 f'text-anchor="middle"><tspan font-weight="800" fill="{th["text"]}">{esc(v)}</tspan> '
                 f'{esc(lab)}</text>')
        cx += w + 8
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------
def achievement_card(th, a):
    W, H = 590, 206
    col = th[a["accent"]]
    defs = frame_defs(th, W, H, 18) + (
        f'<radialGradient id="glow"><stop offset="0" stop-color="{col}" stop-opacity=".22"/>'
        f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
    css = (".shine{animation:shine 6s ease-in-out infinite}"
           "@keyframes shine{0%,100%{opacity:.55}50%{opacity:1}}")
    o = [svg_open(W, H, a["title"], f"{a['kicker']}: {a['title']}. {a['detail']}. {a['cta']}.", css, defs),
         frame(th, W, H, 18)]
    o.append(f'<g clip-path="url(#clip)"><circle class="shine" cx="74" cy="103" r="150" fill="url(#glow)"/></g>')
    o.append(f'<circle cx="74" cy="103" r="40" fill="{col}" fill-opacity=".13" stroke="{col}" stroke-opacity=".6" stroke-width="1.5"/>')
    o.append(glyph(a["glyph"], 74, 103, 17, col, 2.4))
    o.append(text(140, 58, a["kicker"], 11, col, 700, True, ls=1.4))
    o.append(text(139, 95, a["title"], fit(a["title"], W - 190, 27, bold=True), th["text"], 800, ls=-0.4))
    ds, dl = fit_wrap(a["detail"], W - 170, 14, 2)
    for i, line in enumerate(dl):
        o.append(text(140, 124 + i * 19, line, ds, th["muted"]))
    cta = a["cta"].upper() + " →"
    o.append(text(140, H - 26, cta, 11.5, col, 700, True, ls=1.2))
    o.append(text(W - 24, 42, "↗", 18, th["faint"], 700, anchor="end"))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Stack
# ---------------------------------------------------------------------------
def stack_map(th, d):
    W = 1200
    rows = d["stack"]
    left, cx0, cx1 = 40, 292, 1160
    ch, gapx, gapy, size = 34, 8, 10, 15
    layout, y = [], 124
    for r in rows:
        chips, x, yy = [], cx0, y
        for kind in ("work", "repo"):
            for s_ in r[kind]:
                w = tw(s_, size, bold=kind == "work") + (38 if kind == "work" else 28)
                if x + w > cx1:
                    x, yy = cx0, yy + ch + gapy
                chips.append((x, yy, w, s_, kind))
                x += w + gapx
        layout.append((r["layer"], y, chips))
        y = yy + ch + 28
    H = int(y + 12)
    defs = frame_defs(th, W, H)
    desc = "Technology stack. " + " ".join(
        f"{r['layer']}: at work, {', '.join(r['work']) or 'none'}; in public repos, {', '.join(r['repo']) or 'none'}."
        for r in rows)
    o = [svg_open(W, H, "Technology stack", desc, "", defs), frame(th, W, H)]
    o.append(text(40, 52, "STACK · EVIDENCE-TAGGED", 12.5, th["blue"], 700, True, ls=1.6))
    o.append(text(40, 88, "What I've shipped with, and where", 26, th["text"], 800, ls=-0.3))
    lx = W - 40
    for lab, kind in (("in public repos", "repo"), ("in production at Accenture", "work")):
        wl = tw(lab, 14)
        o.append(text(lx, 84, lab, 14, th["muted"], anchor="end"))
        if kind == "work":
            o.append(f'<circle cx="{n(lx - wl - 12)}" cy="79" r="5.5" fill="{th["teal"]}"/>')
        else:
            o.append(f'<circle cx="{n(lx - wl - 12)}" cy="79" r="5" fill="none" stroke="{th["muted"]}" stroke-width="1.6"/>')
        lx -= wl + 40
    for i, (layer, y, chips) in enumerate(layout):
        if i:
            o.append(f'<path d="M40 {y - 14}H1160" stroke="{th["line"]}" stroke-dasharray="2 5"/>')
        o.append(text(left, y + 23, layer, fit(layer, cx0 - left - 16, 16.5, bold=True), th["text"], 750))
        for x, yy, w, s_, kind in chips:
            if kind == "work":
                o.append(rect(x, yy, w, ch, ch / 2, th["teal"], None, extra=f'fill-opacity="{th["tint"]}"'))
                o.append(rect(x, yy, w, ch, ch / 2, "none", th["teal"], 1, extra=f'stroke-opacity="{th["edge"]}"'))
                o.append(f'<circle cx="{n(x + 15)}" cy="{n(yy + ch / 2)}" r="4" fill="{th["teal"]}"/>')
                o.append(text(x + 26, yy + 22.5, s_, size, th["text"], 600))
            else:
                o.append(rect(x, yy, w, ch, ch / 2, th["panel"], th["line2"], 1))
                o.append(text(x + w / 2, yy + 22.5, s_, size, th["muted"], None, anchor="middle"))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Wall of Mastery: periodic table
# ---------------------------------------------------------------------------
def element_slot(z):
    """(row, col, frow) for atomic number z on the standard 18-column layout."""
    if z == 1:
        return 1, 1, False
    if z == 2:
        return 1, 18, False
    for start, row in ((3, 2), (11, 3)):
        if start <= z <= start + 7:
            k = z - start
            return row, (k + 1 if k < 2 else k + 11), False
    if 19 <= z <= 36:
        return 4, z - 18, False
    if 37 <= z <= 54:
        return 5, z - 36, False
    for base, row in ((55, 6), (87, 7)):
        if z in (base, base + 1):
            return row, z - base + 1, False
        if base + 2 <= z <= base + 16:
            return row, z - base + 1, True  # f-block, columns 3..17
        if base + 17 <= z <= base + 31:
            return row, z - base - 13, False
    raise ValueError(z)


def periodic_table(th, d, mode):
    certs = d["certifications"]
    W, H = 1200, 706
    P, S = 64, 58
    L = (W - 18 * P + (P - S)) / 2
    T0 = 46
    css = (".hl{opacity:0;animation:hl 10s ease-in-out infinite}"
           "@keyframes hl{0%,100%{opacity:0}4%{opacity:.5}9%{opacity:0}}"
           ".xp{animation:xp 3.2s ease-in-out infinite}@keyframes xp{0%,100%{opacity:.25}50%{opacity:.9}}"
           ".q{animation:q 1.4s steps(1) infinite}@keyframes q{50%{opacity:.25}}")
    defs = frame_defs(th, W, H) + accent_grad(th, "acc") + (
        f'<linearGradient id="tier" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{th["faint"]}" stop-opacity=".35"/>'
        f'<stop offset="1" stop-color="{th["amber"]}"/></linearGradient>')
    counts = {}
    for c in certs:
        counts[c["issuer"]] = counts.get(c["issuer"], 0) + 1
    tiers = {}
    for c in certs:
        tiers[c["level"]] = tiers.get(c["level"], 0) + 1
    real = [c for c in certs if not c.get("pending")]
    desc = (f"A periodic table of {len(certs)} credentials across {len([k for k in counts if k != 'pending'])} "
            "ecosystems, ordered from fundamentals (lightest) to expert (heaviest). "
            + ", ".join(f"{ISSUERS[k]['label']} {v}" for k, v in counts.items() if k != "pending") + ". "
            + ", ".join(f"{v} {LEVELS[k]['label'].lower()}" for k, v in tiers.items() if k != "pending")
            + f". Element 1 is {real[0]['name']}; element {len(real)} is {real[-1]['name']}."
            + (" Element 74 is pending its verification link." if len(real) < len(certs) else ""))
    o = [svg_open(W, H, "The Periodic Table of Mastery", desc, css, defs), frame(th, W, H)]

    def xy(row, col, frow):
        x = L + (col - 1) * P
        y = T0 + (row - 1) * P if not frow else T0 + 7 * P + 24 + (row - 6) * P
        return x, y

    # group numbers
    tops = {1: 1, 2: 2, 13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 1}
    for col in range(1, 19):
        r = tops.get(col, 4)
        x, y = xy(r, col, False)
        o.append(text(x + S / 2, y - 6, str(col), 9, th["faint"], 600, True, "middle"))

    # header in the classic gap (cols 3-12, rows 1-3)
    gx, _ = xy(1, 3, False)
    gr, _ = xy(1, 12, False)
    gw = gr + S - gx
    o.append(text(gx, T0 + 14, "WALL OF MASTERY · LIVE-VERIFIABLE", 11.5, th["blue"], 700, True, ls=1.6))
    title = "The Periodic Table of Mastery"
    o.append(text(gx - 1, T0 + 50, title, fit(title, gw + 300, 31, bold=True), th["text"], 800, ls=-0.5))
    sub = f"{len(certs)} credentials · 7 ecosystems · lightest = fundamentals, heaviest = expert"
    o.append(text(gx, T0 + 76, sub, fit(sub, gw, 14), th["muted"]))
    # issuer legend
    lx, ly = gx, T0 + 84
    for k in ("microsoft", "google", "snowflake", "aws", "databricks", "anthropic", "mongodb"):
        iss = ISSUERS[k]
        lab = f"{iss['label']} {counts.get(k, 0)}"
        w = tw(lab, 12, bold=True) + 30
        if lx + w > gx + gw:
            lx, ly = gx, ly + 28
        o.append(rect(lx, ly, w, 24, 12, iss["color"], None, extra=f'fill-opacity="{th["tint"]}"'))
        o.append(rect(lx, ly, w, 24, 12, "none", iss["color"], 1, extra=f'stroke-opacity="{th["edge"]}"'))
        o.append(f'<circle cx="{n(lx + 12)}" cy="{n(ly + 12)}" r="4" fill="{iss["color"]}"/>')
        o.append(text(lx + 21, ly + 16.5, lab, 12, th["text"], 600))
        lx += w + 7
    # tier scale
    ty = T0 + 2 * P + 40
    o.append(rect(gx, ty, gw, 5, 2.5, "url(#tier)"))
    order = ("fundamentals", "associate", "specialty", "professional", "expert")
    seg = gw / len(order)
    for i, k in enumerate(order):
        lab = f"{tiers.get(k, 0)} {LEVELS[k]['label'].upper()}"
        o.append(text(gx + seg * i + (seg / 2), ty - 9, lab, fit(lab, seg - 6, 10, mono=True, ls=0.8),
                      th["muted"] if k != "expert" else th["amber"], 700, True, "middle", ls=0.8))

    # ghost cells (unfilled slots) and pointers
    filled = len(certs)
    for z in range(filled + 1, 119):
        row, col, frow = element_slot(z)
        x, y = xy(row, col, frow)
        o.append(rect(x + .5, y + .5, S - 1, S - 1, 7, "none", th["line"], 1, extra='stroke-dasharray="3 4"'))
    for row, lab, lo in ((6, "57–71", 57), (7, "89–103", 89)):
        x, y = xy(row, 3, False)
        active = lo <= filled
        o.append(rect(x + .5, y + .5, S - 1, S - 1, 7, th["panel"] if active else "none", th["line2"], 1,
                      extra='stroke-dasharray="3 3"'))
        o.append(text(x + S / 2, y + 30, lab, 10, th["muted"] if active else th["faint"], 700, True, "middle"))
        o.append(text(x + S / 2, y + 45, "↓", 11, th["muted"] if active else th["faint"], 700, anchor="middle"))

    # tiles
    ink = "dark" if mode == "dark" else "light"
    for z, c in enumerate(certs, start=1):
        row, col, frow = element_slot(z)
        x, y = xy(row, col, frow)
        iss = ISSUERS[c["issuer"]]
        g = [f'<g transform="translate({n(x)} {n(y)})">']
        if c.get("pending"):
            g.append(rect(.75, .75, S - 1.5, S - 1.5, 7, th["panel"], th["muted"], 1.3, extra='stroke-dasharray="4 3"'))
            g.append(text(6, 13, str(z), 9.5, th["faint"], 700, True))
            g.append(text(S / 2, 39, "?", 22, th["muted"], 800, anchor="middle", cls="q"))
            g.append(text(S / 2, 52, "SOON", 7.5, th["faint"], 700, True, "middle", ls=.6))
        else:
            g.append(rect(0, 0, S, S, 7, iss["color"], None, extra=f'fill-opacity="{th["tint"] + .02}"'))
            g.append(rect(.6, .6, S - 1.2, S - 1.2, 7, "none", iss["color"], 1.2 if c["level"] != "expert" else 1.8,
                          extra=f'stroke-opacity="{th["edge"]}"'))
            if c["level"] == "expert":
                g.append(rect(-2.5, -2.5, S + 5, S + 5, 9, "none", th["amber"], 1.6, extra='class="xp"'))
            g.append(rect(0, 0, S, S, 7, iss["color"], None, extra=f'class="hl" style="animation-delay:{n(z * 0.075)}s"'))
            g.append(text(5.5, 12.5, str(z), 9.5, th["muted"], 700, True))
            g.append(text(S - 5, 12.5, iss["short"], 7.5, iss[ink], 700, True, "end"))
            code = c["code"]
            g.append(text(S / 2, 37.5, code, fit(code, S - 8, 16, bold=True), th["text"], 800, anchor="middle"))
            g.append(text(S / 2, 51, level_short(c), 7.5, th["faint"], 700, True, "middle", ls=.6))
        g.append("</g>")
        o.append("".join(g))

    cap = "Every tile opens a live, issuer-hosted verification in the vault →"
    o.append(text(W / 2, H - 26, cap, 13, th["blue"], 700, True, "middle"))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Vault tiles and signature cards (theme-neutral)
# ---------------------------------------------------------------------------
def vault_tile(c, z):
    W, H = 168, 196
    iss = ISSUERS[c["issuer"]]
    col, ink = iss["color"], iss["dark"]
    pending = c.get("pending")
    title = f"No. {z}: {c['name']}"
    desc = ("Verification link pending." if pending else
            f"{iss['label']} · {level_label(c)} · {c['code']} · issued {issued_month(c)}. "
            "Opens the issuer's verification page.")
    o = [svg_open(W, H, title, desc, "", f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="14"/></clipPath>')]
    o.append(rect(0, 0, W, H, 14, NEUTRAL["bg"]))
    if pending:
        o.append(rect(.75, .75, W - 1.5, H - 1.5, 14, "none", "#64748B", 1.5, extra='stroke-dasharray="5 4"'))
    else:
        o.append(rect(0, 0, W, H, 14, col, None, extra='fill-opacity=".08"'))
        o.append(f'<g clip-path="url(#clip)">{rect(0, 0, W, 4, 0, col)}</g>')
        o.append(rect(.75, .75, W - 1.5, H - 1.5, 14, "none", col, 1.4 if c["level"] != "expert" else 2.2,
                      extra='stroke-opacity=".55"'))
    o.append(text(14, 28, f"No. {z}", 11, NEUTRAL["muted"], 700, True))
    o.append(text(W - 14, 28, iss["short"] if not pending else "", 10.5, ink, 700, True, "end"))
    code = c["code"]
    o.append(text(W / 2, 80, code, fit(code, W - 28, 32, bold=True), NEUTRAL["text"] if not pending else "#94A3B8",
                  800, anchor="middle", ls=-0.5))
    ns, nl = fit_wrap(c["name"], W - 26, 12.5, 3, bold=True)
    yy = 110
    for line in nl:
        o.append(text(W / 2, yy, line, ns, "#D6E0EC", 650, anchor="middle"))
        yy += ns * 1.3
    lab = ("★ " if c["level"] == "expert" else "") + level_label(c).upper()
    lab_size = fit(lab, W - 58, 9.5, mono=True, ls=.6)
    lw = tw(lab, lab_size, mono=True, ls=.6) + 16
    o.append(rect(12, H - 34, lw, 20, 10, col, None, extra='fill-opacity=".16"'))
    o.append(text(12 + lw / 2, H - 20.5, lab, lab_size, ink, 700, True, "middle", ls=.6))
    o.append(text(W - 14, H - 19, "…" if pending else "↗", 15, ink, 700, anchor="end"))
    o.append("</svg>")
    return "".join(o)


def signature_card(c, z):
    W, H = 560, 124
    iss = ISSUERS[c["issuer"]]
    col, ink = iss["color"], iss["dark"]
    o = [svg_open(W, H, c["name"], f"No. {z}: {c['name']} · {iss['label']} · {level_label(c)} · issued "
                  f"{issued_month(c)}. Opens the issuer's verification page.")]
    o.append(rect(0, 0, W, H, 16, NEUTRAL["bg"]))
    o.append(rect(0, 0, W, H, 16, col, None, extra='fill-opacity=".06"'))
    o.append(rect(.75, .75, W - 1.5, H - 1.5, 16, "none", col, 1.3, extra='stroke-opacity=".5"'))
    o.append(rect(12, 12, 100, 100, 12, col, None, extra='fill-opacity=".16"'))
    o.append(rect(12.6, 12.6, 98.8, 98.8, 12, "none", col, 1.2, extra='stroke-opacity=".6"'))
    o.append(text(22, 31, str(z), 10.5, NEUTRAL["muted"], 700, True))
    o.append(text(62, 72, c["code"], fit(c["code"], 84, 26, bold=True), NEUTRAL["text"], 800, anchor="middle", ls=-0.4))
    o.append(text(62, 96, iss["short"], 10, ink, 700, True, "middle", ls=1))
    ns, nl = fit_wrap(c["name"], W - 160, 17, 2, bold=True)
    y0 = 52 if len(nl) == 2 else 62
    for i, line in enumerate(nl):
        o.append(text(132, y0 + i * ns * 1.3, line, ns, NEUTRAL["text"], 750))
    meta = f"{iss['label']} · {level_label(c)} · {issued_month(c)}".upper()
    o.append(text(132, H - 20, meta, fit(meta, W - 250, 10.5, mono=True, ls=1), NEUTRAL["muted"], 700, True, ls=1))
    o.append(text(W - 18, H - 20, "VERIFY ↗", 11, ink, 700, True, "end", ls=1))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def footer(th, d):
    W, H = 1200, 220
    p = d["person"]
    css = (".wave{stroke-dasharray:6 10;animation:wv 2.2s linear infinite}@keyframes wv{to{stroke-dashoffset:-32}}")
    defs = frame_defs(th, W, H) + accent_grad(th, "acc")
    o = [svg_open(W, H, "Let's build AI that proves its work",
                  f"Closing banner. {p['status']}. Email {p['email']}, portfolio {p['portfolio']}.", css, defs),
         frame(th, W, H)]
    wave = "M0 170 C150 130 300 210 450 170 S750 130 900 170 S1100 210 1200 170"
    o.append(f'<g clip-path="url(#clip)"><path d="{wave}" stroke="{th["line"]}" stroke-width="2"/>'
             f'<path class="wave" d="{wave}" stroke="url(#acc)" stroke-width="2.5" opacity=".9"/></g>')
    o.append(text(W / 2, 62, "NEXT SYSTEM", 12, th["blue"], 700, True, "middle", ls=2))
    o.append(text(W / 2, 104, "Let's build AI that proves its work.", 34, th["text"], 800, anchor="middle", ls=-0.6))
    line = "Agentic AI · retrieval quality · cloud architecture · evidence-first products"
    o.append(text(W / 2, 136, line, fit(line, 1000, 16), th["muted"], anchor="middle"))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Certification vault (Markdown)
# ---------------------------------------------------------------------------
def pdf_for(d, c):
    """Certificate PDF on the portfolio, which serves it with noindex headers."""
    return d["vault"]["pdf_base"].rstrip("/") + "/" + c["pdf"].lstrip("/") if c.get("pdf") else None


def vault_md(d):
    certs = d["certifications"]
    p = d["person"]
    real = [c for c in certs if not c.get("pending")]
    counts = {}
    for c in real:
        counts[c["issuer"]] = counts.get(c["issuer"], 0) + 1
    numbered = list(enumerate(certs, start=1))
    out = []
    out.append("<!-- Generated by scripts/build.py from data/profile.toml. Edit the data, not this file. -->")
    out.append("")
    out.append("# Verification Vault")
    out.append("")
    out.append(f"> **{len(certs)} credentials across {len(counts)} ecosystems.** Every tile opens the issuer's own "
               "live verification page, so nothing here has to be taken on trust.")
    out.append("")
    out.append(f"[← Back to profile](./README.md) · [Certificate gallery]({d['vault']['gallery']}) · "
               f"[Credly profile]({p['credly']}) · [Portfolio]({p['portfolio']})")
    out.append("")
    out.append('<a href="#how-to-read-the-table">')
    out.append("<picture>")
    out.append('  <source media="(prefers-color-scheme: dark)" srcset="./assets/mastery-dark.svg">')
    out.append('  <source media="(prefers-color-scheme: light)" srcset="./assets/mastery-light.svg">')
    out.append(f'  <img alt="The Periodic Table of Mastery: {len(certs)} credentials ordered from fundamentals to expert" '
               'src="./assets/mastery-light.svg" width="100%">')
    out.append("</picture>")
    out.append("</a>")
    out.append("")
    out.append("<p align=\"center\">" + " · ".join(
        f"<strong>{ISSUERS[k]['label']}</strong> {v}"
        for k, v in sorted(counts.items(), key=lambda kv: -kv[1])) + "</p>")
    out.append("")
    out.append("## How to read the table")
    out.append("")
    out.append("Credentials are placed like elements: **the lightest are fundamentals, the heaviest are expert-level**. "
               "The number on each tile is its place in the table, the code is the exam or common abbreviation, and "
               "the colour is the issuer. Tap any tile below to verify it with the issuer.")
    out.append("")
    order = ("expert", "professional", "specialty", "associate", "fundamentals")
    names = {"professional": "Professional & Advanced"}
    for lvl in order:
        group = [(z, c) for z, c in numbered if c["level"] == lvl]
        if not group:
            continue
        label = names.get(lvl, LEVELS[lvl]["label"])
        out.append(f"### {label} · {len(group)}")
        out.append("")
        out.append('<p align="left">')
        for z, c in group:
            out.append(f'<a href="{esc(c["url"])}" title="{esc(c["name"])}"><img src="./assets/vault/{c["id"]}.svg" '
                       f'alt="No. {z}: {esc(c["name"])} ({ISSUERS[c["issuer"]]["label"]})" width="132"></a>')
        out.append("</p>")
        out.append("")
    pend = [(z, c) for z, c in numbered if c.get("pending")]
    if pend:
        z, c = pend[0]
        out.append(f"### No. {z} · link pending")
        out.append("")
        out.append(f'<p align="left"><a href="{p["portfolio"]}"><img src="./assets/vault/{c["id"]}.svg" '
                   f'alt="No. {z}: verification link pending" width="132"></a></p>')
        out.append("")
        out.append(f"The portfolio holds {len(certs)} PDF-backed credentials; {len(real)} have public issuer links "
                   f"listed here. No. {z} appears once its link is added to `data/profile.toml`.")
        out.append("")
    out.append("## Full index")
    out.append("")
    out.append("Every row links to the issuer's live verification and to the certificate PDF itself.")
    out.append("")
    out.append("<details>")
    out.append(f"<summary><strong>All {len(certs)} credentials, with issue dates and PDFs</strong></summary>")
    out.append("")
    out.append("| No. | Code | Credential | Issuer | Level | Issued | Verify | Certificate |")
    out.append("| ---: | --- | --- | --- | --- | --- | --- | --- |")
    for z, c in numbered:
        if c.get("pending"):
            out.append(f"| {z} | — | {c['name']} | — | — | — | pending | — |")
            continue
        pdf = pdf_for(d, c)
        out.append(f"| {z} | `{c['code']}` | {c['name']} | {ISSUERS[c['issuer']]['label']} | {level_label(c)} | "
                   f"{c['issued']} | [verify ↗]({c['url']}) | " + (f"[PDF]({pdf})" if pdf else "—") + " |")
    out.append("")
    out.append("</details>")
    out.append("")
    out.append("> The issuer link is the source of truth; the PDF is supporting evidence. Issue dates are read from "
               "each certificate. PDFs are hosted on the [portfolio](" + d["vault"]["gallery"] + "), which keeps them "
               "out of search indexes.")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Build driver
# ---------------------------------------------------------------------------
def validate(d):
    certs = d["certifications"]
    ids = [c["id"] for c in certs]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"duplicate certification ids: {sorted(dupes)}")
    urls = [c["url"] for c in certs if c.get("url")]
    if len(urls) != len(set(urls)):
        raise SystemExit("duplicate certification urls")
    last = 0
    for c in certs:
        if c["issuer"] not in ISSUERS or c["level"] not in LEVELS:
            raise SystemExit(f"unknown issuer/level on {c['id']}")
        if not c.get("pending"):
            rank = LEVELS[c["level"]]["rank"]
            if rank < last:
                raise SystemExit(f"{c['id']} breaks the lightest-to-heaviest order")
            last = rank
            if not c["url"].startswith("https://"):
                raise SystemExit(f"{c['id']} needs an https verification url")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", c.get("issued", "")):
                raise SystemExit(f"{c['id']} needs an issued date (YYYY-MM-DD)")
            if not re.fullmatch(r"certs/[a-z0-9-]+\.pdf", c.get("pdf", "")):
                raise SystemExit(f"{c['id']} needs a pdf path like certs/<name>.pdf")
    pdfs = [c["pdf"] for c in certs if c.get("pdf")]
    if len(pdfs) != len(set(pdfs)):
        raise SystemExit("two credentials point at the same pdf")
    if not d.get("vault", {}).get("pdf_base", "").startswith("https://"):
        raise SystemExit("[vault] pdf_base must be an https url")
    if len(certs) > 118:
        raise SystemExit("the periodic table has room for 118 credentials")


def outputs(d) -> dict[str, str]:
    files: dict[str, str] = {}
    for mode, th in THEMES.items():
        files[f"assets/hero-{mode}.svg"] = hero(th, d, mode)
        files[f"assets/timeline-{mode}.svg"] = timeline(th, d)
        files[f"assets/experience-{mode}.svg"] = experience(th, d)
        files[f"assets/stack-{mode}.svg"] = stack_map(th, d)
        files[f"assets/mastery-{mode}.svg"] = periodic_table(th, d, mode)
        files[f"assets/footer-{mode}.svg"] = footer(th, d)
        flag = feat = 0
        card_h = int(max(featured_layout(p)["need"] for p in d["projects"] if p["tier"] == "featured")) + 1
        for p in d["projects"]:
            if p["tier"] == "flagship":
                flag += 1
                files[f"assets/projects/{p['id']}-{mode}.svg"] = flagship_card(th, p, flag)
            else:
                feat += 1
                files[f"assets/projects/{p['id']}-{mode}.svg"] = featured_card(th, p, feat, card_h)
        for a in d["achievements"]:
            files[f"assets/achievements/{a['id']}-{mode}.svg"] = achievement_card(th, a)
    for key, label, icon, color in BUTTONS:
        files[f"assets/buttons/{key}.svg"] = button(label, icon, color)
    for z, c in enumerate(d["certifications"], start=1):
        files[f"assets/vault/{c['id']}.svg"] = vault_tile(c, z)
        if c.get("signature"):
            files[f"assets/vault/signature/{c['id']}.svg"] = signature_card(c, z)
    files["CERTIFICATIONS.md"] = vault_md(d)
    for path, body in files.items():
        if path.endswith(".svg"):
            ET.fromstring(body)  # must be well-formed XML
            files[path] = body + "\n"
    return files


def referenced_assets(md: str) -> set[str]:
    refs = set(re.findall(r'(?:src|srcset)="\.?/?([^"]+\.svg)"', md))
    return {r.lstrip("./") for r in refs}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if generated files are out of date")
    args = ap.parse_args()
    with DATA.open("rb") as fh:
        d = tomllib.load(fh)
    validate(d)
    files = outputs(d)

    existing = {str(p.relative_to(ROOT)) for base in GENERATED_DIRS for p in (ROOT / base).rglob("*.svg")}
    stale = existing - set(files)
    problems = []
    for name in ("README.md", "CERTIFICATIONS.md"):
        md = files.get(name) or (ROOT / name).read_text(encoding="utf-8")
        for ref in sorted(referenced_assets(md)):
            if ref not in files:
                problems.append(f"{name} references missing asset {ref}")

    if args.check:
        changed = [p for p, body in files.items()
                   if not (ROOT / p).exists() or (ROOT / p).read_text(encoding="utf-8") != body]
        for p in sorted(changed):
            problems.append(f"out of date: {p}")
        for p in sorted(stale):
            problems.append(f"stale file (no longer generated): {p}")
        if problems:
            print("\n".join(problems))
            print("\nRun `python3 scripts/build.py` and commit the result.")
            return 1
        print(f"ok: {len(files)} generated files are up to date")
        return 0

    for p, body in files.items():
        dest = ROOT / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.read_text(encoding="utf-8") != body:
            dest.write_text(body, encoding="utf-8")
    for p in stale:
        (ROOT / p).unlink()
    for base in GENERATED_DIRS:
        for folder in sorted((ROOT / base).rglob("*"), reverse=True):
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
    if problems:
        print("\n".join(problems))
        return 1
    print(f"built {len(files)} files ({len(stale)} stale removed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
