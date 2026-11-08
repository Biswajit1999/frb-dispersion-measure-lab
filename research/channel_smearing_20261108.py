"""Cold-plasma intra-channel dispersion audit (synthetic, no catalogue refit).

Frequency in MHz, DM in pc cm^-3, delay in ms. The standard dispersion
constant 4.148808e3 ms MHz^2 (pc cm^-3)^-1 is used. Channels are ideal
rectangular frequency responses; scattering and dedispersion errors omitted.
AI-assisted numerical implementation; scientific review required.
"""
import math
import unittest

K_DM = 4.148808e3

def delay_ms(dm, low_mhz, high_mhz):
    if not (math.isfinite(dm) and dm >= 0 and 0 < low_mhz < high_mhz
            and all(map(math.isfinite, (low_mhz, high_mhz)))):
        raise ValueError("Require nonnegative finite DM and ordered positive edges")
    return K_DM * dm * (low_mhz**-2 - high_mhz**-2)

def linear_smear_ms(dm, center_mhz, width_mhz):
    if not (math.isfinite(center_mhz) and math.isfinite(width_mhz)
            and width_mhz > 0 and center_mhz > width_mhz/2):
        raise ValueError("Invalid channel")
    if not (math.isfinite(dm) and dm >= 0):
        raise ValueError("Invalid DM")
    return 2*K_DM*dm*width_mhz/center_mhz**3

def channel_rms_ms(dm, center_mhz, width_mhz, n=4096):
    """Std of residual dispersive arrival times for a uniform-frequency channel.

    Midpoint quadrature, not a telescope channel-response calibration.
    """
    if not isinstance(n, int) or n < 2:
        raise ValueError("n must be >=2")
    linear_smear_ms(dm, center_mhz, width_mhz)
    start = center_mhz - width_mhz/2
    values = [K_DM*dm/(start + width_mhz*(i+0.5)/n)**2 for i in range(n)]
    mean = math.fsum(values)/n
    return math.sqrt(math.fsum((v-mean)**2 for v in values)/n)

class ChannelTests(unittest.TestCase):
    def test_exact_edges(self):
        self.assertAlmostEqual(delay_ms(100, 400, 800), 1.94475375)
    def test_linear_convergence(self):
        exact=delay_ms(500, 599.95, 600.05)
        self.assertAlmostEqual(exact/linear_smear_ms(500,600,0.1),1,delta=2e-8)
    def test_uniform_rms_limit(self):
        width=0.01
        rms=channel_rms_ms(300,600,width)
        self.assertAlmostEqual(rms/(linear_smear_ms(300,600,width)/math.sqrt(12)),1,delta=2e-6)
    def test_width_scaling(self):
        self.assertAlmostEqual(linear_smear_ms(200,600,0.2)/linear_smear_ms(200,600,0.1),2)
    def test_invalid(self):
        for args in [(-1,600,1),(1,0,1),(1,600,1200)]:
            with self.assertRaises(ValueError): channel_rms_ms(*args)

if __name__ == "__main__":
    unittest.main()
