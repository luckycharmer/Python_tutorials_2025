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
| Which episodes are already built | `notebooks/bonds_to_devices/episodes.csv`, column `status` (`planned` or `built`) |
| Shared style and renderer | `notebooks/bonds_to_devices/reel_kit.py` (read only its top docstring) |
| Worked example to copy | `make_reel_ep01.py`, `h2_morse.py`, `01_why_hydrogen_comes_in_pairs.ipynb` |
| Notebook rules and checker | the `new-tutorial` skill and `.claude/skills/new-tutorial/scripts/check_notebook.py` |

The Drive sheets cannot be edited cell by cell from here. Treat them as read-only schedule; record build progress in `episodes.csv`.

## 1. Pick the work

1. If the owner names an episode, build that one and skip the rest of this step.
2. Read both Drive sheets with the Google Drive `read_file_content` tool. Collect the "Reel (main episode)" rows.
3. An episode is **due** when its `Production due` date is on or before today + 8 days and `episodes.csv` says `planned`.
4. Build the due episodes in date order, **at most two per run**. If none are due, report "Nothing due until <next production date>" and stop. If the Drive tool is unavailable, use the earliest `planned` row in `episodes.csv` instead and say so in the report.

## 2. Fact sheet before any code

Write `notebooks/bonds_to_devices/facts/epNN.md` with:

- the one idea (from `episodes.csv`), in one sentence a 12-year-old could repeat;
- every number that will appear on screen, its unit, its value and **two independent sources**, preferring primary data (NIST, CODATA, peer-reviewed papers, standard textbooks). If two sources disagree, use the primary one and note the spread;
- the physics claims the script makes, each checked for a trap: selection rules, sign conventions, idealisations, "always/never" wording.

Lesson from Episode 1: an end card once said infrared light shows the H₂ vibration. H₂ has no dipole, so it is infrared-inactive and only Raman sees it. Check every claim like this before it reaches the script.

## 3. Build the three files

Use the next episode number `NN` and the `slug` from `episodes.csv`.

| File | Contents |
|---|---|
| `<topic>.py` physics module | Constants with units in names and a sources docstring; small functions. No plotting. |
| `NN_<topic>.ipynb` | Follow the `new-tutorial` skill exactly. Title `# Tutorial NN (Bonds to Devices) — <title>`. Import the physics module. Validate against a measured value the model was not given. |
| `make_reel_epNN.py` | Copy the structure of `make_reel_ep01.py`: `SCENES`, `build(fig, kit)`, `update(art, t, kit)`, then `rk.main(...)`. Import every number from the physics module. |

The scene list is the script. Shape it like this:

- 5 scenes plus the kit's end card, 25–30 s total, 4–6 s per scene;
- headline: at most 2 lines of about 18 characters; subline: at most 2 lines of about 42 characters;
- one equation per scene in `Scene.eq` (mathtext), at most about 45 rendered characters, numbers filled in with f-strings from the module;
- `end_teaser` names the next episode from `episodes.csv`;
- `note` says where the numbers come from and how much motion is slowed, if any.

Draw only inside `kit.content_axes(...)` (the CONTENT region) and `kit.extra_axes()`. The kit adds the header, equation strip, watermarks and end card itself.

## 4. Originality gate (must pass before rendering)

The picture must be a **new visual metaphor for this topic** in the house style. Confirm every line:

- [ ] Paper background, navy ink, coral moving object, Inter type, from `reel_kit` colours. No dark or black backgrounds.
- [ ] One concrete metaphor a viewer can name in three words (ball in a valley, atoms on a spring, water level, a ladder, a gate, a slope).
- [ ] No glowing particle clouds, neon sparkle, spaced-out monospace capital labels, italic serif headlines, or small grey disclaimer blocks in monospace. These are the look of other science pages.
- [ ] Headline and subline wording is your own. Do not search for, watch, download or describe other creators' videos on this topic.
- [ ] The corner credit, centre watermark and end card come from the kit unchanged.

## 5. Check, render, record

1. `python make_reel_epNN.py --stills <middle of each scene> <end card time>` and view **one** contact sheet of the stills. Fix overlaps, text running off the frame and unreadable equations. Repeat only for the frames you changed.
2. Render the full video once: `python make_reel_epNN.py`. Confirm with `ffprobe` that it is 1080×1920, 30 fps, 25–30 s, with the copyright tag.
3. Copy `output/<slug>.mp4` to `videos/<slug>.mp4` (the `output/` folder is not committed).
4. Run `python .claude/skills/new-tutorial/scripts/check_notebook.py --execute notebooks/bonds_to_devices/NN_*.ipynb` from the repository root. Every line must be OK or an accepted WARN.
5. Set the episode to `built` in `episodes.csv`. Add a section to `notebooks/bonds_to_devices/README.md` with a timed voice-over table and a copy-ready post caption, in the same format as Episode 1's.
6. Commit with a clear message and push to the branch this session was given. Never push to `main`; do not open a pull request.
7. Create one Google Doc in the Drive folder titled `Episode NN – ready to post`, with the caption, voice-over, the video path in the repository and any open questions. Use `create_file` with `textContent` and `contentMimeType: text/plain`.

## 6. Report

End with a short report: episodes built, the files, the numbers you checked and their sources, the checker result, the Drive doc link, and anything that needs the owner's decision. If a gate failed and you could not fix it, say which and stop rather than publish a weak episode.

## Keep each run light

- Read the top docstring of `reel_kit.py` and the example episode once; do not read them again.
- One stills contact sheet per round, at most three rounds. Render the full MP4 once, at the end.
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
| Rebuilding an episode that already exists | `episodes.csv` decides what is built, not the Drive sheet's Status |
