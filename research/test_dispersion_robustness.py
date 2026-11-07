import unittest
from dispersion_robustness import sweep_delay, delay_uncertainty, foreground_scenarios

class TestDispersion(unittest.TestCase):
    def test_reference_sweep(self):
        self.assertAlmostEqual(sweep_delay(349.349,400,800), 6.79398, places=4)
    def test_linear_uncertainty(self):
        self.assertAlmostEqual(delay_uncertainty(.006,400,800), sweep_delay(349.349,400,800)*.006/349.349)
    def test_frequency_order(self):
        with self.assertRaises(ValueError): sweep_delay(10,800,400)
    def test_foreground_grid(self):
        self.assertEqual(foreground_scenarios(350,(200,300),(30,80)),[120,70,20,-30])
    def test_negative_foreground(self):
        with self.assertRaises(ValueError): foreground_scenarios(350,(-1,),(30,))
if __name__ == '__main__': unittest.main()
