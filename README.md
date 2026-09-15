# Scientific Python Tutorials

Practical, research-oriented Python tutorials for students and researchers in physics, materials science, and engineering.

This repository is maintained by **Dr Junaid Ali**, Associate Professor of Physics and Head of the Optoelectronics Research Laboratory at COMSATS University Islamabad. It is being developed as a teaching and reproducible-research resource rather than as a collection of disconnected code examples.

## Start here

The first executable notebook is:

- [Tutorial 01 — Arrays, units, and an I–V plot](notebooks/01_core/01_arrays_units_iv_plot.ipynb)

It uses a clearly labelled synthetic dataset to introduce arrays, unit conversion, linear fitting, residual inspection, plotting, and cautious physical interpretation.

## Repository contents

| Item | Purpose |
|---|---|
| [ROADMAP.md](ROADMAP.md) | Development sequence and release criteria |
| [requirements.txt](requirements.txt) | Version-bounded Python dependencies |
| [notebooks/](notebooks/) | Executable teaching notebooks |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Scientific, ethical, and technical contribution rules |
| [CITATION.cff](CITATION.cff) | Machine-readable citation information |

## Scope

The tutorials will show how Python can be used to:

- organise, clean, and inspect experimental data;
- visualise measurements clearly and without distorting them;
- fit physical models and report uncertainty;
- analyse electrical, optical, spectroscopic, and materials-characterisation data;
- automate repetitive laboratory calculations; and
- document an analysis so that another researcher can reproduce it.

## Planned learning path

| Module | Focus |
|---|---|
| 00 | Python and Jupyter setup |
| 01 | NumPy arrays and scientific calculations |
| 02 | Data handling with pandas |
| 03 | Publication-quality plotting with Matplotlib |
| 04 | Curve fitting, residuals, and uncertainty |
| 05 | Electrical and optoelectronic measurements |
| 06 | Spectroscopy and materials-characterisation workflows |
| 07 | Reproducible notebooks, version control, and reporting |
| 08 | Introductory machine learning for materials datasets |

## Intended audience

- Undergraduate and graduate physics students
- Early-career researchers
- Experimental scientists beginning computational analysis
- Teachers developing blended or laboratory-based learning activities

The tutorials assume basic familiarity with scientific measurements but do not assume advanced programming experience.

## Quick start

A clean virtual environment is recommended.

```bash
git clone https://github.com/luckycharmer/Python_tutorials_2025.git
cd Python_tutorials_2025
python -m venv .venv
```

Activate the environment, then install the dependencies and open JupyterLab:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab
```

A fully pinned environment will be issued with the first versioned tutorial release.

## Reproducibility standard

Each released tutorial should include:

1. a stated learning objective;
2. a small, documented dataset or a transparent data source;
3. executable code with explanatory notes;
4. physical interpretation of the output;
5. checks for units, assumptions, and uncertainty; and
6. a short exercise or extension task.

Measured, simulated, and synthetic data must be identified explicitly.

## Repository status

The repository foundation and first tutorial are now available. Further notebooks, documented datasets, exercises, and instructor resources will be added incrementally after scientific and reproducibility checks.

## Academic profile

- [ORCID: 0000-0002-5463-4442](https://orcid.org/0000-0002-5463-4442)
- [Google Scholar](https://scholar.google.com/citations?user=d4rT0dgAAAAJ)

## Contributions and reuse

Suggestions, corrections, and reproducibility reports are welcome through GitHub Issues. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before proposing substantial additions.

A formal licence has not yet been selected. Until one is added, reuse beyond what copyright law permits requires the author's permission.
