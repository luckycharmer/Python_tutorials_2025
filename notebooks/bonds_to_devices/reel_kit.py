"""House style and renderer for every "Bonds to Devices" reel.

An episode script supplies only what is unique to it: its scenes, its
equations and its own animated picture. Everything shared lives here:

- the 1080 x 1920 paper-theme frame, series badge and headline/subline;
- the equation strip (one equation per scene);
- the ownership marks on every frame (corner credit, logo, centre watermark);
- the end card (logo, presenter, lab, notebook link);
- MP4 rendering with copyright metadata, PNG stills and the command line.

Layout regions (figure fractions, 0 = bottom, 1 = top) an episode may draw in:

    CONTENT = (0.255, 0.745)   main animated picture
    EXTRA   = (0.045, 0.145)   below the equation strip (bars, legends)

Cheat-sheet (enough to write an episode without reading the rest of this file):

    Scene(start, end, head, sub, eq_caption="", eq="")   times in seconds
    head  <= 2 lines of ~18 characters;  sub <= 2 lines of ~42 characters
    eq    one mathtext string, <= ~45 rendered characters
    note  footer text, <= 95 characters
    Scenes run 22-26 s; end_teaser adds a 3.5 s end card after the last scene.
    With a 2-line head and 2-line sub, keep drawings below y = 0.715 (the
    CONTENT top of 0.745 is only safe for 1-line heads).

    kit.content_axes(left, width, bottom, top)   axes inside CONTENT
    kit.extra_axes()                             axes inside EXTRA
    kit.style_axis(ax, xlabel, ylabel)           house tick/label look
    kit.end_fade(t)    0 -> 1 as the end card covers the picture; fade
                       any fig.text you added with (1 - end_fade)
    kit.art["note"]    the footer text artist (set_alpha to hide it)
    ease(x), window(t, start, end), sci(x), sci_tex(x), minus(s)
    colours: PAPER INK SOFT CORAL SAND WATER GREEN; fonts: SANS DISPLAY

    python make_reel_epNN.py --sheet    stills at every scene's midpoint and
                                        the end card, as one contact sheet:
                                        output/<slug>_sheet.png

Minimal episode script:

    import reel_kit as rk

    SCENES = [rk.Scene(0, 4, "Headline", "Subline", "Caption", r"$E = h\\nu$"), ...]

    def build(fig, kit):          # create artists once, return a dict
        ax = kit.content_axes()
        ...
        return {"ball": ...}

    def update(art, t, kit):      # move artists for time t (seconds)
        ...

    if __name__ == "__main__":
        rk.main(episode=2, slug="ep02_bond_spring", title="The bond is a spring",
                scenes=SCENES, build=build, update=update,
                note="Frequencies from measured H2 Raman data.")
"""

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "stix"
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle

# ---------------------------------------------------------------- identity
SERIES = "BONDS TO DEVICES"
PRESENTER = "Dr Junaid Ali"
ROLE_LINE = "Associate Professor of Physics"
LAB_LINE = "Optoelectronics Research Laboratory"
UNI_LINE = "COMSATS University Islamabad"
REPO_URL = "github.com/luckycharmer/Python_tutorials_2025"
WATERMARK_CORNER = "© Dr Junaid Ali"
WATERMARK_CENTRE = "© Dr Junaid Ali · Optoelectronics Research Laboratory · COMSATS"
COPYRIGHT_YEAR = 2026

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "output"
DEFAULT_LOGO = HERE / "assets" / "lab_logo.png"

# ---------------------------------------------------------------- frame and palette
WIDTH_PX, HEIGHT_PX, FPS = 1080, 1920, 30
CONTENT = (0.255, 0.745)
EXTRA = (0.045, 0.145)

PAPER = "#f6f1e7"   # background
INK = "#1d2a44"     # main text and lines
SOFT = "#6b7385"    # secondary text
CORAL = "#e4573d"   # the moving object and key numbers
SAND = "#e9dfcc"    # filled areas
WATER = "#7fb3d5"   # quantum levels, light
GREEN = "#2f8f6b"   # energy you must add
CARD = "#ffffff"
CARD_EDGE = "#d9cfbc"


def pick_font(*names):
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in names:
        if name in available:
            return name
    return "DejaVu Sans"


