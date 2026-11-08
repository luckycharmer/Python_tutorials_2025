#!/usr/bin/env python3
"""Episode 1 reel: Why hydrogen comes in pairs.

Picture: two atoms joined by a spring, above an energy valley that a ball
rolls along, with an energy gauge beside it. All shared styling (header,
equation strip, watermarks, end card, rendering) comes from reel_kit.py.
Every number on screen comes from h2_morse.py, the module the notebook uses.

Usage (from this folder):
    python make_reel_ep01.py                     # writes output/ep01_h2_bond.mp4
    python make_reel_ep01.py --stills 2 10 20    # PNG frames at those seconds only
    python make_reel_ep01.py --logo my_logo.png  # logo from another path
"""

import numpy as np
from matplotlib.patches import Circle, Rectangle

import h2_morse as h2
import reel_kit as rk
from reel_kit import CORAL, GREEN, INK, PAPER, SAND, SANS, SOFT, WATER, Scene, ease

# ---------------------------------------------------------------- physics on screen
R_EQ_PM = h2.BOND_LENGTH_PM
DEPTH_EV = h2.WELL_DEPTH_EV
LEVEL0_EV = float(h2.morse_level_eV(0))
INNER_PM, OUTER_PM = h2.turning_points_pm(LEVEL0_EV)
BREAK_EV = h2.D0_MEASURED_EV
KT_ROOM_EV = h2.K_B_EV_PER_K * 298.15
FREQ_HZ = h2.vibration_frequency_Hz()
PAIRS_PER_LITRE = 101325 / (1.380649e-23 * 298.15) * 1e-3   # ideal gas, 1 atm, 25 °C
ZERO_POINT_EV = LEVEL0_EV + DEPTH_EV
HALF_H_NU_EV = 0.5 * h2.H_EV_S * FREQ_HZ

VIB_PERIOD_S = 1.2
SLOWDOWN = FREQ_HZ * VIB_PERIOD_S
FAR_PM = 290.0

SCENES = [
    Scene(0.0, 4.0, "Hydrogen gas\nis made of pairs",
          f"About {rk.sci(PAIRS_PER_LITRE)} pairs in every litre.\nWhy not single atoms?",
          "Ideal gas at 1 atm and 25 °C",
          rf"$N/V = P\,/\,k_BT \approx {rk.sci_tex(PAIRS_PER_LITRE)}\ \mathrm{{L^{{-1}}}}$"),
    Scene(4.0, 9.0, "Let two atoms meet",
          "The closer they get, the lower their energy.\nThe ball rolls downhill.",
          "Energy curve (Morse model)",
          r"$E(r) = D_e\left[\left(1-e^{-a(r-r_e)}\right)^2-1\right]$"),
    Scene(9.0, 14.0, f"The valley floor:\n{R_EQ_PM:.0f} pm apart",
          "They never rest on the floor. A quantum\nminimum of motion keeps them swinging.",
          rf"Zero-point energy,  $\nu = {rk.sci_tex(FREQ_HZ)}$ Hz",
          rf"$E_0 \approx \frac{{1}}{{2}}h\nu = {HALF_H_NU_EV:.2f}\ \mathrm{{eV}}$"),
    Scene(14.0, 19.0, "Prise them apart",
          f"Climbing out of the valley\ncosts {BREAK_EV:.2f} eV per pair.",
          "Energy to break the bond",
          rf"$D_0 = D_e - E_0 = {DEPTH_EV:.2f} - {ZERO_POINT_EV:.2f} = "
          rf"{DEPTH_EV - ZERO_POINT_EV:.2f}\ \mathrm{{eV}}$"),
    Scene(19.0, 24.5, "So why do they\nstay paired?",
          "Each thermal kick at 25 °C carries\nonly a tiny fraction of that.",
          "Bond energy against thermal energy at 25 °C",
          rf"$D_0\,/\,k_BT = {BREAK_EV:.2f}\,/\,{KT_ROOM_EV:.4f} \approx "
          rf"{BREAK_EV / KT_ROOM_EV:.0f}$"),
]
END_TEASER = "Episode 2: the bond as a spring,\nand how light reveals its vibration."
NOTE = ("Energies from measured H₂ constants (Morse model).  "
        f"Swing slowed about {rk.sci(SLOWDOWN)} times.")


# ---------------------------------------------------------------- motion
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


def spring_xy(x1, x2, coils=6, amp=8.0, n=400):
    s = np.linspace(0, 1, n)
    x = x1 + (x2 - x1) * s
    lead = 0.12
    body = np.clip((s - lead) / (1 - 2 * lead), 0, 1)
    y = amp * np.sin(2 * np.pi * coils * body) * ((s > lead) & (s < 1 - lead))
    return x, y


