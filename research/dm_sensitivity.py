"""Independent cold-plasma and foreground-model sensitivity checks.

The CHIME DM is measured; the halo range and mean IGM scaling are illustrative.
No unique host or intergalactic dispersion measure is inferred.
"""
from __future__ import annotations

from math import sqrt

K_DM_S_MHZ2 = 4.148808e3  # seconds MHz^2 / (pc cm^-3)


def delay_seconds(dm: float, low_mhz: float, high_mhz: float) -> float:
    """Positive low-frequency arrival delay relative to the higher frequency."""
    if dm < 0 or not 0 < low_mhz < high_mhz:
        raise ValueError("require nonnegative DM and 0 < low_mhz < high_mhz")
    return K_DM_S_MHZ2 * dm * (low_mhz**-2 - high_mhz**-2)


def delay_error_budget(
    dm: float,
    sigma_dm: float,
    low_mhz: float,
    high_mhz: float,
    sigma_edge_mhz: float = 0.0,
) -> dict[str, float]:
    """1-sigma terms for independent edge errors or a common edge shift.

    The common-shift and independent-edge alternatives must NOT be summed:
    they describe different frequency-calibration error models.
    """
    if sigma_dm < 0 or sigma_edge_mhz < 0:
        raise ValueError("uncertainties must be nonnegative")
    delay = delay_seconds(dm, low_mhz, high_mhz)
    d_dm = K_DM_S_MHZ2 * (low_mhz**-2 - high_mhz**-2)
    d_low = -2 * K_DM_S_MHZ2 * dm / low_mhz**3
    d_high = 2 * K_DM_S_MHZ2 * dm / high_mhz**3
    return {
        "delay_s": delay,
        "dm_sigma_s": abs(d_dm) * sigma_dm,
        "independent_edges_sigma_s": sqrt(d_low**2 + d_high**2) * sigma_edge_mhz,
        "common_shift_sigma_s": abs(d_low + d_high) * sigma_edge_mhz,
    }


def dm_delay_covariance(sigma_dm: float, bands_mhz: list[tuple[float, float]]) -> list[list[float]]:
    """Rank-one covariance from a single shared fitted DM (not independent bands)."""
    if sigma_dm < 0:
        raise ValueError("sigma_dm must be nonnegative")
    gradients = [delay_seconds(1.0, lo, hi) for lo, hi in bands_mhz]
    return [[sigma_dm**2 * a * b for b in gradients] for a in gradients]


def residual_budget(
    observed_dm: float,
    galactic_disk_dm: float,
    halo_range: tuple[float, float],
    redshift: float,
    igm_mean_coefficient: float = 900.0,
) -> dict[str, float | bool]:
    """Algebraic leftover after *assumed* halo and mean-IGM terms.

    Negative leftover means this toy decomposition is inconsistent with
    a nonnegative host term, not that a physical host DM is negative.
    """
    halo_lo, halo_hi = halo_range
    if not (0 <= galactic_disk_dm <= observed_dm and 0 <= halo_lo <= halo_hi
            and redshift >= 0 and igm_mean_coefficient >= 0):
        raise ValueError("invalid foreground-budget inputs")
    excess = observed_dm - galactic_disk_dm
    igm_proxy = igm_mean_coefficient * redshift
    low = excess - halo_hi - igm_proxy
    high = excess - halo_lo - igm_proxy
    return {
        "disk_subtracted_dm": excess,
        "illustrative_igm_mean_dm": igm_proxy,
        "leftover_min_dm": low,
        "leftover_max_dm": high,
        "nonnegative_host_compatible": high >= 0,
    }