SANS = pick_font("Inter", "DejaVu Sans")
DISPLAY = pick_font("Inter Display", "Inter", "DejaVu Sans")


# ---------------------------------------------------------------- helpers
@dataclass
class Scene:
    start: float
    end: float
    head: str
    sub: str
    eq_caption: str = ""
    eq: str = ""          # Matplotlib mathtext, e.g. r"$E = h\nu$"; empty for none


def ease(t):
    """Smooth 0 -> 1 step for t in [0, 1] (clipped outside)."""
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def window(t, start, end, fade=0.4):
    """1 inside [start, end], fading in and out over `fade` seconds."""
    return float(ease((t - start) / fade) * (1 - ease((t - end) / fade)))


def sci(x, digits=1):
    """'2.5 × 10²²' with Unicode superscripts (for plain text)."""
    exp = int(np.floor(np.log10(abs(x))))
    sup = str(exp).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{x / 10**exp:.{digits}f} × 10{sup}"


def sci_tex(x, digits=1):
    """'2.5\\times10^{22}' for use inside mathtext."""
    exp = int(np.floor(np.log10(abs(x))))
    return rf"{x / 10**exp:.{digits}f}\times10^{{{exp}}}"


def minus(s):
    """Typographic minus sign for displayed numbers."""
    return s.replace("-", "−")


