#!/usr/bin/env python3
"""Render Episode 1 of "Bonds to Devices" as a vertical 1080x1920 MP4.

Visual idea: two atoms joined by a spring, above an energy "valley" that a
ball rolls along, with an energy gauge beside it. Every number on screen
comes from h2_morse.py, the same module the class notebook uses.

Usage (from this folder):
    python make_reel_ep01.py                     # writes output/ep01_h2_bond.mp4
    python make_reel_ep01.py --stills 2 10 20    # PNG frames at those seconds only

Needs NumPy and Matplotlib (requirements.txt) plus the ffmpeg program
(not a Python package; install it from ffmpeg.org or your package manager).
The video is silent: add music or a voice-over in your editing app.
"""

import argparse
import shutil
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

import h2_morse as h2

# ---------------------------------------------------------------- settings
WIDTH_PX, HEIGHT_PX, FPS = 1080, 1920, 30
OUT_DIR = Path(__file__).resolve().parent / "output"

PAPER = "#f6f1e7"       # warm paper background
INK = "#1d2a44"         # deep navy text and lines
SOFT = "#6b7385"        # secondary text
CORAL = "#e4573d"       # the rolling ball and key numbers
SAND = "#e9dfcc"        # valley fill
WATER = "#7fb3d5"       # zero-point "water level"
GREEN = "#2f8f6b"


def pick_font(*names):
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in names:
        if name in available:
            return name
    return "DejaVu Sans"


SANS = pick_font("Inter", "DejaVu Sans")
DISPLAY = pick_font("Inter Display", "Inter", "DejaVu Sans")

# Physics numbers used on screen (all from the shared module)
R_EQ_PM = h2.BOND_LENGTH_PM
DEPTH_EV = h2.WELL_DEPTH_EV
LEVEL0_EV = float(h2.morse_level_eV(0))
INNER_PM, OUTER_PM = h2.turning_points_pm(LEVEL0_EV)
BREAK_EV = h2.D0_MEASURED_EV
KT_ROOM_EV = h2.K_B_EV_PER_K * 298.15
FREQ_HZ = h2.vibration_frequency_Hz()
PAIRS_PER_LITRE = 101325 / (1.380649e-23 * 298.15) * 1e-3   # ideal gas, 1 atm, 25 °C

VIB_PERIOD_S = 1.2
SLOWDOWN = FREQ_HZ * VIB_PERIOD_S
FAR_PM = 290.0


def sci(x):
    """Format a number as 'm × 10ⁿ' with Unicode superscripts."""
    exp = int(np.floor(np.log10(x)))
    sup = str(exp).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{x / 10**exp:.1f} × 10{sup}"


# ---------------------------------------------------------------- storyboard
# (start s, end s, headline, subline)
SCENES = [
    (0.0, 4.0, "Hydrogen gas\nis made of pairs",
     f"About {sci(PAIRS_PER_LITRE)} pairs in every litre.\nWhy not single atoms?"),
    (4.0, 9.0, "Let two atoms meet",
     "The closer they get, the lower their energy.\nThe ball rolls downhill."),
    (9.0, 14.0, f"The valley floor:\n{R_EQ_PM:.0f} pm apart",
     "They never rest on the floor. A quantum\nminimum of motion keeps them swinging."),
    (14.0, 19.0, "Prise them apart",
     f"Climbing out of the valley\ncosts {BREAK_EV:.2f} eV per pair."),
    (19.0, 24.5, "So why do they\nstay paired?",
     "Each thermal kick at 25 °C carries\nonly a tiny fraction of that."),
    (24.5, 28.0, "Bonds to Devices",
     "Episode 2: the bond as a spring,\nand how light reveals its vibration."),
]
DURATION_S = SCENES[-1][1]


