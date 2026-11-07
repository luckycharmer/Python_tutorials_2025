# Quantum Computing Track, Milestone A: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the first usable part of the quantum track: track README, notebooks Q00 to Q05, the shared `qsim.py` simulator with tests, and `requirements-quantum.txt`.

**Architecture:** Q00 to Q03 use plain NumPy inside each notebook. Q04 builds a small statevector simulator step by step, and the finished code lives in `notebooks/quantum/qsim.py` (tested with pytest). Q05 rebuilds the same circuits in Qiskit and asserts agreement with `qsim`. Every required check in the spec is an `assert` cell, so a failed check stops notebook execution.

**Tech Stack:** Python 3.11+, NumPy 2, Matplotlib, JupyterLab, pytest, Qiskit 2.x (Q05 only).

**Spec:** `docs/superpowers/specs/2026-11-07-quantum-computing-track-design.md`

## Global Constraints

- Work on branch `ccr-2b74f294-9g2aix`. Do not open a pull request until Dr Junaid Ali confirms; the milestone goes to him for scientific review before merge.
- Core `requirements.txt` stays unchanged.
- Notebook structure, from `CONTRIBUTING.md`: title and context, learning objectives, imports and environment check, data source and units, analysis, validation, physical interpretation, exercise or extension, references.
- Every notebook states in its first cell that all results are **simulated** (no measured data in Milestone A).
- Randomness uses `rng = np.random.default_rng(SEED)` with `SEED = 2026`. No calls to legacy `np.random.*` functions.
- Notebooks are committed with outputs cleared, matching `notebooks/01_core/01_arrays_units_iv_plot.ipynb`. Kernel metadata: `{"display_name": "Python 3", "language": "python", "name": "python3"}`.
- Each notebook targets 45 to 60 minutes. If one runs well past that, split it (for example Q03a/Q03b) rather than drop a required check, and tell Dr Ali.
- Qubit order in `qsim`: qubit 0 is the **leftmost** (most significant) bit, the textbook convention. Qiskit uses the opposite order; Q05 teaches the conversion.
- No claims of quantum advantage. Use plain, concise student-facing English (British spelling, matching the existing notebook).
- Notebook verification command, used in every notebook task (run from repo root):
  `jupyter nbconvert --to notebook --execute --stdout <nb> > /dev/null && echo OK`, then
  `jupyter nbconvert --clear-output --inplace <nb>`.

## Review Focus

1. **Unnormalised state passed to `qsim`.** A student hand-types `[1, 1]`. Expect `measure_counts`, `measure_qubit` and `probabilities` to raise `ValueError` naming normalisation, not silently return wrong probabilities. Test in Task 1.
2. **Bad qubit indices.** Target out of range, negative, or repeated (e.g. CNOT on `(1, 1)`). Expect `ValueError`. Test in Task 1.
3. **Gate size does not match number of targets** (4x4 gate with one target). Expect `ValueError`. Test in Task 1.
4. **Qiskit bit order.** A student compares Qiskit and `qsim` amplitudes directly and sees a mismatch on asymmetric circuits. Q05 must show the mismatch on purpose, then the fix. Test in Task 7 (an asymmetric circuit, `X` on qubit 0 only, in the comparison set).
5. **Reproducibility.** Re-running a notebook gives identical counts. Test in Task 1 (`measure_counts` with the same seed twice returns equal dicts).

---

### Task 1: `qsim.py` simulator module with tests

**Files:**
- Create: `notebooks/quantum/qsim.py`
- Create: `tests/quantum/test_qsim.py`
- Create: `requirements-quantum.txt`

