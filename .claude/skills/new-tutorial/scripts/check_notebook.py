#!/usr/bin/env python3
"""Check a tutorial notebook against the repository's release criteria.

Usage:
    python .claude/skills/new-tutorial/scripts/check_notebook.py NOTEBOOK [NOTEBOOK ...] [--execute]

Uses only the standard library. --execute additionally runs the notebook
in a fresh kernel with `jupyter nbconvert` (installed via requirements.txt).
Exit code is 1 if any FAIL is reported, otherwise 0.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REQUIRED_HEADINGS = [
    ("title", re.compile(r"^#\s+Tutorial\s+\d+", re.M)),
    ("learning objectives", re.compile(r"^##\s+Learning objectives", re.M | re.I)),
    ("interpretation", re.compile(r"^##\s+.*Interpretation", re.M | re.I)),
    ("exercise", re.compile(r"^##\s+Exercises?\b", re.M | re.I)),
]
DATA_TYPE = re.compile(r"\b(synthetic|simulated|measured)\b", re.I)
UNIT_NAME = re.compile(
    r"\b[a-z][a-z0-9]*_(V|mV|A|mA|uA|nA|ohm|W|mW|nm|um|mm|cm|m|s|ms|us|K|C|Hz|eV|J|Pa)\b"
)
RANDOM_USE = re.compile(r"np\.random\.|default_rng|random\.")
SEEDED = re.compile(r"default_rng\(\s*\d+|np\.random\.seed\(\s*\d+|random\.seed\(\s*\d+")
PERSONAL_PATH = re.compile(r"(/home/\w+|/Users/\w+|[A-Za-z]:\\\\Users\\\\)")
SECRET = re.compile(r"(api[_-]?key|password|secret|token)\s*=\s*['\"]\w+", re.I)
VALIDATION = re.compile(r"residual|assert|np\.isclose|np\.allclose|uncertaint|pcov", re.I)


def source(cell):
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else s


def check(path, execute):
    results = []

    def report(level, msg):
        results.append((level, msg))

    try:
        nb = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report("FAIL", f"cannot read notebook: {exc}")
        return results

    cells = nb.get("cells", [])
    md = "\n\n".join(source(c) for c in cells if c.get("cell_type") == "markdown")
    code = "\n\n".join(source(c) for c in cells if c.get("cell_type") == "code")

    for name, pattern in REQUIRED_HEADINGS:
        if pattern.search(md):
            report("OK", f"section present: {name}")
        else:
            report("FAIL", f"missing section: {name}")

    if not re.search(r"^##\s+References", md, re.M | re.I):
        report("WARN", "no References section (needed if any method, data or code is borrowed)")

    first_md = next((source(c) for c in cells if c.get("cell_type") == "markdown"), "")
    if DATA_TYPE.search(first_md):
        report("OK", "data type (measured/simulated/synthetic) stated in the opening cell")
    else:
        report("FAIL", "opening cell does not say whether data is measured, simulated or synthetic")

    if re.search(r"__version__", code):
        report("OK", "environment/version check present")
    else:
        report("WARN", "no library version printout found")

    if UNIT_NAME.search(code):
        report("OK", "unit suffixes used in variable names")
    else:
        report("WARN", "no unit-suffixed names found (e.g. voltage_V, current_mA)")

    if VALIDATION.search(code):
        report("OK", "validation step found (residuals, assert, uncertainty, ...)")
    else:
        report("FAIL", "no validation or residual check found in code")

    if RANDOM_USE.search(code) and not SEEDED.search(code):
        report("FAIL", "random numbers used without a fixed seed")

    code_cells = [source(c) for c in cells if c.get("cell_type") == "code"]
    for i, src in enumerate(code_cells, 1):
        if re.search(r"\b(plt|ax\w*)\.(plot|scatter|errorbar|bar|hist)\(", src):
            if not ("set_xlabel" in src or "plt.xlabel" in src):
                report("WARN", f"code cell {i} draws a plot without an x-axis label")
            if not ("set_ylabel" in src or "plt.ylabel" in src):
                report("WARN", f"code cell {i} draws a plot without a y-axis label")

    raw = Path(path).read_text(encoding="utf-8")
    if PERSONAL_PATH.search(raw):
        report("FAIL", f"personal path found: {PERSONAL_PATH.search(raw).group(0)}")
    if SECRET.search(raw):
        report("FAIL", "possible credential in notebook")

    stored = sum(len(c.get("outputs", [])) for c in cells if c.get("cell_type") == "code")
    if stored:
        report("WARN", f"{stored} stored output(s); clear outputs before committing")

    if execute:
        jupyter = shutil.which("jupyter")
        if not jupyter:
            report("FAIL", "--execute requested but `jupyter` is not installed (pip install -r requirements.txt)")
        else:
            with tempfile.TemporaryDirectory() as tmp:
                proc = subprocess.run(
                    [jupyter, "nbconvert", "--to", "notebook", "--execute",
                     "--ExecutePreprocessor.timeout=300", "--output-dir", tmp, str(path)],
                    capture_output=True, text=True,
                )
            if proc.returncode == 0:
                report("OK", "executed top to bottom in a fresh kernel")
            else:
                clean = re.sub(r"\x1b\[[0-9;]*m", "", proc.stderr)
                lines = [ln for ln in clean.splitlines() if ln.strip() and not set(ln.strip()) <= {"-"}]
                # prefer the exception line(s) near the end, e.g. "ZeroDivisionError: division by zero"
                errs = [ln for ln in lines if re.match(r"^\w*(Error|Exception)\b.*:", ln.strip())]
                tail = "\n      ".join((errs[-2:] if errs else lines[-6:]))
                report("FAIL", f"execution failed:\n      {tail}")

    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notebooks", nargs="+")
    ap.add_argument("--execute", action="store_true", help="also run every cell in a fresh kernel")
    args = ap.parse_args()

    failed = False
    for nb in args.notebooks:
        print(f"\n{nb}")
        for level, msg in check(nb, args.execute):
            print(f"  {level:4s}  {msg}")
            failed |= level == "FAIL"
    print("\nResult:", "FAIL" if failed else "PASS")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
