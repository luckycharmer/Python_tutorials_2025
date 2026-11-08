# Bonds to Devices

A short series that starts with two hydrogen atoms and ends with a working photodetector. Each episode has two parts made from the same Python code:

- a **notebook** for class, which follows the repository's release criteria; and
- a **vertical video** (1080 × 1920, about 28 seconds) for a general audience, for Facebook Reels, Instagram, YouTube Shorts or a lecture opener.

Because the video and the notebook import the same physics module, every number on screen can be traced to a notebook cell and a published reference.

## Episodes

| # | Title | The one idea | Key checked number | Status |
|---|---|---|---|---|
| 1 | Why hydrogen comes in pairs | Atoms bond because the pair has lower energy | H₂ bond energy 4.48 eV (432 kJ/mol) at 74 pm | **Ready** |
| 2 | The bond is a spring | Bonds vibrate at fixed frequencies; Raman light reveals them; heavier isotopes vibrate slower | H₂ vibration 4161 cm⁻¹ (532 nm in, 683 nm out); D₂ 2994 cm⁻¹ | **Ready** |
| 3 | From two atoms to a crystal | Many atoms turn sharp levels into bands | Silicon: 5 × 10²² atoms per cm³ | Planned |
| 4 | Why glass is clear and silicon is not | The band gap decides colour and conduction | Si gap 1.12 eV, GaAs 1.42 eV, SiO₂ about 9 eV | Planned |
| 5 | Doping: one atom in a million | Tiny impurities control conductivity | Intrinsic Si about 10¹⁰ carriers per cm³ at 300 K | Planned |
| 6 | The one-way street | A p–n junction lets current flow one way | Shockley diode equation, thermal voltage about 26 mV at room temperature | Planned |
| 7 | Light in, current out | A photon makes an electron–hole pair; that is a photodetector | Ideal responsivity 0.81 A/W at 1000 nm | Planned |
| 8 | Measuring a real device | Turning an I–V sweep into device numbers | Links to the I–V and photodetector notebooks | Planned |

Planned numbers are textbook values and will be checked again against primary sources when each episode is built.

## How new episodes are made

- `reel_kit.py` holds the shared house style: frame, equation strip, watermarks, end card and renderer. Episode scripts only add their physics and picture.
- `episodes.csv` lists all 31 planned episodes and which are built.
- The `new-episode` skill (`.claude/skills/new-episode/`) builds the next due episode from the Google Drive posting tracker: fact sheet, physics module, notebook, video, checks, commit and a ready-to-post Google Doc.
- Finished videos are committed to `videos/`.

## Episode 1 files

| File | What it is |
|---|---|
| `01_why_hydrogen_comes_in_pairs.ipynb` | Class notebook: energy curve, zero-point energy, bond energy, thermal comparison, validation checks |
| `h2_morse.py` | Constants and Morse model, shared by the notebook and the video |
| `make_reel_ep01.py` | Renders the video to `output/ep01_h2_bond.mp4` (a copy is kept in `videos/`) |
| `facts/ep01.md` | Fact sheet: every on-screen number with two sources |
| `assets/lab_logo.png` | Lab logo for the end card (add your own; see `assets/README.md`) |

To make the video yourself, install `ffmpeg` (a separate program, not a Python package), then run from this folder:

```bash
python make_reel_ep01.py                   # full video, about 2 minutes on a laptop
python make_reel_ep01.py --stills 2 10 20  # quick PNG previews at those seconds
python make_reel_ep01.py --logo path/to/logo.png  # use a logo stored elsewhere
```

The end card credits Dr Junaid Ali and the Optoelectronics Research Laboratory; edit `PRESENTER`, `ROLE_LINE`, `LAB_LINE` and `UNI_LINE` near the top of the script to change it. Each scene shows its equation in a strip below the chart (ideal gas, Morse curve, zero-point energy, bond energy, bond energy against thermal energy), with the numbers filled in from the same code. Every frame carries "© Dr Junaid Ali" in the top-right corner (with the logo, if supplied) and a faint watermark over the energy valley, so the credit survives if someone trims the end card. Your name and copyright are also written into the MP4 file's metadata. Change the wording with `WATERMARK_CORNER` and `WATERMARK_CENTRE`. The `output/` folder is not committed. The video is silent so you can add music or your own voice in CapCut, Canva or the Facebook editor.

## Episode 1 voice-over (optional, about 28 seconds)

Timed to the on-screen scenes. Read at a relaxed pace.

| Time | Say |
|---|---|
| 0–4 s | Hydrogen gas is made of pairs. Every litre holds about twenty-five thousand billion billion of them. Why not single atoms? |
| 4–9 s | Let two atoms meet. The closer they get, the lower their energy, like a ball rolling downhill. |
| 9–14 s | The valley floor is at seventy-four picometres. But they never rest there. They keep swinging. |
| 14–19 s | To prise them apart, you have to climb out of the valley: four point four eight electronvolts. |
| 19–24 s | A thermal kick at room temperature carries less than one hundred and seventieth of that. So they stay paired. |
| 24–28 s | Next time: the bond as a spring, and how light reveals it. |

## Episode 1 post caption (copy and paste)

