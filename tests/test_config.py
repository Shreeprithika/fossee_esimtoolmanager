"""
Tests for Configuration Management and eSim Profile Generation
"""

import os
import shutil
import tempfile
import unittest
from esim_tool_manager.core.config import ConfigurationManager


class TestConfigurationManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test_config.json")
        self.cfg_mgr = ConfigurationManager(config_path=self.config_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_default_values(self):
        self.assertTrue(os.path.exists(self.config_file))
        self.assertIn("install_dir", self.cfg_mgr.config_data)
        self.assertTrue(self.cfg_mgr.get("auto_backup"))

    def test_set_and_get(self):
        self.cfg_mgr.set("custom_test_key", "test_value_123")
        self.assertEqual(self.cfg_mgr.get("custom_test_key"), "test_value_123")

        # Reload from disk
        reloaded = ConfigurationManager(config_path=self.config_file)
        self.assertEqual(reloaded.get("custom_test_key"), "test_value_123")

    def test_custom_tool_path(self):
        fake_path = "C:/fake/path/to/ngspice.exe"
        self.cfg_mgr.set_custom_path("ngspice", fake_path)
        self.assertEqual(self.cfg_mgr.get_custom_path("ngspice"), fake_path)

    def test_esim_profile_export(self):
        tool_paths = {
            "ngspice": "C:/fake/ngspice.exe",
            "kicad": "C:/fake/kicad.exe"
        }
        res = self.cfg_mgr.export_esim_profile(tool_paths, output_dir=self.test_dir)
        self.assertIn("json_profile", res)
        self.assertIn("ini_profile", res)
        self.assertIn("windows_bat", res)
        self.assertIn("shell_script", res)

        self.assertTrue(os.path.exists(res["json_profile"]))
        self.assertTrue(os.path.exists(res["ini_profile"]))
        self.assertTrue(os.path.exists(res["windows_bat"]))
        self.assertTrue(os.path.exists(res["shell_script"]))


if __name__ == "__main__":
    unittest.main()
