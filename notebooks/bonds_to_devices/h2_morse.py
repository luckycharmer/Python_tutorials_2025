"""Hydrogen molecule (H2) energy curve: constants and a Morse model.

Shared by the Episode 1 notebook and the reel renderer, so the numbers
in the class notebook and in the video always come from the same code.

All energies are in eV and all distances in picometres (pm) unless the
variable name says otherwise.

Sources for the constants (see the notebook's References section):
- equilibrium bond length and vibrational constants: Huber & Herzberg (1979),
  via the NIST Chemistry WebBook entry for H2, ground state X 1Sigma_g+;
- dissociation energy D0: Liu et al. (2009), J. Chem. Phys. 130, 174306;
- well depth De: Kolos & Wolniewicz (1968), J. Chem. Phys. 49, 404.
"""

import numpy as np

# Physical constants (CODATA 2018, exact or recommended values)
C_CM_PER_S = 2.99792458e10          # speed of light in cm/s
H_EV_S = 4.135667696e-15            # Planck constant in eV s
K_B_EV_PER_K = 8.617333262e-5       # Boltzmann constant in eV/K
EV_PER_CM1 = 1.239841984e-4         # 1 cm^-1 expressed in eV
KJ_PER_MOL_PER_EV = 96.48533212     # 1 eV per molecule in kJ/mol
AMU_KG = 1.66053906660e-27          # atomic mass unit in kg
EV_J = 1.602176634e-19              # 1 eV in joules
BOHR_PM = 52.917721090              # Bohr radius in pm

# H2 ground-state data
MASS_H_AMU = 1.00782503207          # mass of a hydrogen-1 atom
REDUCED_MASS_AMU = MASS_H_AMU / 2   # two equal masses
BOND_LENGTH_PM = 74.144             # r_e, bottom of the energy well
OMEGA_E_CM1 = 4401.21               # harmonic vibrational constant
OMEGA_E_XE_CM1 = 121.34             # measured anharmonicity constant
D0_MEASURED_CM1 = 36118.0696        # energy to break the bond from the lowest level
WELL_DEPTH_EV = 4.7483              # D_e, depth of the well below two free atoms

D0_MEASURED_EV = D0_MEASURED_CM1 * EV_PER_CM1


def vibration_frequency_Hz():
    """Vibration frequency of H2 from the harmonic constant."""
    return OMEGA_E_CM1 * C_CM_PER_S


def morse_width_per_pm():
    """Morse width parameter a, chosen so the curve has H2's measured stiffness.

    a = 2*pi*c*omega_e * sqrt(mu / (2 De)), converted to 1/pm.
    """
    mu_kg = REDUCED_MASS_AMU * AMU_KG
    angular_frequency_per_s = 2 * np.pi * vibration_frequency_Hz()
    depth_J = WELL_DEPTH_EV * EV_J
    a_per_m = angular_frequency_per_s * np.sqrt(mu_kg / (2 * depth_J))
    return a_per_m * 1e-12


def morse_energy_eV(distance_pm):
    """Energy of the pair at a given nucleus-to-nucleus distance.

    Zero means two separate hydrogen atoms at rest; negative means bonded.
    """
    a = morse_width_per_pm()
    x = np.exp(-a * (np.asarray(distance_pm, dtype=float) - BOND_LENGTH_PM))
    return WELL_DEPTH_EV * ((1 - x) ** 2 - 1)


def morse_level_eV(v):
    """Energy of vibrational level v in the Morse model (measured from the free atoms)."""
    quantum_eV = H_EV_S * vibration_frequency_Hz()
    n = np.asarray(v, dtype=float) + 0.5
    return -WELL_DEPTH_EV + quantum_eV * n - (quantum_eV * n) ** 2 / (4 * WELL_DEPTH_EV)


def morse_level_count():
    """Number of bound vibrational levels the Morse model allows."""
    quantum_eV = H_EV_S * vibration_frequency_Hz()
    return int(np.floor(2 * WELL_DEPTH_EV / quantum_eV - 0.5)) + 1


def turning_points_pm(energy_eV):
    """Inner and outer distances where the curve reaches a given (negative) energy."""
    a = morse_width_per_pm()
    root = np.sqrt(1 + energy_eV / WELL_DEPTH_EV)
    inner = BOND_LENGTH_PM - np.log(1 + root) / a
    outer = BOND_LENGTH_PM - np.log(1 - root) / a
    return inner, outer


def bonding_density(x_pm, y_pm, distance_pm):
    """Electron density of the simple bonding orbital (1s + 1s), in arbitrary units.

    Picture only: this textbook model gets the shape right but not the numbers.
    The energies above come from the Morse curve, not from this function.
    """
    half = distance_pm / 2
    r_a = np.hypot(x_pm + half, y_pm)
    r_b = np.hypot(x_pm - half, y_pm)
    psi = np.exp(-r_a / BOHR_PM) + np.exp(-r_b / BOHR_PM)
    return psi**2
