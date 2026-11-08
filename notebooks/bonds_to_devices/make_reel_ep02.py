#!/usr/bin/env python3
"""Episode 2 reel: The bond is a spring.

Picture: a ball on a spring that draws its own wave on moving paper (a chart
recorder), then a green laser beam that comes back red, landing on a colour
ruler, and finally a heavier ball (deuterium) that draws a slower wave.
All shared styling (header, equation strip, watermarks, end card, rendering)
comes from reel_kit.py. Every number on screen comes from bond_spring.py,
the module the notebook uses.

Usage (from this folder):
    python make_reel_ep02.py                     # writes output/ep02_bond_spring.mp4
    python make_reel_ep02.py --stills 2 7 12     # PNG frames at those seconds only
"""

import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

import bond_spring as bs
import reel_kit as rk
from reel_kit import CORAL, GREEN, INK, PAPER, SAND, SANS, SOFT, Scene, ease

# ---------------------------------------------------------------- physics on screen
NU_H2_CM1 = bs.FUNDAMENTAL_H2_CM1
NU_D2_CM1 = bs.FUNDAMENTAL_D2_CM1
FREQ_HZ = float(bs.frequency_Hz(NU_H2_CM1))
PERIOD_FS = float(bs.period_fs(NU_H2_CM1))
LASER_NM = bs.LASER_NM
LASER_EV = float(bs.photon_energy_eV(LASER_NM))
QUANTUM_EV = NU_H2_CM1 * bs.EV_PER_CM1
OUT_H2_NM = float(bs.stokes_wavelength_nm(LASER_NM, NU_H2_CM1))
OUT_H2_EV = float(bs.photon_energy_eV(OUT_H2_NM))
OUT_D2_NM = float(bs.stokes_wavelength_nm(LASER_NM, NU_D2_CM1))
RATIO = NU_H2_CM1 / NU_D2_CM1
TRILLION = FREQ_HZ / 1e12

PERIOD_H2_S = 1.0                       # one swing on screen
PERIOD_D2_S = PERIOD_H2_S * RATIO       # same slowdown, so the true ratio is kept
SLOWDOWN = FREQ_HZ * PERIOD_H2_S

SCENES = [
    Scene(0.0, 5.0, "The bond is\na spring",
          "Pull the two atoms apart and the bond\npulls back. Let go, and it bounces.",
          "A spring's note is set by its stiffness k and mass μ",
          r"$\nu = \frac{1}{2\pi}\sqrt{k\,/\,\mu}$"),
    Scene(5.0, 10.0, "It rings at\none fixed note",
          f"H₂ swings about {TRILLION:.0f} trillion times\na second. Every H₂ molecule, the same.",
          "Measured H₂ vibration",
          rf"$\nu = c\,\tilde{{\nu}} = c \times {NU_H2_CM1:.0f}\ \mathrm{{cm^{{-1}}}} = "
          rf"{rk.sci_tex(FREQ_HZ, 2)}\ \mathrm{{Hz}}$"),
    Scene(10.0, 15.0, "How do we\nhear that note?",
          "H₂ has no electric dipole, so infrared\nbarely sees it. Shine green light instead.",
          f"Energy of one {LASER_NM:.0f} nm laser photon",
          rf"$E = hc\,/\,\lambda = 1240\ \mathrm{{eV\,nm}}\,/\,{LASER_NM:.0f}\ \mathrm{{nm}} = "
          rf"{LASER_EV:.2f}\ \mathrm{{eV}}$"),
    Scene(15.0, 20.0, "Green in,\nred out",
          "A few photons give the bond one step\nof vibration and come out redder.",
          "Raman scattering: the photon pays for one vibration step",
          rf"${LASER_EV:.2f} - {QUANTUM_EV:.2f} = {OUT_H2_EV:.2f}\ \mathrm{{eV}}"
          rf"\ \rightarrow\ {OUT_H2_NM:.0f}\ \mathrm{{nm}}$"),
    Scene(20.0, 24.5, "Heavier atoms,\nlower note",
          f"Deuterium is twice as heavy. Same\nspring, slower swing: {NU_D2_CM1:.0f} cm⁻¹.",
          "Measured H₂ and D₂ lines, compared with a perfect spring",
          rf"$\tilde{{\nu}}_{{H_2}}\,/\,\tilde{{\nu}}_{{D_2}} = {NU_H2_CM1:.0f}\,/\,{NU_D2_CM1:.0f}"
          rf" = {RATIO:.2f}\ \approx\ \sqrt{{2}}$"),
]
END_TEASER = "Episode 3: from two atoms to a crystal,\nwhere sharp levels become bands."
NOTE = ("H₂, D₂ lines: Dickenson et al. 2013.  "
        f"Swing slowed {rk.sci(SLOWDOWN)} times; Raman peaks enlarged.")

