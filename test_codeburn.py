"""Tests for eval/codeburn.py integration wrapper."""
import unittest
from unittest.mock import patch, MagicMock

import eval.codeburn as cb


class TestCodeburnIntegration(unittest.TestCase):
    def test_find_codeburn(self):
        # find_codeburn should return a valid string or None
        res = cb.find_codeburn()
        self.assertTrue(res is None or isinstance(res, str))

    @patch("eval.codeburn.run_codeburn_cmd")
    def test_get_status(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = "Today $1.00  Month $10.00\n"
        mock_run.return_value = mock_proc

        status = cb.get_status()
        self.assertEqual(status, "Today $1.00  Month $10.00")
        mock_run.assert_called_once_with(["status"], capture_output=True)

    @patch("eval.codeburn.run_codeburn_cmd")
    def test_get_overview(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = "CodeBurn Overview"
        mock_run.return_value = mock_proc

        overview = cb.get_overview(project="bench-router", period="month")
        self.assertEqual(overview, "CodeBurn Overview")
        mock_run.assert_called_once_with(["overview", "--project", "bench-router", "--period", "month"], capture_output=True)

    @patch("eval.codeburn.run_codeburn_cmd")
    def test_export_json(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.stdout = "Exported to codeburn.json"
        mock_run.return_value = mock_proc

        out = cb.export_json(project="bench-router", out_path="/tmp/test.json")
        self.assertEqual(out, "Exported to codeburn.json")
        mock_run.assert_called_once_with(["export", "-f", "json", "--project", "bench-router", "-o", "/tmp/test.json"], capture_output=True)


if __name__ == "__main__":
    unittest.main()
