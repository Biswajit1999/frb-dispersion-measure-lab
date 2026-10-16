"""Reproducible diagnostics for the frozen CHIME/FRB Catalog 1 derivative.

These are descriptive, sensitivity and uncertainty analyses, not a new
host/IGM decomposition or a population selection-function correction.
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Iterable, Mapping

K_DM_SECONDS = 4.148808e3  # s MHz^2 (pc cm^-3)^-1


def _nonnegative(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def _frequency(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def delay_with_uncertainty(dm: float, dm_sigma: float, nu_low_mhz: float,
                           nu_high_mhz: float, low_sigma_mhz: float = 0,
                           high_sigma_mhz: float = 0) -> dict:
    """Cold-plasma sweep and first-order independent-input 1-sigma uncertainty.

    The frequency uncertainties are independent absolute edge uncertainties,
    not channel widths; correlations must be handled externally.
    """
    dm = _nonnegative('dm', dm)
    dm_sigma = _nonnegative('dm_sigma', dm_sigma)
    lo = _frequency('nu_low_mhz', nu_low_mhz)
    hi = _frequency('nu_high_mhz', nu_high_mhz)
    sl = _nonnegative('low_sigma_mhz', low_sigma_mhz)
    sh = _nonnegative('high_sigma_mhz', high_sigma_mhz)
    if lo >= hi:
        raise ValueError('low frequency must be below high frequency')
    delta = lo ** -2 - hi ** -2
    delay = K_DM_SECONDS * dm * delta
    terms = {
        'dm': K_DM_SECONDS * delta * dm_sigma,
        'low_edge': -2 * K_DM_SECONDS * dm * lo ** -3 * sl,
        'high_edge': 2 * K_DM_SECONDS * dm * hi ** -3 * sh,
    }
    return {'delay_s': delay,
            'sigma_s': math.sqrt(sum(x * x for x in terms.values())),
            'sigma_components_s': {k: abs(v) for k, v in terms.items()},
            'assumption': 'independent DM and frequency-edge uncertainties; linear propagation'}


def channel_smearing(dm: float, centre_mhz: float, width_mhz: float) -> dict:
    """Exact dispersive sweep across a top-hat channel, not instrumental width."""
    dm = _nonnegative('dm', dm)
    centre = _frequency('centre_mhz', centre_mhz)
    width = _frequency('width_mhz', width_mhz)
    if width >= 2 * centre:
        raise ValueError('channel lower edge must be positive')
    exact = K_DM_SECONDS * dm * ((centre - width / 2) ** -2 -
                               (centre + width / 2) ** -2)
    linear = 2 * K_DM_SECONDS * dm * width / centre ** 3
    return {'smearing_s': exact, 'narrow_channel_approx_s': linear,
            'approximation_relative_error': abs(linear - exact) / exact if exact else 0.0}


def foreground_sensitivity(observed_dm: float, disk_models: Mapping[str, float],
                           halo_range: tuple[float, float],
                           cosmic_reference: float | None = None) -> dict:
    """Compute model-conditional *residuals*, never a unique host-DM estimate.

    The halo interval is illustrative. A negative residual is retained to
    expose inconsistent assumptions rather than clipped to zero.
    """
    obs = _nonnegative('observed_dm', observed_dm)
    h0, h1 = map(float, halo_range)
    _nonnegative('halo_min', h0)
    _nonnegative('halo_max', h1)
    if h0 > h1 or not disk_models:
        raise ValueError('need ordered halo interval and at least one disk model')
    cosmic = None if cosmic_reference is None else _nonnegative('cosmic_reference', cosmic_reference)
    models = {}
    for name, value in disk_models.items():
        disk = _nonnegative(f'disk model {name}', value)
        after_disk = obs - disk
        residuals = [after_disk - h0, after_disk - h1]
        models[str(name)] = {
            'disk_dm': disk, 'excess_after_disk': after_disk,
            'residual_after_halo_range': [min(residuals), max(residuals)],
            'residual_after_halo_and_reference_cosmic': None if cosmic is None
                else [min(residuals) - cosmic, max(residuals) - cosmic],
        }
    return {'observed_dm': obs, 'halo_range': [h0, h1],
            'cosmic_reference': cosmic, 'models': models,
            'warning': 'model-conditional residuals; halo and cosmic reference are not independently inferred'}


def wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """Binomial Wilson interval, descriptive only for a non-random catalogue."""
    if trials <= 0 or successes < 0 or successes > trials or not 0 < confidence < 1:
        raise ValueError('invalid binomial counts or confidence')
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    p = successes / trials
    denom = 1 + z*z/trials
    centre = (p + z*z/(2*trials))/denom
    half = z * math.sqrt(p*(1-p)/trials + z*z/(4*trials*trials))/denom
    return max(0, centre-half), min(1, centre+half)


def stratified_percentile(events: Iterable[dict], target_dm: float,
                          min_snr: float = 0, min_abs_lat: float = 0,
                          repeater: bool | None = None) -> dict:
    """Catalog DM percentile conditional on explicit observational cuts.

    Records are *bursts*, not independent FRB sources. Wilson bounds are
    shown as a descriptive sampling diagnostic, not survey-corrected errors.
    """
    target_dm = _nonnegative('target_dm', target_dm)
    min_snr = _nonnegative('min_snr', min_snr)
    min_abs_lat = _nonnegative('min_abs_lat', min_abs_lat)
    if min_abs_lat > 90:
        raise ValueError('latitude cut exceeds 90 degrees')
    selected = []
    for event in events:
        dm = float(event['dm'])
        snr = float(event['snr'])
        lat = float(event['galactic_latitude'])
        if not all(math.isfinite(v) for v in (dm, snr, lat)):
            continue
        if dm < 0 or snr < min_snr or abs(lat) < min_abs_lat:
            continue
        if repeater is not None and bool(event['repeater']) != repeater:
            continue
        selected.append(dm)
    n = len(selected)
    if not n:
        return {'n_bursts': 0, 'n_below_or_equal': 0, 'percentile': None,
                'wilson_95_pct': None, 'median_dm': None}
    k = sum(x <= target_dm for x in selected)
    lo, hi = wilson_interval(k, n)
    ordered = sorted(selected)
    median = ordered[n//2] if n % 2 else (ordered[n//2-1]+ordered[n//2])/2
    return {'n_bursts': n, 'n_below_or_equal': k, 'percentile': 100*k/n,
            'wilson_95_pct': [100*lo, 100*hi], 'median_dm': median}
