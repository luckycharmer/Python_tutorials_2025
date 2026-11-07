# Design: Quantum Computing with Python track

Date: 2026-11-07
Status: draft, awaiting approval

## Intent

A separate tutorial track that teaches physics students how quantum computation works, using Python. Students should finish the track able to describe a qubit as a physical two-level system, simulate small circuits from first principles, use Qiskit with confidence, and check any library result against an independent calculation.

The track exists because the repository's main path (Modules 00 to 08) covers data analysis for experimental physics and materials science, and quantum computing does not fit inside it. The same scientific standards apply.

## Audience

- Physics students in mixed classes. Some will have finished a standard quantum mechanics course (spin, operators, Born rule); others will not.
- The main track assumes post-QM knowledge. An optional refresher notebook (Q00) brings the others up to speed.
- Programming background: comfortable with the core notebooks of this repository (NumPy arrays, Matplotlib, simple fitting).

## Goals

- Physics first: introduce qubits through spin-1/2 and photon polarisation before abstract circuit language.
- Students build a small statevector simulator in NumPy, then move to Qiskit and confirm it reproduces their own results.
- Every notebook contains at least one quantitative check against an exact or analytic result.
- Every result is labelled as simulated, or, in the optional hardware notebook, measured.
- Link back to skills from the core track where natural (for example, fitting a decay curve with SciPy in the noise notebook).

## Non-goals

- Quantum chemistry packages (qiskit-nature, PySCF) or other large stacks.
- Quantum machine learning.
- Full quantum error correction. A three-qubit bit-flip code may appear as an extension exercise only.
- Covering every Qiskit feature.

## Anti-goals (would count as failure even if the code runs)

- Library output presented without an independent check.
- Claims of quantum advantage or speed-up that the small examples cannot support.
- Simulated data described or implied to be measured on hardware.
- Any notebook other than the optional hardware notebook that needs an account, an API token, or an internet connection to run.

## Constraints

- Follows `CONTRIBUTING.md` and the release criteria in `ROADMAP.md`: clean-environment run, data provenance, assumptions and units stated, calculation kept separate from interpretation, at least one validation, attribution for reused material.
- Uses the notebook structure from `CONTRIBUTING.md`: title and context, learning objectives, imports and environment check, data source, analysis, validation, interpretation, exercise, references.
- The core `requirements.txt` stays unchanged. Quantum dependencies live in a separate `requirements-quantum.txt`.
- Random sampling uses a fixed seed (`np.random.default_rng(seed)`) so outputs are reproducible.
- Each notebook should take a student roughly 45 to 60 minutes.
- Must run on an ordinary laptop: no notebook needs more than a few qubits (state vectors stay tiny).

## Approaches considered

1. **NumPy first, then Qiskit (chosen).** Students build the simulator themselves, then switch to Qiskit and verify it matches. Nothing is a black box, every Qiskit result has a built-in check, and the heavy dependency is confined to later notebooks. Cost: two or three notebooks go into the simulator before reaching the standard tools.
2. **Qiskit from the start.** Fastest route to algorithms and IBM cloud hardware, but students learn the library before the physics, and Qiskit's API has broken several times (1.0 in 2024, 2.0 in 2025), raising maintenance load.
3. **NumPy only.** Most transparent and no new dependencies, but no hardware access, no industry tooling, and a lot of hand-written code for noise and VQE that students would not reuse.

Dr Junaid Ali chose approach 1.

## Notebook sequence

Folder: `notebooks/quantum/` with its own `README.md`.

