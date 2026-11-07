---
name: new-tutorial
description: Write, extend, or review a teaching notebook in this repository. Use when asked to create a new tutorial, add a lesson for a roadmap module, turn an analysis into a notebook, or check that an existing notebook meets the release criteria in CONTRIBUTING.md and ROADMAP.md.
---

# Writing a tutorial notebook

This repository holds research-grade teaching notebooks for physics, materials science, and engineering students. A good notebook here is short, runs top to bottom from a clean environment, and never overstates what the data shows. Follow the steps below in order.

## 1. Pin down the lesson before writing anything

Work out, from the request and the README's learning path (modules 00 to 08):

- the module number and a short topic, which give the file path: `notebooks/<NN>_<module-slug>/<NN>_<topic_slug>.ipynb` (for example `notebooks/01_core/02_vectorised_resistivity.ipynb`)
- the audience and what they are assumed to know already
- three to five learning objectives, each one something a student can actually do afterwards
- the data: measured, simulated, or synthetic. If the user offers real data, ask whether they have the right to publish it. Never add unpublished, student-owned, or collaborator-owned data without written permission.

If the topic or data source is unclear, ask one short question instead of guessing.

## 2. Build the notebook in the house structure

Use these sections, in this order. `notebooks/01_core/01_arrays_units_iv_plot.ipynb` is the reference example; match its tone and length.

1. **Title and context** (markdown, `# Tutorial NN — Title`). One paragraph. State plainly whether the data is measured, simulated, or synthetic.
2. **Learning objectives** (markdown, `## Learning objectives`). A bulleted list.
3. **Imports and environment check** (code). Import only what is used and print the versions of Python and each scientific library.
4. **Data source and units** (markdown + code). Put units in variable and column names: `voltage_V`, `current_mA`, `wavelength_nm`, `thickness_um`.
5. **Analysis** (several short markdown + code pairs). Explain the physics in one or two sentences before each calculation. Make unit conversions explicit (`current_A = current_mA * 1e-3`), never silent.
6. **Validation or residual checks** (code). Include at least one: residuals, a known limiting case, a dimensional check, comparison with a textbook value, or an `assert` on a physically reasonable range.
7. **Interpretation** (markdown, `## Interpretation and checks`). Keep the calculation separate from the claim. Say what the result does not prove.
8. **Exercise** (markdown, `## Exercise`). Three or four numbered tasks that go from easy to open-ended.
9. **References** (markdown, `## References`), whenever a method, dataset, constant, or adapted code comes from somewhere else.

## 3. Coding rules

- Use only the libraries in `requirements.txt` (NumPy, pandas, Matplotlib, SciPy, JupyterLab). If something else is truly needed, say so and add it to `requirements.txt` with version bounds.
- Seed any random numbers: `rng = np.random.default_rng(42)`.
- Keep each code cell short enough to explain in one breath.
- Every figure needs axis labels with units, a legend when there is more than one series, and `fig.tight_layout()`. Don't use a colour map or axis range that exaggerates the effect.
- Report fitted values together with their uncertainty when the method gives one (for example `scipy.optimize.curve_fit` with `np.sqrt(np.diag(pcov))`).
- No file paths that only exist on one machine, no credentials, no personal information.

## 4. Writing style

- Plain, direct sentences aimed at a second-year undergraduate.
- British spelling, to match the existing material (`organise`, `analyse`, `colour`).
- No filler, no hype, no "In this tutorial we will dive into…". Start with the point.
- Hedge physical claims honestly ("consistent with", "suggests"). Never write "proves" about a fit.

## 5. Check it before handing it over

Run the checker from the repository root:

```bash
python .claude/skills/new-tutorial/scripts/check_notebook.py notebooks/<path>.ipynb
```

It checks the required sections, the data-type statement, units in names, seeding of random numbers, leftover personal paths, and stored outputs. Add `--execute` to run every cell in a fresh kernel too; that needs `jupyter` from `requirements.txt` to be installed. Fix every `FAIL` line. Treat `WARN` lines as things to decide on, not ignore.

Commit notebooks with their outputs cleared, the way tutorial 01 is stored, so diffs stay readable.

## 6. Finish

- Add the new notebook to the "Start here" or contents section of `README.md` if it is the next tutorial in the path.
- Tell the user the file path, what the notebook teaches, the data type, and what the checker reported, including anything left as a warning.
