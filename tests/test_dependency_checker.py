"""
Tests for Dependency Checker and Semantic Version Comparison
"""

import unittest
from esim_tool_manager.modules.dependency_checker import (
    parse_version_tuple,
    compare_versions,
    DependencyChecker
)
from esim_tool_manager.core.models import StatusEnum


class TestDependencyChecker(unittest.TestCase):

    def test_version_parsing(self):
        self.assertEqual(parse_version_tuple("42.0.1"), (42, 0, 1))
        self.assertEqual(parse_version_tuple("8.0"), (8, 0))
        self.assertEqual(parse_version_tuple("v1.2.3-rc1"), (1, 2, 3, 1))
        self.assertEqual(parse_version_tuple(""), (0,))

    def test_version_comparison(self):
        # 42.0 > 38.0
        self.assertEqual(compare_versions("42.0", "38.0"), 1)
        # 8.0.1 > 8.0.0
        self.assertEqual(compare_versions("8.0.1", "8.0.0"), 1)
        # 6.0.0 == 6.0.0
        self.assertEqual(compare_versions("6.0.0", "6.0.0"), 0)
        # 34.0 < 42.0
        self.assertEqual(compare_versions("34.0", "42.0"), -1)
        # 7.0 vs 7.0.0 (equivalent with padding)
        self.assertEqual(compare_versions("7.0", "7.0.0"), 0)

    def test_manifest_loading(self):
        checker = DependencyChecker()
        self.assertIn("tools", checker.manifest_data)
        self.assertIn("python_dependencies", checker.manifest_data)
        self.assertIn("ngspice", checker.manifest_data["tools"])
        self.assertIn("kicad", checker.manifest_data["tools"])

    def test_diagnostic_report_generation(self):
        checker = DependencyChecker()
        report = checker.run_full_diagnostic()
        self.assertIsNotNone(report.platform_info)
        self.assertIn("ngspice", report.tools)
        self.assertIn("matplotlib", report.dependencies)
        self.assertIn("total", report.summary)
        self.assertEqual(report.summary["total"], len(report.tools) + len(report.dependencies))


if __name__ == "__main__":
    unittest.main()
