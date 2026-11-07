"""Conditional FRB dispersion diagnostics; not a host/IGM decomposition."""
from __future__ import annotations
import math

K_DM_S_MHZ2 = 4.148808e3

def sweep_delay(dm: float, nu_low_mhz: float, nu_high_mhz: float) -> float:
    """Cold-plasma arrival-time difference in seconds for DM in pc cm^-3."""
    if not all(math.isfinite(x) for x in (dm, nu_low_mhz, nu_high_mhz)):
        raise ValueError('inputs must be finite')
    if dm < 0 or not (0 < nu_low_mhz < nu_high_mhz):
        raise ValueError('require DM >= 0 and 0 < low frequency < high frequency')
    return K_DM_S_MHZ2 * dm * (nu_low_mhz**-2 - nu_high_mhz**-2)

def delay_uncertainty(dm_sigma: float, nu_low_mhz: float, nu_high_mhz: float) -> float:
    """Propagate catalog DM standard error, holding frequencies exact."""
    return sweep_delay(dm_sigma, nu_low_mhz, nu_high_mhz)

def foreground_scenarios(observed_dm: float, disk_dm: tuple[float, ...],
                         halo_dm: tuple[float, ...]) -> list[float]:
    """Residual columns for each assumed disk and halo combination.

    Residual includes IGM + host + other unmodelled plasma; it is NOT an IGM estimate.
    """
    if not disk_dm or not halo_dm or not math.isfinite(observed_dm) or observed_dm < 0:
        raise ValueError('nonempty foreground grids and nonnegative observed DM required')
    values = []
    for disk in disk_dm:
        for halo in halo_dm:
            if not math.isfinite(disk) or not math.isfinite(halo) or min(disk, halo) < 0:
                raise ValueError('foreground columns must be finite and nonnegative')
            values.append(observed_dm - disk - halo)
    return values
