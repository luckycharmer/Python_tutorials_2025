---
name: new-episode
description: Use when asked to make, build or produce the next "Bonds to Devices" episode, a short vertical science video (reel, short) with its matching teaching notebook, or when a scheduled run says to check the posting tracker and build the episodes that are due.
---

# Building a Bonds to Devices episode

Each episode is one physics idea delivered twice from the same code: a 25–30 s vertical video for the public and a teaching notebook for class. The house style, watermarks, end card and renderer already exist in `notebooks/bonds_to_devices/reel_kit.py`. Your job is the physics, the picture and the checks, not the plumbing.

**Core principle:** every number on screen is computed from a cited source in the episode's physics module, and every frame is visibly Dr Junaid Ali's own design.

## Where things are

| What | Where |
|---|---|
| Posting schedule (owner edits it) | Google Drive folder "Bonds to Devices": sheet `18Zo4BNFqM7mbp3LDDA4Ek3BOf39cAE1T_hHQF77YiaM` (episodes 1–8) and sheet `1e05aud0x9DDzMaczViMrJr8Py93VyGS3CCbvm1E-BXs` (episodes 9–31). Drive folder id `1X2Er-mOiNw6e_Q1FxMKctF4FlscC62oM` |
| Episode list, dates and build status | `notebooks/bonds_to_devices/episodes.csv`: `production_due`, `post_date`, `status` (`planned` or `built`). This file alone is enough to run the skill |
| Shared style and renderer | `notebooks/bonds_to_devices/reel_kit.py`. Its top docstring has a cheat-sheet with every field, limit and helper you need; read that, not the whole file |
| Worked example to copy | `make_reel_ep01.py`, `h2_morse.py`, `01_why_hydrogen_comes_in_pairs.ipynb` |
| Notebook rules and checker | the `new-tutorial` skill and `.claude/skills/new-tutorial/scripts/check_notebook.py` |

All episode files live in `notebooks/bonds_to_devices/` and every command below runs from that folder unless it says otherwise. This overrides the `new-tutorial` skill's folder rule.

The Drive sheets cannot be edited cell by cell from here. Treat them as a read-only view of the schedule; `episodes.csv` holds the dates and the build status. Google Drive may not be connected in a scheduled run: check once with ToolSearch for "Google Drive". If it is missing, skip every Drive step and say so in the report.

## 1. Pick the work

1. If the owner names an episode, build that one and skip the rest of this step.
2. An episode is **due** when `episodes.csv` says `planned` and its `production_due` is on or before today + 8 days.
3. If Google Drive is available, read both sheets with `read_file_content`. Where a "Reel (main episode)" row's `Production due` differs from `episodes.csv`, the owner moved it: use the sheet's date and update `episodes.csv` to match.
4. Build the due episodes in date order, **at most two per run**. If none are due, report "Nothing due until <next production_due>" and stop without changing files.

## 2. Fact sheet before any code

Write `notebooks/bonds_to_devices/facts/epNN.md` with:

- the one idea (from `episodes.csv`), in one sentence a 12-year-old could repeat;
- every **measured** number that will appear on screen, its unit, its value and **two independent sources**, preferring primary data (NIST, CODATA, peer-reviewed papers). Look sources up with WebSearch and WebFetch; that is expected. A source you have not opened in this run is not a source: verify it or leave it out. If two sources disagree, use the primary one and note the spread;
- every **derived** number (computed from measured ones) with its arithmetic instead of a second source;
- every **conventional** choice (a 532 nm laser, 25 °C, 1 atm) marked as a choice;
- the physics claims the script makes, each checked for a trap: selection rules, sign conventions, idealisations, "always/never" wording.

Use the measured value of anything a viewer could observe (for example the H₂ fundamental, 4161 cm⁻¹) and keep model constants (the harmonic ωₑ, 4401 cm⁻¹) inside model equations. Never show both kinds side by side as if they were the same quantity.

Lesson from Episode 1: an end card once said infrared light shows the H₂ vibration. H₂ has no dipole, so it is infrared-inactive and only Raman sees it. Check every claim like this before it reaches the script.

## 3. Build the three files

`NN` is the two-digit episode number and `slug` comes from `episodes.csv` (for example `ep02_bond_spring`). The topic name is the slug without `epNN_` (`bond_spring`).

| File (in `notebooks/bonds_to_devices/`) | Contents |
|---|---|
| `facts/epNN.md` | The fact sheet from step 2 |
| `<topic>.py`, e.g. `bond_spring.py` | Physics module: constants with units in names and a sources docstring; small functions. No plotting. |
| `NN_<title in snake case>.ipynb`, e.g. `02_the_bond_is_a_spring.ipynb` | Follow the `new-tutorial` skill's structure and checker. Title `# Tutorial NN (Bonds to Devices) — <title>`. Import the physics module. Validate against a measured value the model was not given. Import `display` from `IPython.display` if you use it. |
| `make_reel_epNN.py` | Copy the structure of `make_reel_ep01.py`: `SCENES`, `build(fig, kit)`, `update(art, t, kit)`, then `rk.main(...)`. Episode-specific drawing helpers live in this script. Import every number from the physics module. |

