"""Auditable FRB cold-plasma and catalog-selection sensitivity diagnostics.

Dispersion measures are pc cm^-3, frequencies MHz, and delays seconds.
Foreground calculations are conditional, not unique Milky-Way/IGM/host
decompositions. Event bootstrap intervals are descriptive, not population CIs.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Mapping, Sequence
import math
import numpy as np

K_DM_SECONDS_MHZ2 = 4.148808e3


def _nonnegative(name: str, x: float) -> float:
    value = float(x)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return value


def cold_plasma_delay(dm: float, low_mhz: float, high_mhz: float,
                      dm_sigma: float = 0.0) -> dict[str, float]:
    """Band-edge arrival delay and first-order uncertainty from DM alone."""
    dm = _nonnegative("dm", dm)
    sigma = _nonnegative("dm_sigma", dm_sigma)
    low, high = float(low_mhz), float(high_mhz)
    if not all(map(math.isfinite, (low, high))) or not 0 < low < high:
        raise ValueError("require 0 < low_mhz < high_mhz")
    factor = K_DM_SECONDS_MHZ2 * (1/low**2 - 1/high**2)
    return {"delay_s": dm*factor, "dm_only_sigma_s": sigma*factor,
            "delay_per_dm_s": factor}


def intra_channel_smearing(dm: float, centre_mhz: float, width_mhz: float) -> float:
    """Exact cold-plasma delay across one channel, before dedispersion."""
    dm = _nonnegative("dm", dm)
    centre, width = float(centre_mhz), float(width_mhz)
    if not math.isfinite(centre) or not math.isfinite(width) or centre <= 0 or not 0 <= width < 2*centre:
        raise ValueError("invalid positive centre or channel width")
    if width == 0:
        return 0.0
    return cold_plasma_delay(dm, centre-width/2, centre+width/2)["delay_s"]


def foreground_halo_sensitivity(observed_dm: float, excess_after_disk: Mapping[str, float],
                                halo_min: float, halo_max: float,
                                dm_sigma: float = 0.0) -> dict[str, dict[str, float | bool]]:
    """Conditional residual intervals after alternative Galactic disk models.

    Negative residuals flag an incompatible additive assumption; they do not
    indicate negative host/IGM plasma.
    """
    dm = _nonnegative("observed_dm", observed_dm)
    sigma = _nonnegative("dm_sigma", dm_sigma)
    hmin = _nonnegative("halo_min", halo_min)
    hmax = _nonnegative("halo_max", halo_max)
    if hmax < hmin:
        raise ValueError("halo_max must be >= halo_min")
    if not excess_after_disk:
        raise ValueError("at least one foreground model is required")
    results: dict[str, dict[str, float | bool]] = {}
    for model, raw_excess in excess_after_disk.items():
        excess = _nonnegative(str(model), raw_excess)
        disk = dm-excess
        if disk < 0:
            raise ValueError("disk contribution would be negative")
        lo, hi = excess-hmax, excess-hmin
        results[str(model)] = {
            "disk_dm": disk, "excess_after_disk": excess,
            "residual_min": lo, "residual_max": hi,
            "dm_only_sigma": sigma,
            "negative_residual_possible": lo < 0,
            "entire_interval_nonnegative": lo >= 0,
        }
    return results


@dataclass(frozen=True)
class CatalogSensitivity:
    n_events: int
    n_repeater_events: int
    n_nonrepeater_events: int
    target_percentile: float
    leave_one_out_percentile_min: float
    leave_one_out_percentile_max: float
    median_repeater_dm: float
    median_nonrepeater_dm: float
    median_difference_dm: float
    bootstrap_difference_ci_95: tuple[float, float]
    bootstrap_trials: int
    bootstrap_seed: int
    caveat: str


def catalog_event_sensitivity(events: Sequence[Mapping[str, object]], target_dm: float,
                              *, trials: int = 2000, seed: int = 20261014) -> CatalogSensitivity:
    """Event-level bootstrap of repeater/nonrepeater DM contrast.

    Repeat bursts are correlated and CHIME selection is not corrected. These
    are *not* source-population confidence intervals or causal inferences.
    """
    target = _nonnegative("target_dm", target_dm)
    if isinstance(trials, bool) or not isinstance(trials, int) or trials < 100:
        raise ValueError("trials must be an integer >= 100")
    if len(events) < 3:
        raise ValueError("at least three catalogued events required")
    dms = np.asarray([_nonnegative("event dm", e["dm"]) for e in events], dtype=float)
    flags = np.asarray([e["repeater"] for e in events])
    if flags.dtype != np.bool_:
        raise ValueError("event repeater flags must be booleans")
    repeated, other = dms[flags], dms[~flags]
    if len(repeated) < 2 or len(other) < 2:
        raise ValueError("at least two events in each group required")
    n = len(dms)
    count_le = int(np.count_nonzero(dms <= target))
    loo = [100*(count_le - (1 if x <= target else 0))/(n-1) for x in dms]
    rng = np.random.default_rng(seed)
    diffs = np.empty(trials, dtype=float)
    for i in range(trials):
        a = rng.choice(repeated, len(repeated), replace=True)
        b = rng.choice(other, len(other), replace=True)
        diffs[i] = np.median(a) - np.median(b)
    ci = np.quantile(diffs, [0.025, 0.975])
    return CatalogSensitivity(
        n_events=n, n_repeater_events=len(repeated), n_nonrepeater_events=len(other),
        target_percentile=100*count_le/n,
        leave_one_out_percentile_min=float(min(loo)),
        leave_one_out_percentile_max=float(max(loo)),
        median_repeater_dm=float(np.median(repeated)),
        median_nonrepeater_dm=float(np.median(other)),
        median_difference_dm=float(np.median(repeated)-np.median(other)),
        bootstrap_difference_ci_95=(float(ci[0]), float(ci[1])),
        bootstrap_trials=trials, bootstrap_seed=seed,
        caveat="Event-level descriptive resampling; repeated bursts are correlated, selection uncorrected.",
    )


def catalog_sensitivity_dict(*args: object, **kwargs: object) -> dict[str, object]:
    """JSON-ready summary."""
    return asdict(catalog_event_sensitivity(*args, **kwargs))