# ---------------------------------------------------------------- colours of light
RED_683 = "#b8322a"
RED_633 = "#d4632a"
GREEN_532 = "#3a9a4f"


def wavelength_rgb(nm):
    """Approximate colour of visible light, softened towards the paper colour."""
    nm = float(nm)
    if nm < 440:
        r, g, b = -(nm - 440) / 60, 0.0, 1.0
    elif nm < 490:
        r, g, b = 0.0, (nm - 440) / 50, 1.0
    elif nm < 510:
        r, g, b = 0.0, 1.0, -(nm - 510) / 20
    elif nm < 580:
        r, g, b = (nm - 510) / 70, 1.0, 0.0
    elif nm < 645:
        r, g, b = 1.0, -(nm - 645) / 65, 0.0
    else:
        r, g, b = 1.0, 0.0, 0.0
    fade = 1.0 if nm < 700 else max(0.3, 1 - (nm - 700) / 100)
    paper = np.array([0xf6, 0xf1, 0xe7]) / 255
    return 0.55 * np.array([r, g, b]) * fade + 0.45 * paper


# ---------------------------------------------------------------- motion
AMP = 0.47          # stretch on screen, lane units
REST_Y = -0.10      # ball rest height in a lane
H_RELEASE = 2.6
D_APPEAR, D_RELEASE = 19.9, 20.4
X_BALL, X_END = 1.25, 9.75
CEIL_Y = 1.3
SCROLL = 2.1        # paper speed, lane units per second


def stretch_h2(t):
    """Displacement of the H2 ball (negative = stretched), as a function of time."""
    t = np.asarray(t, dtype=float)
    pull = -AMP * ease((t - 0.8) / 1.4)
    swing = -AMP * np.cos(2 * np.pi * (t - H_RELEASE) / PERIOD_H2_S)
    return np.where(t < H_RELEASE, pull, swing)


def stretch_d2(t):
    t = np.asarray(t, dtype=float)
    swing = -AMP * np.cos(2 * np.pi * (t - D_RELEASE) / PERIOD_D2_S)
    return np.where(t < D_RELEASE, -AMP * ease((t - D_APPEAR) / 0.4), swing)


def spring_y(top, bottom, x0, coils=7, amp=0.16, n=300):
    s = np.linspace(0, 1, n)
    y = top + (bottom - top) * s
    lead = 0.12
    body = np.clip((s - lead) / (1 - 2 * lead), 0, 1)
    x = x0 + amp * np.sin(2 * np.pi * coils * body) * ((s > lead) & (s < 1 - lead))
    return x, y


def lorentz(x, centre, width=2.6):
    return 1.0 / (1 + ((x - centre) / width) ** 2)


# ---------------------------------------------------------------- picture
def build_lane(kit, bottom, top, label, ball_size):
    ax = kit.content_axes(left=0.05, width=0.90, bottom=bottom, top=top)
    ax.set_axis_off()
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.0, 1.6)
    lane = {"ax": ax}
    lane["paper"] = ax.add_patch(Rectangle((X_BALL, -0.9), X_END - X_BALL, 1.65,
                                           fc="#ffffff", ec=SAND, lw=2, zorder=0))
    lane["axis"] = ax.plot([X_BALL, X_END], [REST_Y, REST_Y], color=SAND, lw=2, zorder=1)[0]
    lane["ceiling"] = ax.plot([X_BALL - 0.55, X_BALL + 0.55], [CEIL_Y, CEIL_Y], color=INK, lw=6,
                              solid_capstyle="round", zorder=3)[0]
    (lane["spring"],) = ax.plot([], [], color=INK, lw=3, zorder=3, solid_joinstyle="round")
    (lane["trace"],) = ax.plot([], [], color=CORAL, lw=3.5, zorder=2)
    lane["ball"] = ax.scatter([X_BALL], [REST_Y], s=ball_size, c=CORAL, edgecolors=INK,
                              linewidths=2.5, zorder=5)
    lane["label"] = ax.text(0.05, 0.25, label, color=INK, family=SANS, size=34,
                            weight="bold", ha="left", va="center")
    return lane