def ease(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def vibrate(t_s):
    """Classical swing between the turning points of the lowest level, slowed down."""
    mid = 0.5 * (INNER_PM + OUTER_PM)
    amp = 0.5 * (OUTER_PM - INNER_PM)
    return mid + amp * np.cos(2 * np.pi * t_s / VIB_PERIOD_S)   # starts at the outer point


def distance_at(t):
    if t < 4.0:
        return FAR_PM
    if t < 9.0:
        return FAR_PM + (OUTER_PM - FAR_PM) * ease((t - 4.0) / 4.5)
    if t < 14.0:
        return vibrate(t - 9.0)
    if t < 19.0:
        start = vibrate(5.0)
        return start + (FAR_PM - start) * ease((t - 14.5) / 4.0)
    if t < 20.5:
        return FAR_PM + (OUTER_PM - FAR_PM) * ease((t - 19.0) / 1.5)
    return vibrate(t - 20.5)


def scene_at(t):
    for i, (a, b, *_rest) in enumerate(SCENES):
        if a <= t < b:
            return i
    return len(SCENES) - 1


def text_alpha(t, i, fade=0.35):
    a, b = SCENES[i][0], SCENES[i][1]
    fade_in = 1.0 if i == 0 else ease((t - a) / fade)
    fade_out = 1.0 if i == len(SCENES) - 1 else ease((b - t) / fade)
    return min(fade_in, fade_out)


# ---------------------------------------------------------------- drawing helpers
def spring_xy(x1, x2, coils=6, amp=8.0, n=400):
    """Zig-zag spring between two x positions (stage units are pm)."""
    s = np.linspace(0, 1, n)
    x = x1 + (x2 - x1) * s
    lead = 0.12
    body = np.clip((s - lead) / (1 - 2 * lead), 0, 1)
    y = amp * np.sin(2 * np.pi * coils * body) * ((s > lead) & (s < 1 - lead))
    return x, y


def build_figure():
    fig = plt.figure(figsize=(WIDTH_PX / 100, HEIGHT_PX / 100), dpi=100, facecolor=PAPER)
    art = {}

    # series badge
    badge = fig.add_axes([0.07, 0.948, 0.40, 0.03])
    badge.set_axis_off()
    badge.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.5",
                                   transform=badge.transAxes, fc=INK, ec="none",
                                   mutation_aspect=0.08))
    badge.text(0.5, 0.48, "BONDS TO DEVICES  ·  1", color=PAPER, family=SANS, size=19,
               weight="bold", ha="center", va="center", transform=badge.transAxes)
    fig.text(0.93, 0.963, "H + H → H₂", color=SOFT, family=SANS, size=24, ha="right",
             va="center")

    art["head"] = fig.text(0.07, 0.925, "", color=INK, family=DISPLAY, size=64,
                           weight="heavy", va="top", linespacing=1.02)
    art["sub"] = fig.text(0.07, 0.83, "", color=SOFT, family=SANS, size=30, va="top",
                          linespacing=1.32)

    # atom stage
    st = fig.add_axes([0.0, 0.585, 1.0, 0.11])
    st.set_axis_off()
    half_w = 190.0
    half_h = half_w * (0.11 * HEIGHT_PX) / WIDTH_PX
    st.set_xlim(-half_w, half_w)
    st.set_ylim(-half_h, half_h)
    (art["spring"],) = st.plot([], [], color=INK, lw=3.2, solid_joinstyle="round")
    art["atoms"] = [Circle((0, 0), 24, fc=INK, ec="none", zorder=3) for _ in range(2)]
    art["shines"] = [Circle((0, 0), 7, fc="#ffffff", alpha=0.35, ec="none", zorder=4)
                     for _ in range(2)]
    for c in art["atoms"] + art["shines"]:
        st.add_patch(c)
    art["atom_labels"] = [st.text(0, 0, "H", color=PAPER, family=SANS, size=30, weight="bold",
                                  ha="center", va="center", zorder=5) for _ in range(2)]
    art["gap"] = st.text(0, 32, "", color=INK, family=SANS, size=28, weight="semibold",
                         ha="center", va="bottom")
    art["stage"] = st

    # energy valley
    ax = fig.add_axes([0.10, 0.20, 0.70, 0.36])
    ax.set_facecolor(PAPER)
    r = np.linspace(52, 330, 700)
    e = h2.morse_energy_eV(r)
    ymin, ymax = -5.4, 0.9
    ax.fill_between(r, e, ymin, color=SAND, lw=0)
    ax.plot(r, e, color=INK, lw=3.5)
    rw = np.linspace(INNER_PM, OUTER_PM, 200)
    art["water"] = ax.fill_between(rw, h2.morse_energy_eV(rw), LEVEL0_EV, color=WATER,
                                   alpha=0.0, lw=0)
    art["water_label"] = ax.text(OUTER_PM + 8, LEVEL0_EV - 0.05, "where H₂ actually sits",
                                 color="#2c6d99", family=SANS, size=19, va="top", alpha=0)
    ax.text(325, 0.18, "atoms far apart", color=SOFT, family=SANS, size=19, ha="right")
    art["ball_shadow"] = ax.scatter([0], [0], s=1100, c=INK, alpha=0.10, lw=0, zorder=4)
    art["ball"] = ax.scatter([0], [0], s=620, c=CORAL, edgecolors=INK, linewidths=2.5,
                             zorder=5)
    ax.set_xlim(45, 335)
    ax.set_ylim(ymin, ymax)
    ax.set_yticks([])
    ax.set_xticks([R_EQ_PM, 150, 200, 250, 300])
    ax.set_xticklabels(["74", "150", "200", "250", "300"])
    ax.tick_params(colors=SOFT, labelsize=20, length=6, width=1.5, color=SOFT)
    for lab in ax.get_xticklabels():
        lab.set_family(SANS)
    ax.get_xticklabels()[0].set_color(CORAL)
    ax.get_xticklabels()[0].set_weight("bold")
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(SOFT)
    ax.spines["bottom"].set_linewidth(1.5)
    ax.set_xlabel("gap between the two nuclei (picometres)", color=SOFT, family=SANS,
                  size=21, labelpad=12)
    art["valley"] = ax

    # energy gauge, sharing the valley's energy scale
    g = fig.add_axes([0.84, 0.20, 0.06, 0.36])
    g.set_xlim(0, 1)
    g.set_ylim(ymin, ymax)
    g.set_axis_off()
    g.add_patch(Rectangle((0.25, -DEPTH_EV), 0.5, DEPTH_EV, fc="#ffffff", ec=INK, lw=2,
                          zorder=1))
    art["gauge_fill"] = g.bar([0.5], [0], width=0.5, bottom=[0], color=CORAL, alpha=0.85, zorder=2)[0]
    g.text(0.5, 0.35, "energy", color=SOFT, family=SANS, size=19, ha="center")
    g.text(0.5, -DEPTH_EV - 0.35, f"−{DEPTH_EV:.2f}", color=SOFT, family=SANS, size=16,
           ha="center", va="top")
    art["gauge_val"] = fig.text(0.87, 0.175, "", color=CORAL, family=SANS, size=30,
                                weight="bold", ha="center", va="top")
    fig.text(0.87, 0.153, "eV", color=SOFT, family=SANS, size=19, ha="center", va="top")
    (art["climb"],) = g.plot([0.92, 0.92], [LEVEL0_EV, 0], color=GREEN, lw=4, alpha=0,
                             solid_capstyle="butt")
    art["climb_label"] = ax.text(250, -2.3, f"{BREAK_EV:.2f} eV\nto climb out", color=GREEN,
                                 family=SANS, size=24, weight="bold", ha="center", alpha=0)

    # comparison bars (scene 5)
    cb = fig.add_axes([0.07, 0.06, 0.86, 0.075])
    cb.set_xlim(0, 1.0)
    cb.set_ylim(-0.5, 1.6)
    cb.set_axis_off()
    art["bar_bond"] = cb.barh([1.0], [0], height=0.45, color=INK)[0]
    art["bar_heat"] = cb.barh([0.0], [0], height=0.45, color=CORAL)[0]
    art["bar_bond_t"] = cb.text(0, 1.38, f"Bond: {BREAK_EV:.2f} eV", color=INK, family=SANS,
                                size=21, weight="semibold", alpha=0)
    art["bar_heat_t"] = cb.text(0.035, 0.0, f"Heat kick at 25 °C: {KT_ROOM_EV:.3f} eV  "
                                f"(about 1/{BREAK_EV / KT_ROOM_EV:.0f})", color=CORAL,
                                family=SANS, size=21, weight="semibold", va="center", alpha=0)

    art["note"] = fig.text(0.07, 0.022,
                           "Energies from measured H₂ constants (Morse model).  "
                           f"Swing slowed about {sci(SLOWDOWN)} times.",
                           color=SOFT, family=SANS, size=16)
    art["end_url"] = fig.text(0.07, 0.125, "Free notebook and code\n"
                              "github.com/luckycharmer/Python_tutorials_2025",
                              color=INK, family=SANS, size=25, weight="semibold",
                              linespacing=1.5, alpha=0, va="top")
    return fig, art


