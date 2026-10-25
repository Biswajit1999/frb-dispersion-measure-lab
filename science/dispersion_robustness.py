"""Conditional FRB dispersion and foreground sensitivity diagnostics.

All frequencies are in MHz, dispersion measures in pc cm^-3, and times in s
unless the function name explicitly says ``_ms``. No telescope data are
fabricated here; these are independent physical calculations.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

# Standard cold-plasma group-delay coefficient for MHz and pc cm^-3 (seconds).
K_DM_S_MHZ2 = 4.148808e3


def _positive(name: str, values: object) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(arr)) or np.any(arr <= 0):
        raise ValueError(f"{name} must be finite and strictly positive")
    return arr


def _nonnegative(name: str, values: object) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(arr)) or np.any(arr < 0):
        raise ValueError(f"{name} must be finite and nonnegative")
    return arr


def cold_plasma_delay_s(dm: float, frequency_mhz: object, reference_mhz: float = 800.0) -> np.ndarray:
    """Relative group delay K*DM*(nu^-2 - nu_ref^-2), signed above nu_ref."""
    dm = _nonnegative("dm", dm)
    nu = _positive("frequency_mhz", frequency_mhz)
    ref = float(_positive("reference_mhz", reference_mhz))
    return K_DM_S_MHZ2 * dm * (nu**-2 - ref**-2)


def dispersion_delay_sigma_s(
    dm: float,
    dm_sigma: float,
    frequency_mhz: object,
    reference_mhz: float = 800.0,
    frequency_sigma_mhz: object = 0.0,
    reference_sigma_mhz: float = 0.0,
) -> np.ndarray:
    """First-order independent-error propagation (not a calibration covariance).

    Treat DM, each channel frequency, and the reference frequency as
    independent. This is inappropriate if the channel and reference share a
    common oscillator error; supply a full covariance model in that case.
    """
    dm = float(_nonnegative("dm", dm))
    sd = float(_nonnegative("dm_sigma", dm_sigma))
    nu = _positive("frequency_mhz", frequency_mhz)
    ref = float(_positive("reference_mhz", reference_mhz))
    snu = _nonnegative("frequency_sigma_mhz", frequency_sigma_mhz)
    sr = float(_nonnegative("reference_sigma_mhz", reference_sigma_mhz))
    d_dm = K_DM_S_MHZ2 * (nu**-2 - ref**-2)
    d_nu = -2 * K_DM_S_MHZ2 * dm / nu**3
    d_ref = 2 * K_DM_S_MHZ2 * dm / ref**3
    return np.sqrt((d_dm * sd)**2 + (d_nu * snu)**2 + (d_ref * sr)**2)


def intrachannel_smearing_ms(dm: float, center_mhz: object, width_mhz: object) -> np.ndarray:
    """Exact cold-plasma delay across a rectangular frequency channel.

    This is the uncorrected intra-channel dispersive smearing; for coherent
    dedispersion of an imperfect trial DM, pass the absolute DM mismatch.
    """
    dm = float(_nonnegative("dm", dm))
    center = _positive("center_mhz", center_mhz)
    width = _positive("width_mhz", width_mhz)
    if np.any(np.broadcast_arrays(center, width)[0] <= np.broadcast_arrays(center, width)[1] / 2):
        raise ValueError("channel width must be smaller than twice its centre frequency")
    return 1e3 * K_DM_S_MHZ2 * dm * ((center - width/2)**-2 - (center + width/2)**-2)


@dataclass(frozen=True)
class ForegroundBudget:
    """Observer-frame DM remainder under explicitly assumed intervals."""
    raw_host_min: float
    raw_host_max: float
    feasible_host_interval: tuple[float, float] | None
    physical_overlap: bool


def conditional_host_dm_interval(
    observed_dm: float,
    disk_dm: float,
    halo_dm_bounds: tuple[float, float],
    igm_dm_bounds: tuple[float, float],
) -> ForegroundBudget:
    """Calculate *conditional* observer-frame host DM, not a host measurement.

    DM_obs = DM_disk + DM_halo + DM_IGM + DM_host_obs.
    A source-frame host DM would be (1+z)*DM_host_obs, requiring an
    independently measured redshift. Halo/IGM bounds are user assumptions.
    """
    obs = float(_nonnegative("observed_dm", observed_dm))
    disk = float(_nonnegative("disk_dm", disk_dm))
    halo = np.asarray(halo_dm_bounds, dtype=float)
    igm = np.asarray(igm_dm_bounds, dtype=float)
    for name, b in (("halo", halo), ("igm", igm)):
        if b.shape != (2,) or not np.all(np.isfinite(b)) or b[0] < 0 or b[1] < b[0]:
            raise ValueError(f"{name} bounds must be ordered nonnegative pairs")
    lo = float(obs - disk - halo[1] - igm[1])
    hi = float(obs - disk - halo[0] - igm[0])
    valid = hi >= 0
    return ForegroundBudget(lo, hi, (max(0.0, lo), hi) if valid else None, valid)