**Interfaces:**
- Produces (all in `qsim`; states are 1-D `complex128` arrays of length `2**n`; gates are `complex128` square arrays):
  - Constants: `I2, X, Y, Z, H, S, T` (2x2), `CNOT` (4x4, control is first target).
  - `rx(theta: float) -> np.ndarray`, `ry(theta: float) -> np.ndarray`, `rz(theta: float) -> np.ndarray` using the convention `R_a(θ) = exp(-iθσ_a/2)`.
  - `zero_state(n_qubits: int) -> np.ndarray`
  - `n_qubits(state: np.ndarray) -> int`
  - `apply_gate(state: np.ndarray, gate: np.ndarray, targets: Sequence[int]) -> np.ndarray` (returns a new array).
  - `probabilities(state: np.ndarray) -> np.ndarray`
  - `project(state: np.ndarray, qubit: int, outcome: int) -> np.ndarray` (normalised post-measurement state; `ValueError` if the outcome has zero probability).
  - `measure_qubit(state: np.ndarray, qubit: int, rng: np.random.Generator) -> tuple[int, np.ndarray]`
  - `measure_counts(state: np.ndarray, shots: int, rng: np.random.Generator) -> dict[str, int]` (keys are bitstrings with qubit 0 leftmost; only nonzero counts included).
  - `fidelity(psi: np.ndarray, phi: np.ndarray) -> float` returning `|<psi|phi>|**2`.
- `NORM_TOL = 1e-9` module constant for normalisation checks.

- [ ] **Step 1: Write `requirements-quantum.txt`**

Header comment: install on top of `requirements.txt`; Q00 to Q04 need only the core file. Lines for now: `pytest>=8,<9` (comment: runs `tests/quantum`). Qiskit is added in Task 7; `qiskit-aer` and `qiskit-ibm-runtime` are added in Milestones B and C.

- [ ] **Step 2: Write the failing tests** in `tests/quantum/test_qsim.py`

Add `notebooks/quantum` to `sys.path` at the top via `pathlib.Path(__file__).resolve().parents[2] / "notebooks" / "quantum"`. Tests and their assertions:

```python
def test_gates_are_unitary():          # for each of I2,X,Y,Z,H,S,T,CNOT, rx/ry/rz(0.7): U.conj().T @ U ≈ identity
def test_known_identities():           # H@Z@H ≈ X; H@X@H ≈ Z; S@S ≈ Z; T@T ≈ S; rx(np.pi) ≈ -1j*X
def test_zero_state():                 # zero_state(3) has length 8, [0]==1, rest 0, dtype complex128
def test_x_on_qubit0_is_leftmost():    # apply_gate(zero_state(2), X, [0]) ≈ |10> i.e. index 2 == 1
def test_bell_state():                 # H on 0 then CNOT [0,1] from |00> ≈ [1,0,0,1]/sqrt(2)
def test_cnot_reversed_targets():      # CNOT with targets [1,0] on |01> gives |11>
def test_probabilities_sum_to_one():   # random normalised 3-qubit state (rng seed 2026): sum == 1 within 1e-12
def test_project_and_measure_qubit():  # project(bell, 0, 1) ≈ |11>; measure_qubit on bell returns (m, state) with state ≈ |mm>
def test_measure_counts_statistics():  # state = ry(np.pi/4) @ |0> = cos(π/8)|0>+sin(π/8)|1>, shots=4000, seed 2026:
                                       # |counts["0"]/4000 - cos(π/8)**2| < 3*sqrt(p*(1-p)/4000); sum(counts.values()) == 4000
def test_measure_counts_reproducible():# same seed twice -> identical dicts
def test_fidelity():                   # fidelity(|0>,|0>) == 1; fidelity(|0>,|1>) == 0; global phase e^{i0.3} ignored
def test_rejects_unnormalised():       # probabilities, measure_counts, measure_qubit on np.array([1,1],complex) raise ValueError
def test_rejects_bad_targets():        # targets [2] on 2 qubits, [-1], CNOT on [1,1] -> ValueError
def test_rejects_gate_size_mismatch(): # CNOT with targets [0] -> ValueError
def test_project_zero_probability():   # project(zero_state(1), 0, 1) -> ValueError
```

- [ ] **Step 3: Run tests, expect failure**