def build(fig, kit):
    art = {}
    art["h2"] = build_lane(kit, 0.595, 0.715, "H₂", 900)
    art["d2"] = build_lane(kit, 0.47, 0.59, "D₂", 1700)
    art["d2_parts"] = [art["d2"][k] for k in ("paper", "axis", "ceiling", "spring", "trace",
                                              "ball", "label")]

    # bracket over one H2 swing (scene 2)
    h = art["h2"]["ax"]
    art["bracket"], = h.plot([], [], color=INK, lw=2.2)
    art["bracket_t"] = h.text(0, 1.08, f"one swing = {PERIOD_FS:.1f} femtoseconds",
                              color=INK, family=SANS, size=20, weight="semibold",
                              ha="center", va="bottom", alpha=0)
    art["pull"] = FancyArrowPatch((1.85, -0.6), (1.85, 0.15), arrowstyle="-|>",
                                  mutation_scale=28, color=GREEN, lw=4, alpha=0)
    h.add_patch(art["pull"])
    art["pull_t"] = h.text(2.05, 0.12, "pulls back", color=GREEN, family=SANS, size=20,
                           weight="bold", va="center", alpha=0)

    # middle band text, scenes 1-2
    mid = kit.content_axes(left=0.05, width=0.90, bottom=0.36, top=0.585)
    mid.set_axis_off()
    mid.set_xlim(0, 1)
    mid.set_ylim(0, 1)
    art["rule1"] = mid.text(0.03, 0.78, "Stiffer spring  →  higher note", color=INK,
                            family=SANS, size=34, weight="semibold", alpha=0)
    art["rule2"] = mid.text(0.03, 0.50, "Heavier ball  →  lower note", color=INK,
                            family=SANS, size=34, weight="semibold", alpha=0)
    art["big"] = mid.text(0.03, 0.62, f"{TRILLION:.0f} trillion", color=CORAL,
                          family=rk.DISPLAY, size=96, weight="heavy", va="center", alpha=0)
    art["big_sub"] = mid.text(0.035, 0.30, "swings every second", color=INK, family=SANS,
                              size=34, weight="semibold", va="center", alpha=0)

    # photon beam, scenes 3-4 (in the D2 lane's place)
    beam = kit.content_axes(left=0.05, width=0.90, bottom=0.47, top=0.59)
    beam.set_axis_off()
    beam.set_xlim(0, 10)
    beam.set_ylim(-1.2, 1.2)
    (art["beam_in"],) = beam.plot([], [], color=GREEN_532, lw=4)
    (art["beam_out_g"],) = beam.plot([], [], color=GREEN_532, lw=4)
    (art["beam_out_r"],) = beam.plot([], [], color=RED_683, lw=4)
    art["mol"] = beam.scatter([4.75, 5.25], [0, 0], s=520, c=INK, zorder=4)
    (art["mol_bond"],) = beam.plot([4.75, 5.25], [0, 0], color=INK, lw=5, zorder=3)
    art["beam_in_t"] = beam.text(0.3, 0.75, f"{LASER_NM:.0f} nm in", color=GREEN_532,
                                 family=SANS, size=24, weight="bold")
    art["beam_mol_t"] = beam.text(5.0, -0.95, "H₂", color=INK, family=SANS, size=22,
                                  weight="bold", ha="center", va="center")
    art["beam_out_g_t"] = beam.text(9.7, 0.75, f"most light: still {LASER_NM:.0f} nm",
                                    color=GREEN_532, family=SANS, size=24, weight="bold",
                                    ha="right")
    art["beam_out_r_t"] = beam.text(9.7, 0.75, f"a few photons: {OUT_H2_NM:.0f} nm",
                                    color=RED_683, family=SANS, size=24, weight="bold",
                                    ha="right")
    art["beam_parts"] = [art[k] for k in ("beam_in", "mol", "mol_bond", "beam_in_t",
                                          "beam_mol_t")]

    # colour ruler, scenes 3-5
    sp = kit.content_axes(left=0.08, width=0.84, bottom=0.29, top=0.45)
    sp.set_xlim(500, 720)
    sp.set_ylim(-0.30, 1.25)
    sp.set_yticks([])
    nm = np.linspace(500, 720, 441)
    band = np.array([wavelength_rgb(v) for v in nm])[None, :, :]
    art["band"] = sp.imshow(band, extent=[500, 720, -0.27, -0.06], aspect="auto", zorder=1)
    x = np.linspace(500, 720, 1500)
    art["x"] = x
    (art["peak_g"],) = sp.plot(x, np.zeros_like(x), color=GREEN_532, lw=3.5, zorder=3)
    art["xr"] = np.linspace(OUT_H2_NM - 18, OUT_H2_NM + 18, 300)
    art["xd"] = np.linspace(OUT_D2_NM - 18, OUT_D2_NM + 18, 300)
    (art["peak_r"],) = sp.plot(art["xr"], np.zeros(300), color=RED_683, lw=3.5, zorder=3)
    (art["peak_d"],) = sp.plot(art["xd"], np.zeros(300), color=RED_633, lw=3.5, zorder=3)
    art["peak_r_t"] = sp.text(OUT_H2_NM, 0.60, f"H₂\n{OUT_H2_NM:.0f} nm", color=RED_683,
                              family=SANS, size=22, weight="bold", ha="center", alpha=0)
    art["peak_d_t"] = sp.text(OUT_D2_NM, 0.52, f"D₂\n{OUT_D2_NM:.0f} nm", color=RED_633,
                              family=SANS, size=22, weight="bold", ha="center", alpha=0)
    art["peak_g_t"] = sp.text(LASER_NM + 5, 1.02, "laser", color=GREEN_532, family=SANS,
                              size=22, weight="bold", ha="left", alpha=0)
    (art["shift"],) = sp.plot([LASER_NM, OUT_H2_NM], [0.30, 0.30], color=INK, lw=2.2, alpha=0)
    art["shift_t"] = sp.text(0.5 * (LASER_NM + OUT_H2_NM) - 18, 0.36,
                             f"shift {NU_H2_CM1:.0f} cm⁻¹", color=INK, family=SANS, size=21,
                             weight="semibold", ha="center", alpha=0)
    art["enlarged_t"] = sp.text(718, 1.12, "Raman peaks enlarged", color=SOFT, family=SANS,
                                size=17, ha="right", alpha=0)
    sp.set_xticks([500, 550, 600, 650, 700])
    kit.style_axis(sp, xlabel="colour of light (wavelength, nm)")
    sp.spines["left"].set_visible(False)
    art["sp"] = sp

    # comparison bars, scene 5
    cb = kit.extra_axes()
    cb.set_xlim(0, 1.0)
    cb.set_ylim(-0.5, 1.6)
    art["bar_h"] = cb.barh([0.95], [0], height=0.36, color=INK)[0]
    art["bar_d"] = cb.barh([-0.25], [0], height=0.36, color=CORAL)[0]
    art["bar_h_t"] = cb.text(0, 1.25, f"H₂: {NU_H2_CM1:.0f} cm⁻¹", color=INK, family=SANS,
                             size=21, weight="semibold", alpha=0)
    art["bar_d_t"] = cb.text(0, 0.05, f"D₂: {NU_D2_CM1:.0f} cm⁻¹", color=CORAL,
                             family=SANS, size=21, weight="semibold", alpha=0)
    return art