> Why does hydrogen gas come as H₂ and not as single atoms?
>
> Bring two hydrogen atoms together and their energy drops, reaching its lowest point when the nuclei are 74 picometres apart. Pulling them apart again takes 4.48 eV, which is 432 kJ for every mole of hydrogen. Everyday heat supplies about 0.026 eV per molecule, roughly 170 times too little. So hydrogen stays paired.
>
> Every number here was calculated in Python from measured data. The notebook and code are free on GitHub: github.com/luckycharmer/Python_tutorials_2025
>
> Episode 1 of Bonds to Devices: from a single chemical bond to a working light sensor.
>
> #Physics #Chemistry #Hydrogen #ChemicalBond #Python #ScienceEducation #COMSATS

## Accuracy notes for presenters

- **74 pm** is the bottom of the energy curve. A real molecule is always vibrating, so the bond length measured from its rotation spectrum is slightly longer, about 75 pm.
- There are two depths. The curve's bottom is 4.75 eV below two free atoms, but the molecule can't sit there: its lowest allowed level is 0.27 eV higher. That is why the bond energy is 4.48 eV, not 4.75 eV.
- The spring and the rolling ball are teaching pictures. The spring is not a physical object, and the ball shows the pair's energy at each gap. All on-screen energies come from the Morse curve.
- "Where H₂ actually sits" marks the lowest allowed vibration level, 0.27 eV above the valley floor.
- The swing in the video is slowed by about 1.6 × 10¹⁴ times and drawn as a classical motion.

## Episode 2 files

| File | What it is |
|---|---|
| `02_the_bond_is_a_spring.ipynb` | Class notebook: frequency and period, bond stiffness, anharmonicity, Raman shift, isotope prediction, validation checks |
| `bond_spring.py` | Constants and spring/Raman functions, shared by the notebook and the video |
| `make_reel_ep02.py` | Renders the video to `output/ep02_bond_spring.mp4` (a copy is kept in `videos/`) |
| `facts/ep02.md` | Fact sheet: every on-screen number with two sources, and the trap checks |

```bash
python make_reel_ep02.py                     # full video
python make_reel_ep02.py --stills 2.5 7.5 12.5 17.5 22.5 26.5   # PNG previews
```

The picture is a ball on a spring that draws its own wave on moving paper, a green laser beam that comes back red and lands on a colour ruler, and finally a heavier deuterium ball that draws a slower wave. The equation strip shows the spring formula, ν = c ν̃, the laser photon energy, the Raman energy balance and the H₂/D₂ ratio, with the numbers filled in from `bond_spring.py`.

## Episode 2 voice-over (optional, about 28 seconds)

Timed to the on-screen scenes. Read at a relaxed pace.

| Time | Say |
|---|---|
| 0–5 s | A chemical bond is a spring. Pull the two atoms apart and it pulls them back. Let go, and it bounces. |
| 5–10 s | And it always rings at the same note. Hydrogen swings about a hundred and twenty-five trillion times a second. Every hydrogen molecule, the same. |
| 10–15 s | How do we hear that note? Hydrogen has no electric dipole, so infrared light barely notices it. So we shine a green laser instead. |
| 15–20 s | Most of the light bounces off unchanged. But a few photons give the bond one step of vibration, and come out red: green in, red out. |
| 20–24.5 s | Swap in deuterium, twice as heavy. Same spring, heavier ball, lower note: about one point four times slower. |
| 24.5–28 s | Next time: from two atoms to a crystal. |

## Episode 2 post caption (copy and paste)

> A chemical bond is a spring, and it rings at one fixed note.
>
> The hydrogen molecule vibrates about 125 trillion times a second (4161 cm⁻¹). H₂ has no electric dipole, so infrared light barely sees it. Shine a green 532 nm laser on it instead: a few scattered photons hand the bond one step of vibration (0.52 eV) and come out red, at 683 nm. That colour shift is Raman scattering, and it measures the bond's note.
>
> Swap hydrogen for deuterium, twice as heavy: same spring, lower note, 2994 cm⁻¹. The ratio is 1.39, just under √2, because a real bond is not quite a perfect spring.
>
> Every number here was calculated in Python from measured data. The notebook and code are free on GitHub: github.com/luckycharmer/Python_tutorials_2025
>
> Episode 2 of Bonds to Devices: from a single chemical bond to a working light sensor.
>
> #Physics #Chemistry #Raman #Spectroscopy #Hydrogen #Python #ScienceEducation #COMSATS

## Episode 2 accuracy notes for presenters

- **One ball, two atoms.** The single ball on a spring stands for the two atoms swinging against each other (the reduced mass). The wave on the paper shows how far the bond is stretched over time, slowed by about 1.2 × 10¹⁴ times. The D₂ wave uses the same slowdown, so the two speeds are in the true ratio.
- **Which number is the note?** 4161 cm⁻¹ is the measured spacing of the lowest two vibrational levels, and it is what Raman scattering measures. The textbook ωₑ = 4401 cm⁻¹ describes an ideal spring and is not shown on screen.
- **Infrared.** H₂ is not completely invisible to infrared: very weak quadrupole lines exist. "Barely sees it" is the accurate wording.
- **Green in, red out.** Only a tiny fraction of the scattered light is shifted; the red peaks on the colour ruler are drawn enlarged. The blue-shifted (anti-Stokes) line is negligible at room temperature and is not shown.
- **Not exactly √2.** The mass doubles, so a perfect spring would be √2 = 1.41 times slower. The measured ratio is 1.39 because the real bond softens as it stretches.