Run: `python -m pytest tests/quantum -q`
Expected: collection error `ModuleNotFoundError: No module named 'qsim'`.

- [ ] **Step 4: Implement `notebooks/quantum/qsim.py`**

Module docstring states the qubit-order convention and that it is a teaching simulator for a few qubits. `apply_gate`: reshape the state to `(2,)*n`, reshape the gate to `(2,)*(2k)`, contract with `np.tensordot` over the target axes, then `np.moveaxis` the result axes back to the target positions, and flatten. Keep the whole module readable in one sitting (roughly 80 to 120 lines with docstrings).

- [ ] **Step 5: Run tests, expect pass**

Run: `python -m pytest tests/quantum -q`
Expected: all 15 tests pass.

- [ ] **Step 6: Commit**

```bash
git add notebooks/quantum/qsim.py tests/quantum/test_qsim.py requirements-quantum.txt
git commit -m "feat(quantum): add tested teaching statevector simulator"
```

### Task 2: Q00 — Complex vectors and Dirac notation (optional refresher)

**Files:** Create `notebooks/quantum/Q00_complex_vectors_dirac_notation.ipynb`

**Interfaces:** Consumes nothing from `qsim` (plain NumPy only).

Content: marked **optional** at the top for students who have completed a QM course. Complex numbers in NumPy; kets as column arrays; bra as conjugate transpose; inner product with `np.vdot`; normalisation; Born rule; Hermitian operators; expectation value ⟨Z⟩.

- [ ] **Step 1: Write the notebook** with these `assert` checks in its validation section:
  - a random complex vector from `rng` normalised to `np.isclose(np.vdot(psi, psi).real, 1.0)`;
  - Born-rule probabilities sum to 1 within `1e-12`;
  - for that state, `np.vdot(psi, Z @ psi).real` equals `p0 - p1` within `1e-12`;
  - `Z` and `X` are Hermitian (`np.allclose(M, M.conj().T)`).
- [ ] **Step 2: Run the verification command** — Expected: `OK`. Clear outputs.
- [ ] **Step 3: Commit** — `git commit -m "feat(quantum): add Q00 refresher on complex vectors and Dirac notation"`

### Task 3: Q01 — One qubit as a physical system

**Files:** Create `notebooks/quantum/Q01_one_qubit_physical_system.ipynb`

Content: spin-1/2 and photon polarisation as two-level systems (H/V polarisation ↔ |0⟩/|1⟩); Bloch-sphere angles θ, φ and a Matplotlib 3-D Bloch plot written in the notebook (no extra library); measurement as sampling with `rng.choice`; shot noise and the binomial standard error `sqrt(p(1-p)/N)`; plot of sampled frequency against N (N from 10 to 10 000) with ±3σ band.

- [ ] **Step 1: Write the notebook** with `assert` checks:
  - for |ψ⟩ = cos(π/8)|0⟩ + sin(π/8)|1⟩ and `N = 1000` shots, `abs(f0 - np.cos(np.pi/8)**2) < 3*np.sqrt(p*(1-p)/N)`;
  - Bloch vector of |ψ⟩ has length 1 within `1e-12`;
  - Malus's law link: P(0) for polarisation at angle α equals `np.cos(alpha)**2` for five angles.
- [ ] **Step 2: Run the verification command** — Expected: `OK`. Clear outputs.
- [ ] **Step 3: Commit** — `git commit -m "feat(quantum): add Q01 one qubit as a physical system"`

### Task 4: Q02 — Single-qubit gates

**Files:** Create `notebooks/quantum/Q02_single_qubit_gates.ipynb`

Content: Pauli, Hadamard, S, T and rotation gates as matrices (defined in the notebook, not imported); wave-plate analogy (half-wave plate ↔ X-like flip, quarter-wave plate ↔ phase gate); Rabi-style rotation: P(1) after `rx(θ)` from |0⟩ plotted against θ, overlaid with `np.sin(theta/2)**2`.

