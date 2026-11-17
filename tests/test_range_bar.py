import unittest
from xml.etree import ElementTree

from report.html import range_bar


class RangeBarTests(unittest.TestCase):
    def test_real_interval_geometry_and_reference_line(self):
        text = range_bar({"observed_range_ratio_bounds": [1.1, 1.2], "threshold_sensitive": True}, 0.15)
        svg = ElementTree.fromstring(text)
        self.assertEqual(svg.attrib["role"], "img")
        self.assertIn("不是置信区间", svg.attrib["aria-label"])
        lines = svg.findall("line")
        reference, bar = lines[2], lines[3]
        self.assertLess(float(bar.attrib["x1"]), float(reference.attrib["x1"]))
        self.assertLess(float(reference.attrib["x1"]), float(bar.attrib["x2"]))
        self.assertEqual(reference.attrib["stroke-dasharray"], "4 3")
        self.assertTrue(all(30 <= float(line.attrib[key]) <= 390 for line in lines for key in ("x1", "x2")))

    def test_missing_invalid_intervals_are_not_plotted(self):
        for bounds in (None, [], [1.3, 1.2], [float("nan"), 1], [True, 1.2], [-1, 2]):
            self.assertNotIn("<svg", range_bar({"observed_range_ratio_bounds": bounds}, 0.15))
