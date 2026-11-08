#!/usr/bin/env python3
"""Render Episode 1 of "Bonds to Devices" as a vertical 1080x1920 MP4.

Every number on screen comes from h2_morse.py, the same module the class
notebook uses.

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
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import font_manager

import h2_morse as h2

# ---------------------------------------------------------------- settings
WIDTH_PX, HEIGHT_PX, FPS = 1080, 1920, 30
OUT_DIR = Path(__file__).resolve().parent / "output"

BG = "#0e1116"
INK = "#f2efe8"
MUTED = "#8b93a1"
ACCENT = "#ffb547"      # amber: the "you are here" dot and key numbers
TEAL = "#4fd1c5"
CLOUD_CMAP = LinearSegmentedColormap.from_list(
    "cloud", [BG, "#123a4a", "#1f7a80", TEAL, "#c9f5e9", "#fffbe6"]
)


def pick_font(*names):
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in names:
        if name in available:
            return name
    return "DejaVu Sans"


HEAD_FONT = pick_font("Inter Display", "Inter", "DejaVu Sans")
BODY_FONT = pick_font("Inter", "DejaVu Sans")
MONO_FONT = pick_font("JetBrains Mono", "DejaVu Sans Mono")

# Physics numbers used on screen (all from the shared module)
R_EQ_PM = h2.BOND_LENGTH_PM
LEVEL0_EV = float(h2.morse_level_eV(0))
INNER_PM, OUTER_PM = h2.turning_points_pm(LEVEL0_EV)
BREAK_EV = h2.D0_MEASURED_EV
KT_ROOM_EV = h2.K_B_EV_PER_K * 298.15
FREQ_HZ = h2.vibration_frequency_Hz()

# ---------------------------------------------------------------- storyboard
# (start s, end s, headline, subline)
SCENES = [
    (0.0, 3.0, "Why does hydrogen\ncome in pairs?", "Start with two lone hydrogen atoms."),
    (3.0, 8.0, "Bring them closer", "Their electron clouds overlap.\nThe energy drops."),
    (8.0, 13.0, f"The sweet spot: {R_EQ_PM:.0f} pm",
     "Bottom of the curve. But the pair\nnever sits still: it vibrates."),
    (13.0, 18.0, "Now pull them apart", f"Breaking the bond costs {BREAK_EV:.2f} eV."),
    (18.0, 22.5, "Room heat can't do it",
     f"Thermal jiggling at 25 °C ≈ {KT_ROOM_EV:.3f} eV.\n"
     f"About {BREAK_EV / KT_ROOM_EV:.0f}× too weak. So hydrogen gas is H₂."),
    (22.5, 26.0, "Bonds to Devices", "Next episode: the bond as a spring,\nand how light reveals its vibration."),
]
DURATION_S = SCENES[-1][1]
FAR_PM = 250.0


def ease(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


VIB_PERIOD_S = 1.1


def vibrate(t_s, period_s=VIB_PERIOD_S):
    """Classical swing between the turning points of the lowest level (slowed down)."""
    mid = 0.5 * (INNER_PM + OUTER_PM)
    amp = 0.5 * (OUTER_PM - INNER_PM)
    return mid + amp * np.cos(2 * np.pi * t_s / period_s)  # starts at the outer point


def distance_at(t):
    if t < 3.0:
        return FAR_PM
    if t < 8.0:
        return FAR_PM + (OUTER_PM - FAR_PM) * ease((t - 3.0) / 4.0)
    if t < 13.0:
        return vibrate(t - 8.0)
    if t < 18.0:
        start = vibrate(5.0)
        return start + (300.0 - start) * ease((t - 13.5) / 4.0)
    if t < 22.5:
        return 300.0 + (OUTER_PM - 300.0) * ease((t - 18.0) / 1.5) if t < 19.5 else vibrate(t - 19.5)
    return vibrate(t - 19.5)


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


# ---------------------------------------------------------------- figure
def build_figure():
    fig = plt.figure(figsize=(WIDTH_PX / 100, HEIGHT_PX / 100), dpi=100, facecolor=BG)

    art = {}
    art["series"] = fig.text(0.07, 0.955, "BONDS TO DEVICES  ·  EPISODE 1",
                             color=ACCENT, family=MONO_FONT, size=21, weight="bold")
    art["head"] = fig.text(0.07, 0.925, "", color=INK, family=HEAD_FONT, size=62,
                           weight="bold", va="top", linespacing=1.05)
    art["sub"] = fig.text(0.07, 0.832, "", color=MUTED, family=BODY_FONT, size=31,
                          va="top", linespacing=1.3)

    # electron cloud
    ax_c = fig.add_axes([0.0, 0.425, 1.0, 0.33])
    ax_c.set_facecolor(BG)
    ax_c.set_axis_off()
    half_w = 280.0
    half_h = half_w * (0.33 * HEIGHT_PX) / WIDTH_PX
    xs = np.linspace(-half_w, half_w, 400)
    ys = np.linspace(-half_h, half_h, int(400 * half_h / half_w))
    art["grid"] = np.meshgrid(xs, ys)
    art["norm"] = h2.bonding_density(0.0, 0.0, R_EQ_PM)  # brightness fixed to the bonded centre
    art["cloud"] = ax_c.imshow(np.zeros_like(art["grid"][0]), cmap=CLOUD_CMAP, vmin=0, vmax=1,
                               extent=[-half_w, half_w, -half_h, half_h], origin="lower",
                               interpolation="bilinear", aspect="equal")
    art["nuclei_glow"] = ax_c.scatter([0, 0], [0, 0], s=900, c=ACCENT, alpha=0.18, lw=0)
    art["nuclei"] = ax_c.scatter([0, 0], [0, 0], s=110, c="#fff3d6", lw=0, zorder=3)
    art["label_a"] = ax_c.text(0, 30, "H", color=INK, family=BODY_FONT, size=26, ha="center",
                               weight="bold")
    art["label_b"] = ax_c.text(0, 30, "H", color=INK, family=BODY_FONT, size=26, ha="center",
                               weight="bold")
    bracket_y = -half_h * 0.55
    (art["bracket"],) = ax_c.plot([], [], color=INK, lw=2.2, solid_capstyle="butt")
    art["bracket_y"] = bracket_y
    art["bracket_label"] = ax_c.text(0, bracket_y - 30, "", color=INK, family=MONO_FONT,
                                     size=30, ha="center", va="top")
    ax_c.set_xlim(-half_w, half_w)
    ax_c.set_ylim(-half_h, half_h)

    # live readout
    fig.text(0.07, 0.395, "DISTANCE", color=MUTED, family=MONO_FONT, size=19)
    fig.text(0.53, 0.395, "ENERGY", color=MUTED, family=MONO_FONT, size=19)
    art["r_val"] = fig.text(0.07, 0.355, "", color=INK, family=MONO_FONT, size=46, weight="bold")
    art["e_val"] = fig.text(0.53, 0.355, "", color=ACCENT, family=MONO_FONT, size=46,
                            weight="bold")

    # energy curve
    ax = fig.add_axes([0.15, 0.125, 0.78, 0.205])
    ax.set_facecolor(BG)
    r = np.linspace(48, 320, 600)
    e = h2.morse_energy_eV(r)
    for lw, al in [(14, 0.05), (8, 0.10)]:
        ax.plot(r, e, color=TEAL, lw=lw, alpha=al, solid_capstyle="round")
    ax.plot(r, e, color=TEAL, lw=3.2)
    ax.axhline(0, color=MUTED, lw=1.2, ls=(0, (4, 4)))
    ax.text(318, 0.18, "two free atoms", color=MUTED, family=MONO_FONT, size=17, ha="right")
    ax.hlines(LEVEL0_EV, INNER_PM, 318, color=ACCENT, lw=1.4, ls=(0, (2, 3)), alpha=0.8)
    ax.text(318, LEVEL0_EV - 0.25, "lowest allowed level", color=ACCENT, family=MONO_FONT,
            size=17, ha="right", va="top", alpha=0.9)
    art["arrow"] = ax.annotate("", xy=(240, 0), xytext=(240, LEVEL0_EV),
                               arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2,
                                               mutation_scale=26))
    art["arrow_label"] = ax.text(250, LEVEL0_EV / 2, f"{BREAK_EV:.2f} eV\nto break",
                                 color=INK, family=MONO_FONT, size=21, va="center")
    art["dot_glow"] = ax.scatter([0], [0], s=1400, c=ACCENT, alpha=0.22, lw=0, zorder=4)
    art["dot"] = ax.scatter([0], [0], s=260, c=ACCENT, lw=0, zorder=5)
    ax.set_xlim(40, 325)
    ax.set_ylim(-5.4, 1.0)
    ax.set_xticks([74, 150, 200, 250, 300])
    ax.set_yticks([-4, -2, 0])
    ax.tick_params(colors=MUTED, labelsize=18, length=0, pad=10)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_family(MONO_FONT)
    ax.get_xticklabels()[0].set_color(ACCENT)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color("#2a313c")
    ax.set_xlabel("distance between the two nuclei (pm)", color=MUTED, family=BODY_FONT,
                  size=20, labelpad=10)
    ax.set_ylabel("energy (eV)", color=MUTED, family=BODY_FONT, size=20, labelpad=8)

    fig.text(0.07, 0.016,
             "Energies: Morse fit to measured H₂ data.  Cloud: simple 1s + 1s picture.\n"
             f"Motion slowed about {FREQ_HZ * VIB_PERIOD_S / 1e14:.1f} × 10¹⁴ times.  1 pm = 10⁻¹² m.",
             color="#5d6573", family=BODY_FONT, size=16, linespacing=1.4)

    art["end_url"] = fig.text(0.07, 0.69, "Notebook and code:\ngithub.com/luckycharmer/"
                              "Python_tutorials_2025", color=INK, family=MONO_FONT, size=24,
                              linespacing=1.5, alpha=0)
    return fig, art


def draw_frame(art, t):
    d = distance_at(t)
    i = scene_at(t)
    a = text_alpha(t, i)
    _, _, head, sub = SCENES[i]
    art["head"].set_text(head)
    art["head"].set_alpha(a)
    art["sub"].set_text(sub)
    art["sub"].set_y(0.832 - 0.05 * head.count("\n"))
    art["sub"].set_alpha(a)

    end = ease((t - SCENES[-1][0]) / 0.6)
    gx, gy = art["grid"]
    dens = h2.bonding_density(gx, gy, d) / art["norm"]
    art["cloud"].set_data(np.clip(dens, 0, 1) ** 0.55 * (1 - 0.75 * end))
    pos = np.array([[-d / 2, 0], [d / 2, 0]])
    art["nuclei"].set_offsets(pos)
    art["nuclei_glow"].set_offsets(pos)
    art["label_a"].set_position((-d / 2, 26))
    art["label_b"].set_position((d / 2, 26))
    y = art["bracket_y"]
    art["bracket"].set_data([-d / 2, -d / 2, -d / 2, d / 2, d / 2, d / 2],
                            [y + 12, y - 12, y, y, y + 12, y - 12])
    art["bracket_label"].set_text(f"{d:.0f} pm")
    art["end_url"].set_alpha(end)
    for key in ("label_a", "label_b", "bracket_label"):
        art[key].set_alpha(1 - end)
    art["bracket"].set_alpha(1 - end)

    energy = float(h2.morse_energy_eV(d))
    art["r_val"].set_text(f"{d:6.1f} pm")
    art["e_val"].set_text(f"{energy:+.2f} eV".replace("-", "−"))
    art["dot"].set_offsets([[d, energy]])
    art["dot_glow"].set_offsets([[d, energy]])

    show_arrow = 1.0 if t >= 15.5 else 0.0
    art["arrow"].set_alpha(show_arrow)
    art["arrow"].arrow_patch.set_alpha(show_arrow)
    art["arrow_label"].set_alpha(show_arrow)


def render(stills=None):
    OUT_DIR.mkdir(exist_ok=True)
    fig, art = build_figure()

    if stills:
        for t in stills:
            draw_frame(art, t)
            path = OUT_DIR / f"ep01_still_{t:05.1f}s.png"
            fig.savefig(path, facecolor=BG)
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
    n_frames = int(DURATION_S * FPS)
    for k in range(n_frames):
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