def set_alpha(items, a):
    for it in items:
        if it is not None:
            it.set_alpha(a)


def draw_lane(lane, t, stretch, period, start):
    y_ball = REST_Y + float(stretch(t))
    sx, sy = spring_y(CEIL_Y, y_ball + 0.2, X_BALL)
    lane["spring"].set_data(sx, sy)
    lane["ball"].set_offsets([[X_BALL, y_ball]])
    x = np.linspace(X_BALL, X_END, 500)
    tau = t - (x - X_BALL) / SCROLL
    y = REST_Y + stretch(tau)
    y = np.where(tau >= start, y, np.nan)
    lane["trace"].set_data(x, y)


def update(art, t, kit):
    end = kit.end_fade(t)

    # H2 recorder, all scenes
    draw_lane(art["h2"], t, stretch_h2, PERIOD_H2_S, 0.0)
    pull = rk.window(t, 1.4, H_RELEASE, fade=0.3)
    art["pull"].set_alpha(pull)
    art["pull_t"].set_alpha(pull)

    # scene 2: bracket over one swing (between two troughs on the trace)
    br = rk.window(t, 5.4, 9.7)
    k = np.floor((t - H_RELEASE) / PERIOD_H2_S)
    t_trough = H_RELEASE + k * PERIOD_H2_S - 1.0 * PERIOD_H2_S   # a past trough
    x1 = X_BALL + (t - t_trough) * SCROLL
    x2 = x1 + PERIOD_H2_S * SCROLL
    if x2 > X_END - 0.1:
        x1 -= PERIOD_H2_S * SCROLL
        x2 -= PERIOD_H2_S * SCROLL
    art["bracket"].set_data([x1, x1, x2, x2], [0.88, 0.98, 0.98, 0.88])
    art["bracket"].set_alpha(br)
    art["bracket_t"].set_x(0.5 * (x1 + x2))
    art["bracket_t"].set_alpha(br)

    # middle band text
    r1 = rk.window(t, 1.8, 4.9, fade=0.4)
    art["rule1"].set_alpha(r1)
    art["rule2"].set_alpha(rk.window(t, 2.8, 4.9, fade=0.4))
    big = rk.window(t, 5.3, 9.8)
    art["big"].set_alpha(big)
    art["big_sub"].set_alpha(big)

    # photon beam, scenes 3-4
    beam_a = rk.window(t, 10.4, 19.7)
    lam_g = 0.6
    lam_r = lam_g * OUT_H2_NM / LASER_NM
    xin = np.linspace(0.3, 4.5, 400)
    art["beam_in"].set_data(xin, 0.32 * np.sin(2 * np.pi * (xin - 1.6 * t) / lam_g))
    xout = np.linspace(5.5, 9.7, 400)
    art["beam_out_g"].set_data(xout, 0.32 * np.sin(2 * np.pi * (xout - 1.6 * t) / lam_g))
    art["beam_out_r"].set_data(xout, 0.32 * np.sin(2 * np.pi * (xout - 1.6 * t) / lam_r))
    set_alpha(art["beam_parts"], beam_a)
    g_out = rk.window(t, 10.8, 15.3) * beam_a
    r_out = float(ease((t - 15.3) / 0.6)) * beam_a
    art["beam_out_g"].set_alpha(g_out)
    art["beam_out_g_t"].set_alpha(g_out)
    art["beam_out_r"].set_alpha(r_out)
    art["beam_out_r_t"].set_alpha(r_out)

    # D2 recorder, scene 5
    d_a = float(ease((t - D_APPEAR) / 0.4))
    draw_lane(art["d2"], t, stretch_d2, PERIOD_D2_S, D_APPEAR)
    set_alpha(art["d2_parts"], d_a)

    # colour ruler
    x = art["x"]
    ruler = float(ease((t - 10.6) / 0.6))
    for item in [art["sp"].patch, art["band"]] + list(art["sp"].get_xticklabels()):
        item.set_alpha(ruler)
    art["sp"].xaxis.label.set_alpha(ruler)
    art["sp"].spines["bottom"].set_alpha(ruler)
    art["sp"].tick_params(colors=rk.SOFT if ruler > 0.5 else PAPER)
    g = float(ease((t - 11.2) / 0.8))
    art["peak_g"].set_ydata(np.minimum(1.0 * g * lorentz(x, LASER_NM), 1.0))
    art["peak_g"].set_alpha(ruler)
    art["peak_g_t"].set_alpha(g)
    r = float(ease((t - 15.6) / 1.0))
    art["peak_r"].set_ydata(0.42 * r * lorentz(art["xr"], OUT_H2_NM))
    art["peak_r"].set_alpha(min(ruler, r))
    art["peak_r_t"].set_alpha(r)
    art["enlarged_t"].set_alpha(r)
    sh = rk.window(t, 17.0, 19.8)
    art["shift"].set_alpha(sh)
    art["shift_t"].set_alpha(sh)
    dd = float(ease((t - 20.8) / 1.0))
    art["peak_d"].set_ydata(0.38 * dd * lorentz(art["xd"], OUT_D2_NM))
    art["peak_d"].set_alpha(min(ruler, dd))
    art["peak_d_t"].set_alpha(dd)

    # comparison bars, scene 5
    grow = float(ease((t - 21.0) / 1.0))
    show = rk.window(t, 20.6, 24.5)
    art["bar_h"].set_width(0.95 * grow)
    art["bar_d"].set_width(0.95 * NU_D2_CM1 / NU_H2_CM1 * grow)
    for key in ("bar_h", "bar_d", "bar_h_t", "bar_d_t"):
        art[key].set_alpha(show)
    kit.art["note"].set_alpha((1 - show) * (1 - end))


if __name__ == "__main__":
    rk.main(episode=2, slug="ep02_bond_spring", title="The bond is a spring",
            scenes=SCENES, build=build, update=update, note=NOTE, end_teaser=END_TEASER)
