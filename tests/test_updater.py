"""
Tests for Update and Upgrade Engine
"""

import os
import shutil
import tempfile
import unittest
from esim_tool_manager.modules.updater import ToolUpdater
from esim_tool_manager.core.config import config_manager


class TestToolUpdater(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.updater = ToolUpdater()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_backup_and_rollback(self):
        # Create a mock installed tool directory
        install_base = os.path.join(self.test_dir, "tools")
        backup_base = os.path.join(self.test_dir, "backups")
        tool_dir = os.path.join(install_base, "mock_tool")
        os.makedirs(tool_dir, exist_ok=True)

        original_file = os.path.join(tool_dir, "test.txt")
        with open(original_file, "w") as f:
            f.write("ORIGINAL_VERSION_1.0")

        # Configure paths in config_manager temporarily
        config_manager.set("install_dir", install_base)
        config_manager.set("backup_dir", backup_base)

        # 1. Test Backup
        backup_created = self.updater.create_tool_backup("mock_tool")
        self.assertIsNotNone(backup_created)
        self.assertTrue(os.path.exists(backup_created))

        # 2. Corrupt or delete the original tool folder
        with open(original_file, "w") as f:
            f.write("CORRUPTED_UPGRADE_FAIL")

        # 3. Test Rollback
        restored = self.updater.rollback_backup("mock_tool", backup_created)
        self.assertTrue(restored)

        with open(original_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "ORIGINAL_VERSION_1.0")


if __name__ == "__main__":
    unittest.main()
