import unittest
import os
import re

class TestOfflineReadiness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_dir = r"c:\Users\USER\PythonDataViz2026_Dashboard_Group4"
        cls.index_path = os.path.join(cls.repo_dir, "index.html")
        with open(cls.index_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

    def test_local_vendor_assets_exist(self):
        """Verify all local vendor assets exist on disk and are non-empty"""
        vendor_files = ["tailwindcss.js", "chart.umd.min.js", "lucide.min.js"]
        for vf in vendor_files:
            vpath = os.path.join(self.repo_dir, "vendor", vf)
            self.assertTrue(os.path.exists(vpath), f"Missing {vf}")
            self.assertGreater(os.path.getsize(vpath), 50000, f"{vf} is too small")

    def test_no_broken_absolute_asset_paths(self):
        """Verify HTML only uses relative paths (./ or filename) for local assets"""
        src_matches = re.findall(r'src=["\']([^"\']+)["\']', self.html_content)
        href_matches = re.findall(r'href=["\']([^"\']+)["\']', self.html_content)

        for src in src_matches:
            if not src.startswith("http"):
                self.assertFalse(src.startswith("/"), f"Absolute path found in src: {src}")
                # verify local file exists
                clean_src = src.lstrip("./").replace("/", os.sep)
                local_path = os.path.join(self.repo_dir, clean_src)
                self.assertTrue(os.path.exists(local_path), f"Referenced src not found: {src}")

        for href in href_matches:
            if not href.startswith("http") and not href.startswith("#"):
                self.assertFalse(href.startswith("/"), f"Absolute path found in href: {href}")
                clean_href = href.lstrip("./").replace("/", os.sep)
                local_path = os.path.join(self.repo_dir, clean_href)
                self.assertTrue(os.path.exists(local_path), f"Referenced href not found: {href}")

    def test_datastore_offline_bundle(self):
        """Verify data_store.js provides valid offline data structures"""
        ds_path = os.path.join(self.repo_dir, "data", "processed", "data_store.js")
        self.assertTrue(os.path.exists(ds_path))
        with open(ds_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("window.DATA_AIID = [", content)
        self.assertIn("window.DATA_FINANCIAL = [", content)
        self.assertIn("window.DATA_WEEKLY = [", content)
        self.assertIn('"id": 1', content)
        self.assertIn('"id": 1749', content)

if __name__ == '__main__':
    unittest.main()