def draw_frame(art, t):
    d = distance_at(t)
    i = scene_at(t)
    a = text_alpha(t, i)
    _, _, head, sub = SCENES[i]
    art["head"].set_text(head)
    art["head"].set_alpha(a)
    art["sub"].set_text(sub)
    art["sub"].set_alpha(a)
    art["sub"].set_y(0.83 - 0.05 * head.count("\n"))

    # atoms and spring
    xa, xb = -d / 2, d / 2
    for c, s, lab, x in zip(art["atoms"], art["shines"], art["atom_labels"], (xa, xb)):
        c.center = (x, 0)
        s.center = (x - 8, 9)
        lab.set_position((x, -1))
    spring_alpha = 1 - ease((d - 140) / 50)
    sx, sy = spring_xy(xa + 24, xb - 24)
    art["spring"].set_data(sx, sy)
    art["spring"].set_alpha(spring_alpha)
    art["gap"].set_text(f"{d:.0f} pm")

    # ball on the valley
    energy = float(h2.morse_energy_eV(d))
    art["ball"].set_offsets([[d, energy]])
    art["ball_shadow"].set_offsets([[d, energy - 0.08]])
    water = ease((t - 9.6) / 0.8)
    art["water"].set_alpha(0.55 * water)
    art["water_label"].set_alpha(water)

    # gauge
    art["gauge_fill"].set_height(energy)
    art["gauge_val"].set_text(f"{energy:.2f}".replace("-", "−"))
    climb = ease((t - 15.5) / 0.6) * (1 - ease((t - 19.0) / 0.5))
    art["climb"].set_alpha(climb)
    art["climb_label"].set_alpha(climb)

    # comparison bars
    grow = ease((t - 19.8) / 1.2)
    show = ease((t - 19.3) / 0.4) * (1 - ease((t - 24.5) / 0.4))
    art["bar_bond"].set_width(1.0 * grow)
    art["bar_heat"].set_width(max(KT_ROOM_EV / BREAK_EV * grow, 0.004 * grow))
    for key in ("bar_bond", "bar_heat", "bar_bond_t", "bar_heat_t"):
        art[key].set_alpha(show)
    art["note"].set_alpha(1 - show)

    end = ease((t - SCENES[-1][0]) / 0.6)
    art["end_url"].set_alpha(end)
    art["valley"].set_alpha(1)
    art["gap"].set_alpha(1 - end)


def render(stills=None):
    OUT_DIR.mkdir(exist_ok=True)
    fig, art = build_figure()

    if stills:
        for t in stills:
            draw_frame(art, t)
            path = OUT_DIR / f"ep01_still_{t:05.1f}s.png"
            fig.savefig(path, facecolor=PAPER)
            print(f"wrote {path}")
        return

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("ffmpeg not found. Install it, or use --stills to export PNG frames.")
    out = OUT_DIR / "ep01_h2_bond.mp4"
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
           "-s", f"{WIDTH_PX}x{HEIGHT_PX}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(DURATION_S * FPS)):
        draw_frame(art, k / FPS)
        fig.canvas.draw()
        proc.stdin.write(fig.canvas.buffer_rgba().tobytes())
        if k % FPS == 0:
            print(f"\r{k / FPS:4.0f} / {DURATION_S:.0f} s", end="", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stills", nargs="+", type=float, help="export PNG frames at these seconds")
    args = ap.parse_args()
    render(args.stills)
