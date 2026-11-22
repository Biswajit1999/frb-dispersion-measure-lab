"""FRB cold-plasma bandpass and foreground-envelope sensitivity; no IGM inference."""
import math
import unittest

K_DM = 4.148808e-3  # seconds GHz^2 / (pc cm^-3)

def delay_seconds(dm, low_mhz, high_mhz):
    if not (math.isfinite(dm) and dm >= 0 and 0 < low_mhz < high_mhz):
        raise ValueError("invalid dispersion or band edges")
    return K_DM*dm*((low_mhz/1000)**-2-(high_mhz/1000)**-2)

def delay_uncertainty(dm_sigma, low_mhz, high_mhz):
    if not math.isfinite(dm_sigma) or dm_sigma < 0:
        raise ValueError("invalid DM uncertainty")
    return delay_seconds(dm_sigma, low_mhz, high_mhz)

def excess_interval(total_dm, total_sigma, foreground_models, halo_bounds=(0.,0.)):
    """Conservative foreground-model and halo envelope, not an IGM estimate."""
    if not foreground_models or not all(math.isfinite(v) and v >= 0 for v in foreground_models):
        raise ValueError("foreground models required")
    if not (math.isfinite(total_dm) and math.isfinite(total_sigma) and total_sigma >= 0):
        raise ValueError("invalid observed DM")
    lo,hi=halo_bounds
    if not (0 <= lo <= hi and math.isfinite(hi)):
        raise ValueError("invalid halo bounds")
    return (total_dm-total_sigma-max(foreground_models)-hi,
            total_dm+total_sigma-min(foreground_models)-lo)

class Tests(unittest.TestCase):
    def test_zero(self): self.assertEqual(delay_seconds(0,400,800),0)
    def test_reference(self): self.assertAlmostEqual(delay_seconds(349.349,400,800),6.79398,places=4)
    def test_linearity(self): self.assertAlmostEqual(delay_seconds(20,400,800),2*delay_seconds(10,400,800))
    def test_uncertainty(self): self.assertAlmostEqual(delay_uncertainty(.006,400,800),delay_seconds(.006,400,800))
    def test_envelope(self): self.assertEqual(excess_interval(350,1,[200,325],(10,30)),(-6,141))
    def test_invalid(self):
        with self.assertRaises(ValueError): delay_seconds(1,800,400)
        with self.assertRaises(ValueError): excess_interval(10,1,[])

if __name__=="__main__": unittest.main()