- [ ] **Step 1: Write the notebook** with `assert` checks: every gate unitary; `H@Z@H ≈ X`; `S@S ≈ Z`; `T@T ≈ S`; simulated Rabi curve equals `np.sin(theta/2)**2` within `1e-12` on 101 points in [0, 2π].
- [ ] **Step 2: Run the verification command** — Expected: `OK`. Clear outputs.
- [ ] **Step 3: Commit** — `git commit -m "feat(quantum): add Q02 single-qubit gates"`

### Task 5: Q03 — Two qubits and entanglement

**Files:** Create `notebooks/quantum/Q03_two_qubits_entanglement.ipynb`

Content: `np.kron` tensor products; CNOT; the four Bell states; density matrix `ρ = |ψ⟩⟨ψ|`; partial trace written in the notebook via reshape to `(2,2,2,2)` and `np.einsum`; CHSH with observables `A(θ) = cos θ Z + sin θ X`.

- [ ] **Step 1: Write the notebook** with `assert` checks:
  - partial trace of |Φ+⟩ over either qubit ≈ `np.eye(2)/2`; for the product state |0⟩|+⟩ it gives a pure state (`np.trace(rho_A @ rho_A) ≈ 1`);
  - classical bound: brute-force all 16 deterministic ±1 assignments to (a, a′, b, b′) and assert `max |S| == 2`;
  - quantum value with a = 0, a′ = π/2, b = π/4, b′ = −π/4 on |Φ+⟩: `np.isclose(S, 2*np.sqrt(2))`.
- [ ] **Step 2: Run the verification command** — Expected: `OK`. Clear outputs. Time a read-through; if well over 60 minutes, split CHSH into Q03b and note it for Dr Ali.
- [ ] **Step 3: Commit** — `git commit -m "feat(quantum): add Q03 two qubits and entanglement"`

### Task 6: Q04 — Build a mini simulator

**Files:** Create `notebooks/quantum/Q04_build_a_mini_simulator.ipynb`

**Interfaces:** Consumes the full `qsim` interface from Task 1.

Content: build `zero_state`, `apply_gate`, `probabilities`, `project` and `measure_counts` step by step in the notebook with the same signatures as `qsim`, explaining the reshape/tensordot idea with a 2-qubit picture. Then explain that the finished version lives in `qsim.py` and import it. Teleportation (3 qubits; qubit 0 holds the input, qubits 1 and 2 share |Φ+⟩) is the test case.

- [ ] **Step 1: Write the notebook** with `assert` checks:
  - the notebook-built functions agree with `qsim` (`np.allclose`) on the Bell circuit and on a seeded random 3-qubit circuit of 10 gates from `{H, X, rx(θ), CNOT}`;
  - teleportation: for 3 input states (|0⟩, |+⟩, and a seeded random state) and **all four** outcome pairs (m0, m1), after CNOT on targets [0, 1] and H on qubit 0, using `qsim.project` on qubits 0 and 1 then the corrections X^m1 then Z^m0 on qubit 2, the qubit-2 amplitudes (the state is a product state after projection) have fidelity with the input ≥ `1 - 1e-12`.
- [ ] **Step 2: Run the verification command** — Expected: `OK`. Clear outputs.
- [ ] **Step 3: Commit** — `git commit -m "feat(quantum): add Q04 build a mini simulator with teleportation"`

### Task 7: Q05 — Bridge to Qiskit

**Files:**
- Create: `notebooks/quantum/Q05_bridge_to_qiskit.ipynb`
- Modify: `requirements-quantum.txt` (add `qiskit>=2.0,<3`, then tighten the lower bound to the version verified in Step 2)

**Interfaces:** Consumes `qsim`. Uses `qiskit.QuantumCircuit`, `qiskit.quantum_info.Statevector` (`Statevector.from_instruction`, `.reverse_qargs()`, `.data`), `qiskit.primitives.StatevectorSampler(seed=SEED)`, and counts via `job.result()[0].data.meas.get_counts()` after `qc.measure_all()`.

