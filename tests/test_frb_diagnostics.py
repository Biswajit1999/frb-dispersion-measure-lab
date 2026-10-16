"""Numerical invariants and edge cases for the FRB sensitivity diagnostics."""
import math
import unittest
from research_analysis.frb_diagnostics import (
    K_DM_SECONDS, channel_smearing, delay_with_uncertainty,
    foreground_sensitivity, stratified_percentile, wilson_interval)


class DispersionTests(unittest.TestCase):
    def test_400_to_800(self):
        r = delay_with_uncertainty(349.3490751229, 0.0058411, 400, 800)
        self.assertAlmostEqual(r['delay_s'], 6.793979, places=5)
        self.assertGreater(r['sigma_s'], 0)

    def test_dm_linearity(self):
        a = delay_with_uncertainty(100, 0, 400, 800)
        b = delay_with_uncertainty(200, 0, 400, 800)
        self.assertAlmostEqual(b['delay_s'], 2*a['delay_s'])

    def test_dm_uncertainty_finite_difference(self):
        x = delay_with_uncertainty(300, .2, 400, 800)
        plus = delay_with_uncertainty(300.2, 0, 400, 800)['delay_s']
        minus = delay_with_uncertainty(299.8, 0, 400, 800)['delay_s']
        self.assertAlmostEqual(x['sigma_components_s']['dm'], (plus-minus)/2, places=10)

    def test_frequency_uncertainty_finite_difference(self):
        x = delay_with_uncertainty(300, 0, 400, 800, .01, .02)
        lo_plus = delay_with_uncertainty(300, 0, 400.01, 800)['delay_s']
        lo_minus = delay_with_uncertainty(300, 0, 399.99, 800)['delay_s']
        self.assertAlmostEqual(x['sigma_components_s']['low_edge'], abs(lo_plus-lo_minus)/2, delta=1e-8)

    def test_channel_narrow_limit(self):
        x = channel_smearing(349, 600, .1)
        self.assertLess(x['approximation_relative_error'], 1e-6)

    def test_invalid_frequencies(self):
        with self.assertRaises(ValueError): delay_with_uncertainty(100, 0, 800, 400)
        with self.assertRaises(ValueError): channel_smearing(100, 400, 800)


class ForegroundTests(unittest.TestCase):
    def test_model_spread_and_negative_residual(self):
        x = foreground_sensitivity(349.349, {'NE2001': 198.93, 'YMW16': 324.85}, (30, 80), 30.33)
        self.assertGreater(x['models']['NE2001']['excess_after_disk'],
                           x['models']['YMW16']['excess_after_disk'])
        self.assertLess(x['models']['YMW16']['residual_after_halo_and_reference_cosmic'][1], 0)

    def test_interval_ordering(self):
        with self.assertRaises(ValueError): foreground_sensitivity(100, {'a': 50}, (80, 30))


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {'dm': 100, 'snr': 12, 'galactic_latitude': 40, 'repeater': False},
            {'dm': 300, 'snr': 15, 'galactic_latitude': 5, 'repeater': True},
            {'dm': 500, 'snr': 25, 'galactic_latitude': -30, 'repeater': False},
            {'dm': 800, 'snr': 30, 'galactic_latitude': 20, 'repeater': True},
        ]

    def test_unfiltered_percentile(self):
        x = stratified_percentile(self.rows, 400)
        self.assertEqual((x['n_bursts'], x['n_below_or_equal']), (4, 2))
        self.assertEqual(x['percentile'], 50)

    def test_latitude_selection(self):
        x = stratified_percentile(self.rows, 400, min_abs_lat=25)
        self.assertEqual(x['n_bursts'], 2)
        self.assertEqual(x['percentile'], 50)

    def test_repeater_selection(self):
        x = stratified_percentile(self.rows, 400, repeater=True)
        self.assertEqual(x['n_bursts'], 2)
        self.assertEqual(x['percentile'], 50)

    def test_empty_selection(self):
        x = stratified_percentile(self.rows, 400, min_snr=100)
        self.assertIsNone(x['percentile'])

    def test_wilson_extremes(self):
        lo, hi = wilson_interval(0, 100)
        self.assertEqual(lo, 0)
        self.assertGreater(hi, 0)
        lo, hi = wilson_interval(100, 100)
        self.assertEqual(hi, 1)
        self.assertLess(lo, 1)

if __name__ == '__main__': unittest.main()
