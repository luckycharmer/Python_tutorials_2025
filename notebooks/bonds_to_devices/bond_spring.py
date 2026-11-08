"""The chemical bond as a spring: H2 and D2 vibrations and their Raman shift.

Shared by the Episode 2 notebook and the reel renderer, so the numbers in
the class notebook and in the video always come from the same code.

Wavenumbers are in cm^-1, wavelengths in nm, energies in eV and masses in
atomic mass units unless the variable name says otherwise.

Sources for the constants (see the notebook's References section):
- measured fundamental vibration (v = 0 -> 1, J = 0, the Raman Q(0) line) of
  H2, HD and D2: Dickenson et al. (2013), Phys. Rev. Lett. 110, 193601;
- spectroscopic constants omega_e, omega_e x_e, omega_e y_e, omega_e z_e:
  Huber & Herzberg (1979), via the NIST Chemistry WebBook (SRD 69) entries
  for H2 and D2, ground state X 1Sigma_g+;
- atomic masses: CODATA 2018 / AME2020;
- physical constants: CODATA 2018.
"""

import numpy as np

# Physical constants (CODATA 2018, exact or recommended values)
C_CM_PER_S = 2.99792458e10          # speed of light in cm/s
H_EV_S = 4.135667696e-15            # Planck constant in eV s
HC_EV_NM = 1239.841984              # h*c in eV nm
EV_PER_CM1 = 1.239841984e-4         # 1 cm^-1 expressed in eV
AMU_KG = 1.66053906660e-27          # atomic mass unit in kg
K_B_EV_PER_K = 8.617333262e-5       # Boltzmann constant in eV/K

# Atomic masses (CODATA 2018 / AME2020)
MASS_H_AMU = 1.00782503223          # hydrogen-1 atom
MASS_D_AMU = 2.01410177812          # deuterium (hydrogen-2) atom

# H2 ground-state constants (Huber & Herzberg 1979, via NIST WebBook)
OMEGA_E_H2_CM1 = 4401.213
OMEGA_E_XE_H2_CM1 = 121.336
OMEGA_E_YE_H2_CM1 = 0.8129

# D2 ground-state constants (Huber & Herzberg 1979, via NIST WebBook)
OMEGA_E_D2_CM1 = 3115.50
OMEGA_E_XE_D2_CM1 = 61.82
OMEGA_E_YE_D2_CM1 = 0.562
OMEGA_E_ZE_D2_CM1 = -0.02286

# Measured fundamental vibrations, v = 0 -> 1 (Dickenson et al. 2013)
FUNDAMENTAL_H2_CM1 = 4161.16632     # +/- 0.00018
FUNDAMENTAL_HD_CM1 = 3632.16054     # +/- 0.00024
FUNDAMENTAL_D2_CM1 = 2993.61713     # +/- 0.00017

# A common Raman laser: frequency-doubled Nd:YAG, nominal wavelength
LASER_NM = 532.0


def reduced_mass_amu(m1_amu, m2_amu):
    """Reduced mass of two atoms: the single mass that moves on the spring."""
    return m1_amu * m2_amu / (m1_amu + m2_amu)


MU_H2_AMU = reduced_mass_amu(MASS_H_AMU, MASS_H_AMU)
MU_HD_AMU = reduced_mass_amu(MASS_H_AMU, MASS_D_AMU)
MU_D2_AMU = reduced_mass_amu(MASS_D_AMU, MASS_D_AMU)


def frequency_Hz(wavenumber_cm1):
    """Vibration frequency (swings per second) for a wavenumber in cm^-1."""
    return np.asarray(wavenumber_cm1, dtype=float) * C_CM_PER_S


def period_fs(wavenumber_cm1):
    """Time for one swing, in femtoseconds."""
    return 1e15 / frequency_Hz(wavenumber_cm1)


def force_constant_N_per_m(omega_e_cm1, mu_amu):
    """Spring stiffness k = mu * (2 pi c omega_e)^2, in N/m (harmonic model)."""
    angular_per_s = 2 * np.pi * frequency_Hz(omega_e_cm1)
    return mu_amu * AMU_KG * angular_per_s**2


def harmonic_wavenumber_cm1(k_N_per_m, mu_amu):
    """Wavenumber of a spring with stiffness k and mass mu: (1/2 pi c) sqrt(k/mu)."""
    angular_per_s = np.sqrt(k_N_per_m / (np.asarray(mu_amu, dtype=float) * AMU_KG))
    return angular_per_s / (2 * np.pi * C_CM_PER_S)


def fundamental_from_constants_cm1(omega_e, omega_e_xe, omega_e_ye=0.0, omega_e_ze=0.0):
    """Spacing G(1) - G(0) from the Dunham-type expansion of the levels.

    G(v) = we(v+1/2) - wexe(v+1/2)^2 + weye(v+1/2)^3 + weze(v+1/2)^4, so
    G(1) - G(0) = we - 2 wexe + (13/4) weye + 5 weze.
    """
    return omega_e - 2 * omega_e_xe + 3.25 * omega_e_ye + 5 * omega_e_ze


def isotope_fundamental_cm1(mu_amu):
    """Predict an isotopologue's fundamental from the H2 constants alone.

    Same electrons, same energy curve, only the mass changes. With
    rho = sqrt(mu_H2 / mu): omega_e scales as rho, omega_e x_e as rho^2 and
    omega_e y_e as rho^3.
    """
    rho = np.sqrt(MU_H2_AMU / np.asarray(mu_amu, dtype=float))
    return fundamental_from_constants_cm1(OMEGA_E_H2_CM1 * rho,
                                          OMEGA_E_XE_H2_CM1 * rho**2,
                                          OMEGA_E_YE_H2_CM1 * rho**3)


def photon_energy_eV(wavelength_nm):
    """Energy of one photon of the given wavelength."""
    return HC_EV_NM / np.asarray(wavelength_nm, dtype=float)


def stokes_wavelength_nm(laser_nm, shift_cm1):
    """Wavelength of light that has given one vibration quantum to the molecule.

    1/lambda_out = 1/lambda_in - shift (all in cm^-1). Vacuum wavelengths.
    """
    laser_cm1 = 1e7 / np.asarray(laser_nm, dtype=float)
    return 1e7 / (laser_cm1 - np.asarray(shift_cm1, dtype=float))


def anti_stokes_to_stokes_boltzmann(shift_cm1, temperature_K):
    """Fraction of molecules already in v = 1 relative to v = 0 (Boltzmann factor).

    Sets roughly how much weaker the anti-Stokes (blue-shifted) line is.
    """
    return np.exp(-np.asarray(shift_cm1) * EV_PER_CM1 / (K_B_EV_PER_K * temperature_K))
