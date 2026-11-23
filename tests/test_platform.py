"""
Tests for Platform Detection Engine
"""

import unittest
import platform
from esim_tool_manager.core.platform_detect import PlatformDetector
from esim_tool_manager.core.models import SystemPlatformInfo


class TestPlatformDetector(unittest.TestCase):

    def test_os_type_detection(self):
        os_type = PlatformDetector.get_os_type()
        self.assertIn(os_type, ["windows", "linux", "darwin"])

    def test_os_name_non_empty(self):
        name = PlatformDetector.get_os_name()
        self.assertTrue(len(name) > 0)

    def test_architecture(self):
        arch = PlatformDetector.get_architecture()
        self.assertIn(arch, ["x86_64", "arm64", "x86", "aarch64", platform.machine().lower()])

    def test_package_managers_detection(self):
        pms = PlatformDetector.detect_package_managers()
        self.assertIsInstance(pms, list)

    def test_system_info_model(self):
        info = PlatformDetector.get_system_info()
        self.assertIsInstance(info, SystemPlatformInfo)
        self.assertEqual(info.os_type, PlatformDetector.get_os_type())
        self.assertEqual(info.python_version, platform.python_version())


if __name__ == "__main__":
    unittest.main()
