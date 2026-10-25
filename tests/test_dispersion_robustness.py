import numpy as np
import pytest

from science.dispersion_robustness import (
    K_DM_S_MHZ2, cold_plasma_delay_s, dispersion_delay_sigma_s,
    intrachannel_smearing_ms, conditional_host_dm_interval,
)


def test_catalog_sweep_reproduced():
    assert float(cold_plasma_delay_s(349.3490751229, 400.0)) == pytest.approx(6.793979, abs=1e-6)
    assert float(cold_plasma_delay_s(349.3490751229, 800.0)) == 0.0


def test_delay_scales_with_dm_and_inverse_frequency_squared():
    nu = np.array([400., 600., 800.])
    d = cold_plasma_delay_s(100., nu)
    assert np.all(np.diff(d) < 0)
    assert np.allclose(cold_plasma_delay_s(200., nu), 2*d)


def test_analytic_uncertainty_matches_seeded_monte_carlo():
    rng = np.random.default_rng(25)
    dm, dm_sigma, nu, nu_sigma = 349.349, 0.006, 600., 0.01
    analytic = float(dispersion_delay_sigma_s(dm, dm_sigma, nu, frequency_sigma_mhz=nu_sigma))
    simulated = cold_plasma_delay_s(rng.normal(dm, dm_sigma, 80000), rng.normal(nu, nu_sigma, 80000))
    assert np.std(simulated) == pytest.approx(analytic, rel=0.02)


def test_uncertainty_at_reference_only_dm_is_zero():
    assert float(dispersion_delay_sigma_s(349., 0.01, 800.)) == 0.0


def test_smearing_agrees_with_narrow_channel_limit():
    dm, nu, width = 349.349, 600., 0.1
    exact = float(intrachannel_smearing_ms(dm, nu, width))
    approx = 1e3 * K_DM_S_MHZ2 * dm * 2*width/nu**3
    assert exact == pytest.approx(approx, rel=1e-7)
    assert float(intrachannel_smearing_ms(0, nu, width)) == 0.0


def test_smearing_rejects_nonphysical_channels():
    with pytest.raises(ValueError):
        intrachannel_smearing_ms(100, 400, 800)


def test_conditional_foreground_models_not_interchangeable():
    observed = 349.3490751229
    ne = conditional_host_dm_interval(observed, observed-150.4, (30,80), (0,40))
    ymw = conditional_host_dm_interval(observed, observed-24.5, (30,80), (0,40))
    assert ne.physical_overlap
    assert ne.feasible_host_interval == pytest.approx((30.4, 120.4))
    assert not ymw.physical_overlap
    assert ymw.feasible_host_interval is None


def test_foreground_validation():
    with pytest.raises(ValueError):
        conditional_host_dm_interval(200, 50, (70, 30), (0, 100))
    with pytest.raises(ValueError):
        cold_plasma_delay_s(-1, 600)