Content: the same circuits built in Qiskit; a deliberate first comparison that fails on an asymmetric circuit, with an explanation of Qiskit's little-endian order (qubit 0 is the rightmost bit), then the fix with `.reverse_qargs()` and reversed count strings; environment cell prints the Qiskit version.

- [ ] **Step 1: Write the notebook** with `assert` checks:
  - for each circuit in {X on qubit 0 of 2 qubits, Bell, 3-qubit GHZ, seeded random 3-qubit circuit from Task 6's gate set}: `np.allclose(Statevector.from_instruction(qc).reverse_qargs().data, qsim_state)`;
  - the raw (un-reversed) comparison for "X on qubit 0" is **not** close (shows the pitfall on purpose);
  - sampled GHZ counts with 4000 shots: each of `"000"` and `"111"` within 3σ of 0.5, and no other bitstrings.
- [ ] **Step 2: Install and verify in a clean virtual environment**

```bash
python -m venv /tmp/qenv && . /tmp/qenv/bin/activate
pip install -r requirements.txt -r requirements-quantum.txt
python -c "import qiskit; print(qiskit.__version__)"
```
Expected: a 2.x version prints. Set the lower bound in `requirements-quantum.txt` to that minor version (e.g. `qiskit>=2.6,<3`).
- [ ] **Step 3: Run the verification command inside that environment** — Expected: `OK`. Clear outputs.
- [ ] **Step 4: Commit** — `git commit -m "feat(quantum): add Q05 bridge to Qiskit"`

### Task 8: Track README, root README and ROADMAP

**Files:**
- Create: `notebooks/quantum/README.md`
- Modify: `README.md` (new section "Quantum computing track" after "Planned learning path")
- Modify: `ROADMAP.md` (new section "Quantum computing track" before "Release criteria")

- [ ] **Step 1: Write `notebooks/quantum/README.md`**: who it is for (physics students; Q00 optional for those without a QM course); install commands (`pip install -r requirements.txt -r requirements-quantum.txt`); the notebook table for Q00 to Q05 linked, with Q06 to Q09 listed as planned; the qubit-order note; how to run `python -m pytest tests/quantum`.
- [ ] **Step 2: Update `README.md`** with a 3 to 5 line section linking to the track README.
- [ ] **Step 3: Update `ROADMAP.md`** with the three milestones from the spec (A: Q00–Q05; B: Q06–Q08 with `qiskit-aer`; C: Q09 with hardware data run by Dr Ali's lab).
- [ ] **Step 4: Check every relative link resolves**

Run: `grep -oE '\]\([^)#]+' README.md ROADMAP.md notebooks/quantum/README.md` and confirm each path exists with `ls`.
Expected: no missing paths.
- [ ] **Step 5: Commit** — `git commit -m "docs: add quantum computing track to README and roadmap"`

### Task 9: Clean-environment release check

- [ ] **Step 1:** In a fresh venv with both requirement files, run `python -m pytest tests/quantum -q` — Expected: all pass.
- [ ] **Step 2:** Execute every notebook `notebooks/quantum/Q0*.ipynb` with the verification command in order — Expected: `OK` for each.
- [ ] **Step 3:** Confirm outputs are cleared and no personal paths or tokens are present.
  Run: `python -c "import json,glob; bad=[f for f in glob.glob('notebooks/quantum/*.ipynb') for c in json.load(open(f))['cells'] if c['cell_type']=='code' and (c['outputs'] or c['execution_count'])]; print(sorted(set(bad)) or 'clean')"` — Expected: `clean`.
  Run: `grep -rnI '/home/\|/Users/\|token' notebooks/quantum` — Expected: no matches.
- [ ] **Step 4:** `git push -u origin ccr-2b74f294-9g2aix`, then ask Dr Ali whether to open the Milestone A pull request for his review.