# ---------------------------------------------------------------- the kit
class Kit:
    """Builds the shared frame; episodes ask it for axes in the free regions."""

    def __init__(self, episode, scenes, note, logo=None, end_teaser=None):
        self.episode = episode
        self.scenes = list(scenes)
        if end_teaser:
            self.scenes.append(Scene(self.scenes[-1].end, self.scenes[-1].end + 3.5,
                                     "Bonds to Devices", end_teaser))
        self.duration = self.scenes[-1].end
        self.end_start = self.scenes[-1].start
        self.note = note
        self.logo = logo
        self.fig = plt.figure(figsize=(WIDTH_PX / 100, HEIGHT_PX / 100), dpi=100,
                              facecolor=PAPER)
        self.art = {}
        self._header()
        self._equation_strip()

    # regions -------------------------------------------------------
    def content_axes(self, left=0.0, width=1.0, bottom=None, top=None, **kw):
        b = CONTENT[0] if bottom is None else bottom
        t = CONTENT[1] if top is None else top
        ax = self.fig.add_axes([left, b, width, t - b], **kw)
        ax.set_facecolor(PAPER)
        return ax

    def extra_axes(self, left=0.07, width=0.86):
        ax = self.fig.add_axes([left, EXTRA[0], width, EXTRA[1] - EXTRA[0]])
        ax.set_axis_off()
        return ax

    def style_axis(self, ax, xlabel="", ylabel=""):
        """House look for a plotted axis: soft ticks, no box, Inter labels."""
        ax.tick_params(colors=SOFT, labelsize=20, length=6, width=1.5, color=SOFT)
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_family(SANS)
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        for side in ["left", "bottom"]:
            ax.spines[side].set_color(SOFT)
            ax.spines[side].set_linewidth(1.5)
        if xlabel:
            ax.set_xlabel(xlabel, color=SOFT, family=SANS, size=21, labelpad=12)
        if ylabel:
            ax.set_ylabel(ylabel, color=SOFT, family=SANS, size=21, labelpad=10)

    # fixed parts ---------------------------------------------------
    def _header(self):
        fig = self.fig
        badge = fig.add_axes([0.07, 0.948, 0.40, 0.03])
        badge.set_axis_off()
        badge.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.5",
                                       transform=badge.transAxes, fc=INK, ec="none",
                                       mutation_aspect=0.08))
        badge.text(0.5, 0.48, f"{SERIES}  ·  {self.episode}", color=PAPER, family=SANS,
                   size=19, weight="bold", ha="center", va="center", transform=badge.transAxes)
        mark_x = 0.93
        if self.logo is not None:
            h_px, w_px = self.logo.shape[:2]
            bug_h = 0.034
            bug_w = bug_h * HEIGHT_PX * w_px / h_px / WIDTH_PX
            bug = fig.add_axes([0.93 - bug_w, 0.963 - bug_h / 2, bug_w, bug_h])
            bug.imshow(self.logo, interpolation="antialiased")
            bug.set_axis_off()
            mark_x = 0.93 - bug_w - 0.015
        fig.text(mark_x, 0.963, WATERMARK_CORNER, color=SOFT, family=SANS, size=21,
                 weight="semibold", ha="right", va="center")
        self.art["head"] = fig.text(0.07, 0.925, "", color=INK, family=DISPLAY, size=64,
                                    weight="heavy", va="top", linespacing=1.02)
        self.art["sub"] = fig.text(0.07, 0.83, "", color=SOFT, family=SANS, size=30, va="top",
                                   linespacing=1.32)

    def _equation_strip(self):
        eqa = self.fig.add_axes([0.05, 0.158, 0.90, 0.078])
        eqa.set_xlim(0, 1)
        eqa.set_ylim(0, 1)
        eqa.set_axis_off()
        self.art["eq_box"] = eqa.add_patch(FancyBboxPatch(
            (0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.12", mutation_aspect=0.155,
            fc=CARD, ec=CARD_EDGE, lw=1.8))
        self.art["eq_cap"] = eqa.text(0.035, 0.76, "", color=SOFT, family=SANS, size=18,
                                      va="center")
        self.art["eq"] = eqa.text(0.035, 0.34, "", color=INK, size=36, va="center")

    def finish(self):
        """Add the layers that must sit on top of the episode's picture."""
        fig = self.fig
        wm = fig.add_axes([0.0, CONTENT[0], 1.0, CONTENT[1] - CONTENT[0]])
        wm.set_axis_off()
        wm.patch.set_alpha(0)
        wm.text(0.5, 0.22, WATERMARK_CENTRE, ha="center", va="center", color=INK, alpha=0.13,
                family=SANS, size=14, weight="semibold")
        wm.text(0.5, 0.45, WATERMARK_CORNER, ha="center", va="center", color=INK, alpha=0.07,
                family=DISPLAY, size=58, weight="heavy", rotation=18)
        self.art["note"] = fig.text(0.07, 0.022, self.note, color=SOFT, family=SANS, size=16)
        self._end_card()

    def _end_card(self):
        cover = self.fig.add_axes([0.0, 0.0, 1.0, 0.765])
        cover.set_xlim(0, 1)
        cover.set_ylim(0, 1)
        cover.set_axis_off()
        self.art["cover"] = cover.add_patch(Rectangle((0, 0), 1, 1, fc=PAPER, ec="none",
                                                      alpha=0))
        credit = []
        to_frac = 1 / 0.765
        top = 0.40
        if self.logo is not None:
            h_px, w_px = self.logo.shape[:2]
            scale = min(0.15 * HEIGHT_PX / h_px, 0.70 * WIDTH_PX / w_px)
            w_frac = w_px * scale / WIDTH_PX
            h_frac = h_px * scale / HEIGHT_PX * to_frac
            y0 = 0.47 * to_frac
            credit.append(cover.imshow(self.logo, extent=[0.5 - w_frac / 2, 0.5 + w_frac / 2,
                                                          y0, y0 + h_frac],
                                       aspect="auto", zorder=3, interpolation="antialiased"))
        else:
            top = 0.52
        lines = [
            (top, PRESENTER, dict(size=50, weight="heavy", color=INK, family=DISPLAY)),
            (top - 0.042, ROLE_LINE, dict(size=27, color=SOFT)),
            (top - 0.076, LAB_LINE, dict(size=27, color=SOFT)),
            (top - 0.106, UNI_LINE, dict(size=27, color=SOFT)),
            (0.205, "Free notebook and code", dict(size=23, color=SOFT)),
            (0.175, REPO_URL, dict(size=25, weight="bold", color=CORAL)),
        ]
        for y, txt, kw in lines:
            kw.setdefault("family", SANS)
            credit.append(cover.text(0.5, y * to_frac, txt, ha="center", va="center",
                                     zorder=4, **kw))
        for item in credit:
            item.set_alpha(0)
        self.art["credit"] = credit

    # per frame -----------------------------------------------------
    def scene_index(self, t):
        for i, s in enumerate(self.scenes):
            if s.start <= t < s.end:
                return i
        return len(self.scenes) - 1

    def end_fade(self, t):
        """0 before the end card, rising to 1 as the end card covers the picture."""
        return float(ease((t - self.end_start) / 0.4))

    def draw_common(self, t):
        i = self.scene_index(t)
        s = self.scenes[i]
        fade_in = 1.0 if i == 0 else ease((t - s.start) / 0.35)
        fade_out = 1.0 if i == len(self.scenes) - 1 else ease((s.end - t) / 0.35)
        a = float(min(fade_in, fade_out))
        art = self.art
        art["head"].set_text(s.head)
        art["head"].set_alpha(a)
        art["sub"].set_text(s.sub)
        art["sub"].set_alpha(a)
        art["sub"].set_y(0.83 - 0.05 * s.head.count("\n"))
        has_eq = bool(s.eq)
        for key in ("eq_box", "eq_cap", "eq"):
            art[key].set_alpha(a if has_eq else 0)
        art["eq_cap"].set_text(s.eq_caption)
        art["eq"].set_text(s.eq)
        cover = self.end_fade(t)
        art["cover"].set_alpha(cover)
        for item in art["credit"]:
            item.set_alpha(float(ease((t - self.end_start - 0.4) / 0.5)))
        art["note"].set_alpha(1 - cover)


# ---------------------------------------------------------------- rendering
def load_logo(path):
    if path is None or not Path(path).is_file():
        return None
    return plt.imread(str(path))


def render(episode, slug, title, scenes, build, update, note, end_teaser=None,
           stills=None, logo_path=DEFAULT_LOGO, sheet=False):
    OUT_DIR.mkdir(exist_ok=True)
    logo = load_logo(logo_path)
    print("logo:", logo_path if logo is not None else "none found, end card shows name only")
    kit = Kit(episode, scenes, note, logo=logo, end_teaser=end_teaser)
    art = build(kit.fig, kit)
    kit.finish()

    def frame(t):
        kit.draw_common(t)
        update(art, t, kit)

    if sheet:
        stills = [round((s.start + s.end) / 2, 2) for s in kit.scenes]
        stills[-1] = round(kit.duration - 0.5, 2)
    if stills:
        paths = []
        for t in stills:
            frame(t)
            path = OUT_DIR / f"{slug}_still_{t:05.1f}s.png"
            kit.fig.savefig(path, facecolor=PAPER)
            paths.append(path)
            print(f"wrote {path}")
        if sheet:
            from PIL import Image
            tiles = [Image.open(p).convert("RGB").resize((360, 640)) for p in paths]
            board = Image.new("RGB", (360 * len(tiles), 640), PAPER)
            for k, tile in enumerate(tiles):
                board.paste(tile, (360 * k, 0))
            out = OUT_DIR / f"{slug}_sheet.png"
            board.save(out)
            for p in paths:
                p.unlink()
            print(f"wrote {out}")
        return

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("ffmpeg not found. Install it, or use --stills to export PNG frames.")
    out = OUT_DIR / f"{slug}.mp4"
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
           "-s", f"{WIDTH_PX}x{HEIGHT_PX}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart",
           "-metadata", f"title=Bonds to Devices, Episode {episode}: {title}",
           "-metadata", f"artist={PRESENTER}",
           "-metadata", f"copyright=© {COPYRIGHT_YEAR} {PRESENTER}, {LAB_LINE}, {UNI_LINE}",
           "-metadata", f"comment=Notebook and code: {REPO_URL}",
           str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(int(kit.duration * FPS)):
        frame(k / FPS)
        kit.fig.canvas.draw()
        proc.stdin.write(kit.fig.canvas.buffer_rgba().tobytes())
        if k % FPS == 0:
            print(f"\r{k / FPS:4.0f} / {kit.duration:.0f} s", end="", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"\nwrote {out}")


def main(**episode):
    """Command line shared by every episode script."""
    ap = argparse.ArgumentParser(description=f"Render episode {episode['episode']}.")
    ap.add_argument("--stills", nargs="+", type=float, help="export PNG frames at these seconds")
    ap.add_argument("--sheet", action="store_true",
                    help="one contact sheet: every scene's midpoint plus the end card")
    ap.add_argument("--logo", default=DEFAULT_LOGO,
                    help="lab logo image (default: assets/lab_logo.png in this folder)")
    args = ap.parse_args()
    render(stills=args.stills, logo_path=args.logo, sheet=args.sheet, **episode)
