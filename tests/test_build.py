import ipaddress
import tempfile
import unittest
from pathlib import Path
from scripts.build import build

class TestBuild(unittest.TestCase):
    def test_collapse_and_domains(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"lists").mkdir()
            (root/"lists"/"a.txt").write_text("example.com\na.example.com\n1.1.1.1\n1.1.1.0/24\n")
            d,n=build(root/"lists",root/"all.txt",root/"domains.txt",root/"ips.txt")
            self.assertEqual((d,n),(1,1))
            self.assertIn("example.com", (root/"all.txt").read_text())
            self.assertNotIn("\na.example.com\n",(root/"all.txt").read_text())
    def test_wide_requires_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"lists").mkdir()
            (root/"lists"/"a.txt").write_text("34.0.0.0/15\n")
            with self.assertRaises(ValueError):
                build(root/"lists",root/"all.txt",root/"domains.txt",root/"ips.txt")
    def test_approved_discord(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"config").mkdir()
            (root/"config"/"approved-broad-cidrs.txt").write_text("172.64.0.0/13\n")
            (root/"lists").mkdir()
            (root/"lists"/"a.txt").write_text("172.64.0.0/13\n")
            d,n=build(root/"lists",root/"all.txt",root/"domains.txt",root/"ips.txt")
            self.assertEqual(n,1)

if __name__=="__main__":
    unittest.main()
