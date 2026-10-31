"""Analytic limiting cases and covariance checks; no network access."""
import math

import pytest

from research.dm_sensitivity import (
    delay_error_budget,
    delay_seconds,
    dm_delay_covariance,
    residual_budget,
)


def test_chime_400_800_delay():
    assert delay_seconds(349.3490751229, 400, 800) == pytest.approx(6.79398, abs=1e-5)


def test_reference_invariance():
    dm = 349.3490751229
    assert delay_seconds(dm, 400, 800) == pytest.approx(
        delay_seconds(dm, 400, 600) + delay_seconds(dm, 600, 800), rel=1e-13
    )


def test_dm_uncertainty_is_linear():
    a = delay_error_budget(349.35, 0.006, 400, 800)
    b = delay_error_budget(349.35, 0.012, 400, 800)
    assert b["dm_sigma_s"] == pytest.approx(2 * a["dm_sigma_s"])
    assert a["independent_edges_sigma_s"] == 0


def test_common_and_independent_edge_models_differ():
    a = delay_error_budget(349.35, 0.006, 400, 800, 0.1)
    assert a["independent_edges_sigma_s"] > a["common_shift_sigma_s"] > 0


def test_shared_dm_covariance_is_rank_one():
    c = dm_delay_covariance(0.006, [(400, 600), (600, 800)])
    assert c[0][1] == pytest.approx(math.sqrt(c[0][0] * c[1][1]))
    assert c[0][0] * c[1][1] - c[0][1] ** 2 == pytest.approx(0, abs=1e-18)


def test_foreground_models_cannot_be_conflated():
    ne = residual_budget(349.3490751229, 198.93185424804688, (30, 80), 0.0337)
    ymw = residual_budget(349.3490751229, 324.8529968261719, (30, 80), 0.0337)
    assert ne["leftover_min_dm"] > 0
    assert ymw["leftover_max_dm"] < 0
    assert ne["nonnegative_host_compatible"] is True
    assert ymw["nonnegative_host_compatible"] is False


def test_invalid_input_rejected():
    with pytest.raises(ValueError):
        delay_seconds(100, 800, 400)
    with pytest.raises(ValueError):
        dm_delay_covariance(-1, [(400, 800)])
    with pytest.raises(ValueError):
        residual_budget(100, 110, (30, 80), 0.03)