# ---------------------------------------------------------------- picture
def build(fig, kit):
    art = {}
    # atoms on a spring
    st = kit.content_axes(bottom=0.585, top=0.695)
    st.set_axis_off()
    half_w = 190.0
    half_h = half_w * (0.11 * rk.HEIGHT_PX) / rk.WIDTH_PX
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

    # energy valley
    ax = kit.content_axes(left=0.10, width=0.70, bottom=0.31, top=0.565)
    r = np.linspace(52, 330, 700)
    ymin, ymax = -5.4, 0.9
    ax.fill_between(r, h2.morse_energy_eV(r), ymin, color=SAND, lw=0)
    ax.plot(r, h2.morse_energy_eV(r), color=INK, lw=3.5)
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
    kit.style_axis(ax, xlabel="gap between the two nuclei (picometres)")
    ax.spines["left"].set_visible(False)
    ax.get_xticklabels()[0].set_color(CORAL)
    ax.get_xticklabels()[0].set_weight("bold")

    # energy gauge on the same energy scale
    g = kit.content_axes(left=0.84, width=0.06, bottom=0.31, top=0.565)
    g.set_xlim(0, 1)
    g.set_ylim(ymin, ymax)
    g.set_axis_off()
    g.add_patch(Rectangle((0.25, -DEPTH_EV), 0.5, DEPTH_EV, fc="#ffffff", ec=INK, lw=2,
                          zorder=1))
    art["gauge_fill"] = g.bar([0.5], [0], width=0.5, bottom=[0], color=CORAL, alpha=0.85,
                              zorder=2)[0]
    g.text(0.5, 0.35, "energy", color=SOFT, family=SANS, size=19, ha="center")
    g.text(0.5, -DEPTH_EV - 0.35, f"−{DEPTH_EV:.2f}", color=SOFT, family=SANS, size=16,
           ha="center", va="top")
    art["gauge_val"] = fig.text(0.87, 0.285, "", color=CORAL, family=SANS, size=30,
                                weight="bold", ha="center", va="top")
    art["gauge_unit"] = fig.text(0.87, 0.263, "eV", color=SOFT, family=SANS, size=19,
                                 ha="center", va="top")
    (art["climb"],) = g.plot([0.92, 0.92], [LEVEL0_EV, 0], color=GREEN, lw=4, alpha=0,
                             solid_capstyle="butt")
    art["climb_label"] = ax.text(250, -2.3, f"{BREAK_EV:.2f} eV\nto climb out", color=GREEN,
                                 family=SANS, size=24, weight="bold", ha="center", alpha=0)

    # bond against heat bars
    cb = kit.extra_axes()
    cb.set_xlim(0, 1.0)
    cb.set_ylim(-0.5, 1.6)
    art["bar_bond"] = cb.barh([1.0], [0], height=0.45, color=INK)[0]
    art["bar_heat"] = cb.barh([0.0], [0], height=0.45, color=CORAL)[0]
    art["bar_bond_t"] = cb.text(0, 1.38, f"Bond: {BREAK_EV:.2f} eV", color=INK, family=SANS,
                                size=21, weight="semibold", alpha=0)
    art["bar_heat_t"] = cb.text(0.035, 0.0, f"Heat kick at 25 °C: {KT_ROOM_EV:.3f} eV  "
                                f"(about 1/{BREAK_EV / KT_ROOM_EV:.0f})", color=CORAL,
                                family=SANS, size=21, weight="semibold", va="center", alpha=0)
    return art


def update(art, t, kit):
    d = distance_at(t)
    xa, xb = -d / 2, d / 2
    for c, s, lab, x in zip(art["atoms"], art["shines"], art["atom_labels"], (xa, xb)):
        c.center = (x, 0)
        s.center = (x - 8, 9)
        lab.set_position((x, -1))
    sx, sy = spring_xy(xa + 24, xb - 24)
    art["spring"].set_data(sx, sy)
    art["spring"].set_alpha(1 - ease((d - 140) / 50))
    art["gap"].set_text(f"{d:.0f} pm")

    energy = float(h2.morse_energy_eV(d))
    art["ball"].set_offsets([[d, energy]])
    art["ball_shadow"].set_offsets([[d, energy - 0.08]])
    water = ease((t - 9.6) / 0.8)
    art["water"].set_alpha(0.55 * water)
    art["water_label"].set_alpha(water)

    art["gauge_fill"].set_height(energy)
    art["gauge_val"].set_text(rk.minus(f"{energy:.2f}"))
    climb = rk.window(t, 15.5, 19.0, fade=0.5)
    art["climb"].set_alpha(climb)
    art["climb_label"].set_alpha(climb)

    grow = ease((t - 19.8) / 1.2)
    show = rk.window(t, 19.3, 24.5)
    art["bar_bond"].set_width(1.0 * grow)
    art["bar_heat"].set_width(max(KT_ROOM_EV / BREAK_EV * grow, 0.004 * grow))
    for key in ("bar_bond", "bar_heat", "bar_bond_t", "bar_heat_t"):
        art[key].set_alpha(show)

    end = kit.end_fade(t)
    kit.art["note"].set_alpha((1 - show) * (1 - end))
    art["gauge_val"].set_alpha(1 - end)
    art["gauge_unit"].set_alpha(1 - end)
    art["gap"].set_alpha(1 - end)


if __name__ == "__main__":
    rk.main(episode=1, slug="ep01_h2_bond", title="Why hydrogen comes in pairs",
            scenes=SCENES, build=build, update=update, note=NOTE, end_teaser=END_TEASER)
