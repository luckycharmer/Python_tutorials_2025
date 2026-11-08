# Bonds to Devices

A short series that starts with two hydrogen atoms and ends with a working photodetector. Each episode has two parts made from the same Python code:

- a **notebook** for class, which follows the repository's release criteria; and
- a **vertical video** (1080 × 1920, about 28 seconds) for a general audience, for Facebook Reels, Instagram, YouTube Shorts or a lecture opener.

Because the video and the notebook import the same physics module, every number on screen can be traced to a notebook cell and a published reference.

## Episodes

| # | Title | The one idea | Key checked number | Status |
|---|---|---|---|---|
| 1 | Why hydrogen comes in pairs | Atoms bond because the pair has lower energy | H₂ bond energy 4.48 eV (432 kJ/mol) at 74 pm | **Ready** |
| 2 | The bond is a spring | Bonds vibrate at fixed frequencies; light reveals them | H₂ vibration 4161 cm⁻¹ (Raman); D₂ is slower | Planned |
| 3 | From two atoms to a crystal | Many atoms turn sharp levels into bands | Silicon: 5 × 10²² atoms per cm³ | Planned |
| 4 | Why glass is clear and silicon is not | The band gap decides colour and conduction | Si gap 1.12 eV, GaAs 1.42 eV, SiO₂ about 9 eV | Planned |
| 5 | Doping: one atom in a million | Tiny impurities control conductivity | Intrinsic Si about 10¹⁰ carriers per cm³ at 300 K | Planned |
| 6 | The one-way street | A p–n junction lets current flow one way | Shockley diode equation, thermal voltage about 26 mV at room temperature | Planned |
| 7 | Light in, current out | A photon makes an electron–hole pair; that is a photodetector | Ideal responsivity 0.81 A/W at 1000 nm | Planned |
| 8 | Measuring a real device | Turning an I–V sweep into device numbers | Links to the I–V and photodetector notebooks | Planned |

Planned numbers are textbook values and will be checked again against primary sources when each episode is built.

## Episode 1 files

| File | What it is |
|---|---|
| `01_why_hydrogen_comes_in_pairs.ipynb` | Class notebook: energy curve, zero-point energy, bond energy, thermal comparison, validation checks |
| `h2_morse.py` | Constants and Morse model, shared by the notebook and the video |
| `make_reel_ep01.py` | Renders the video to `output/ep01_h2_bond.mp4` |
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