| No. | Title | Core content | Required check |
|---|---|---|---|
| Q00 (optional) | Complex vectors and Dirac notation | Complex numbers in NumPy, kets as arrays, inner products, normalisation, Born rule, expectation values | Normalisation equals 1; probabilities sum to 1 |
| Q01 | One qubit as a physical system | Spin-1/2 and polarisation as two-level systems, Bloch sphere (Matplotlib), measurement as sampling, shot noise | Sampled frequencies agree with Born-rule probabilities within binomial error bars |
| Q02 | Single-qubit gates | Pauli, Hadamard, phase and rotation gates as matrices; polarisation optics analogy (wave plates); Rabi-style rotation | Each gate is unitary (U†U = I); known identities such as HZH = X |
| Q03 | Two qubits and entanglement | Tensor products, CNOT, Bell states, reduced density matrix via partial trace, CHSH value | Classical CHSH bound 2 versus quantum value 2√2; partial trace of a Bell state gives I/2 |
| Q04 | Build a mini simulator | A small statevector simulator (apply gate to chosen qubit, measure, sample shots), unit-style tests, teleportation as the test case | Teleported state matches input state (fidelity = 1 within floating-point tolerance) |
| Q05 | Bridge to Qiskit | Rebuild Q02 to Q04 circuits in Qiskit; `Statevector`; sampling with Qiskit primitives; qubit-ordering convention | `np.allclose` between Qiskit and the student simulator for every circuit, after accounting for Qiskit's little-endian qubit order |
| Q06 | First algorithms | Deutsch-Jozsa and Grover search on two or three qubits | Grover success probability matches the analytic sin²((2k+1)θ) curve |
| Q07 | Noise and decoherence | Density matrices, amplitude and phase damping channels in NumPy, Ramsey-style decay curve, fitting T2 with SciPy, comparison with a Qiskit Aer noise model | Fitted decay time recovers the value used in the simulation within its uncertainty; NumPy and Aer results agree |
| Q08 | Variational quantum eigensolver | Two-qubit H2 Hamiltonian from published Pauli coefficients, simple ansatz, SciPy optimiser, energy versus bond length | VQE energy matches exact diagonalisation (`numpy.linalg.eigh`) at each bond length |
| Q09 (optional) | Running on real hardware | Bell or CHSH circuit on IBM Quantum through `qiskit-ibm-runtime`, comparison with the noiseless and noisy simulations | Measured CHSH value compared to the classical bound, with stated statistical uncertainty |

Q09 must also run offline: it ships with a saved, clearly labelled set of measured results (with date, backend name and shot count recorded) so the analysis cells work without an account.

## Dependencies

`requirements-quantum.txt`, installed on top of `requirements.txt`:

- `qiskit` (2.x, upper-bounded below 3)
- `qiskit-aer` (version compatible with the chosen Qiskit release)
- `qiskit-ibm-runtime` (only needed for Q09; marked optional in a comment)

Q00 to Q04 need only the core requirements. Exact version bounds are pinned at build time after a clean-environment run.

## Release order

1. Milestone A: track README, Q00 to Q05, `requirements-quantum.txt`. This is usable on its own as a short course.
2. Milestone B: Q06 to Q08.
3. Milestone C: Q09 with saved hardware data.

## Repository changes outside the track folder

- `README.md`: add a short "Quantum computing track" section linking to `notebooks/quantum/README.md`.
- `ROADMAP.md`: add the track as a separate phase with the three milestones above.

## Decided by Dr Junaid Ali

- Audience: physics students.
- A separate track, not part of Modules 00 to 08.
- Mixed classes: optional refresher, main track at post-QM level.
- Approach: NumPy first, then Qiskit.

## Calls made in this design (open to correction)

- Folder name `notebooks/quantum/` and notebook numbering Q00 to Q09.
- Physics-first framing through spin and polarisation, linked to optoelectronics.
- Separate `requirements-quantum.txt` so the core track stays light.
- Hardware notebook is optional and runs offline from saved data.
- H2 Hamiltonian coefficients taken from a cited published source rather than generated with a chemistry package.

## Left to the builder

- Exact wording, figure styling and exercise design within each notebook.
- Internal API of the student simulator in Q04, provided it stays short enough to read in one sitting (roughly 50 to 80 lines).
- Exact dependency pins, chosen after a verified clean install.
- Choice of ansatz and optimiser in Q08, provided the result is checked against exact diagonalisation.

## Settled during review (builder's calls, open to correction)

- **Self-contained track.** Only Tutorial 01 exists in the core path, so the quantum notebooks do not depend on unwritten core modules. Q07 teaches `scipy.optimize.curve_fit` with parameter uncertainty itself, and links to Module 04 only once that module exists.
- **Worked notebooks, like Tutorial 01.** Each notebook is fully worked, with exercises at the end. Worked solutions to the exercises are released separately, as ROADMAP.md says.
- **Shared simulator module.** Q04 builds the simulator step by step in the notebook, and the finished code is also saved as `notebooks/quantum/qsim.py`. Q05 to Q08 import it, so they pass a clean-environment run without depending on student code.
- **Time limit.** If a notebook runs well past 60 minutes, it is split rather than trimmed, so no required check is lost. Q03, Q07 and Q08 are the likely candidates. Numbering is finalised before each milestone is released.
- **Review gates.** Each milestone is submitted as its own pull request, and Dr Junaid Ali reviews it for scientific and typographical errors before merge. Approving this document approves the "calls made" listed above.