The scene list is the script. Shape it like this:

- 5 scenes lasting 22–26 s in total (4–6 s each); `end_teaser` adds a 3.5 s end card, so the video is 25–30 s;
- headline: at most 2 lines of about 18 characters; subline: at most 2 lines of about 42 characters;
- one equation per scene in `Scene.eq` (mathtext), at most about 45 rendered characters, numbers filled in with f-strings from the module;
- `end_teaser` names the next episode from `episodes.csv`;
- `note` says where the numbers come from and how much motion is slowed, if any, in at most 95 characters;
- numbers in headlines and sublines are in words or plain figures ("125 trillion", "74 pm"); scientific notation belongs in the equation strip;
- anything drawn bigger or slower than reality is labelled on screen ("Raman peaks enlarged").

Draw only inside `kit.content_axes(...)` (the CONTENT region) and `kit.extra_axes()`. With a two-line headline and subline, keep drawings below y = 0.715. The kit adds the header, equation strip, watermarks and end card itself.

## 4. Originality gate (must pass before rendering)

The picture must be a **new visual metaphor for this topic** in the house style. Confirm every line:

- [ ] Paper background, navy ink, coral moving object, Inter type, from `reel_kit` colours. No dark or black backgrounds.
- [ ] One concrete metaphor a viewer can name in three words (ball in a valley, atoms on a spring, water level, a ladder, a gate, a slope).
- [ ] No glowing particle clouds, neon sparkle, spaced-out monospace capital labels, italic serif headlines, or small grey disclaimer blocks in monospace. These are the look of other science pages.
- [ ] Headline and subline wording is your own. Do not search for, watch, download or describe other creators' videos on this topic.
- [ ] The corner credit, centre watermark and end card come from the kit unchanged.

## 5. Check, render, record

1. `python make_reel_epNN.py --sheet` writes `output/<slug>_sheet.png` (every scene's midpoint plus the end card). View it once. Fix overlaps, text running off the frame and unreadable equations, then run `--sheet` again. At most three rounds.
2. Render the full video once: `python make_reel_epNN.py`. Confirm with `ffprobe` that it is 1080×1920, 30 fps, 25–30 s, with the copyright tag.
3. Copy `output/<slug>.mp4` to `videos/<slug>.mp4` (the `output/` folder is not committed).
4. Run `python .claude/skills/new-tutorial/scripts/check_notebook.py --execute notebooks/bonds_to_devices/NN_*.ipynb` from the repository root. Every line must be OK or an accepted WARN.
5. Set the episode to `built` in `episodes.csv`. In `notebooks/bonds_to_devices/README.md`, change the episode's row in the Episodes table to **Ready** and add sections headed `## Episode NN files`, `## Episode NN voice-over` and `## Episode NN post caption`, in the same format as Episode 1's. In the repository root `README.md`, add the episode to the "Bonds to Devices series" list.
6. Commit with a clear message and push to the branch this session was given. Never push to `main`; do not open a pull request.
7. If Google Drive is available, create one Google Doc in the Drive folder (`parentId` above) titled `Episode NN – ready to post` (two digits, e.g. `Episode 02 – ready to post`), with the caption, voice-over, the video path, the branch and commit, and any open questions. Use `create_file` with `textContent` and `contentMimeType: text/plain`.

## 6. Report

End with a short report: episodes built, the files, the numbers you checked and their sources, the checker result, the Drive doc link, and anything that needs the owner's decision. If a gate failed and you could not fix it, say which and stop rather than publish a weak episode.

## Keep each run light

- Read the top docstring of `reel_kit.py` and the example episode once; do not read them again.
- Use `--sheet` for previews; at most three rounds. Render the full MP4 once, at the end.
- At most two episodes per run.
- Do not upload videos to Drive: base64 uploads cost far more than they help. The video lives in `videos/` on GitHub.

## Common mistakes

| Mistake | Fix |
|---|---|
| Typing numbers into the script by hand | Compute them in the physics module and format them with f-strings |
| Copying another page's look because it is popular | Run the originality gate; invent a metaphor for this topic |
| A claim that is almost right (IR for H₂, "electrons orbit") | Fact sheet with two sources and a trap check, before code |
| Headline or equation running off the frame | Respect the character limits; check the contact sheet |
| Drawing outside CONTENT and covering the equation strip | Only `kit.content_axes` and `kit.extra_axes` |
| Showing a model constant next to a measured value as if they were the same | Measured values on screen; model constants inside model equations |
| Citing a source from memory | Open it with WebFetch in this run, or leave it out |
| Rebuilding an episode that already exists | `episodes.csv` decides what is built, not the Drive sheet's Status |
