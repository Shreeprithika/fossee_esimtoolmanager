"""
Tests for Tool Installer and Archive Extraction
"""

import os
import shutil
import zipfile
import tempfile
import unittest
from esim_tool_manager.modules.installer import ToolInstaller


class TestToolInstaller(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.installer = ToolInstaller()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_zip_extraction(self):
        # Create a mock zip archive
        zip_path = os.path.join(self.test_dir, "mock_tool.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("bin/mock_tool.exe", "MOCK_EXECUTABLE_CONTENT")
            zf.writestr("README.txt", "Mock tool test")

        extract_dest = os.path.join(self.test_dir, "extracted")
        ok = self.installer.extract_archive(zip_path, extract_dest)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(os.path.join(extract_dest, "bin", "mock_tool.exe")))

    def test_dry_run_package_manager(self):
        ok = self.installer.install_via_package_manager(
            tool_key="ngspice",
            pm_name="winget",
            package_identifier="Ngspice.Ngspice",
            dry_run=True
        )
        self.assertTrue(ok)

    def test_dry_run_install_tool(self):
        ok = self.installer.install_tool("ngspice", dry_run=True)
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
