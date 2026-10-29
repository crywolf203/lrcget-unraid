import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
import urllib.error

spec = importlib.util.spec_from_file_location("publish_release", Path(__file__).with_name("publish-release.py"))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class PublishReleaseTests(unittest.TestCase):
    def publish(self, request, version="2.2.1"):
        return release.publish(version, "a" * 40, "crywolf203/lrcget-unraid", "123", request)

    def test_create_release_and_tag(self):
        request = Mock(side_effect=[None, {"tag_name": "v1.1.0"}, {"html_url": "https://example.com/release"}])
        self.publish(request)
        method, path, payload = request.call_args.args
        self.assertEqual((method, path), ("POST", "/releases"))
        self.assertEqual(payload["tag_name"], "lrcget-2.2.1")
        self.assertEqual(payload["target_commitish"], "a" * 40)
        self.assertEqual(payload["make_latest"], "true")
        self.assertIn("releases/tag/2.2.1", payload["body"])
        self.assertIn("ghcr.io/crywolf203/lrcget-unraid:2.2.1", payload["body"])

    def test_existing_release_is_not_modified(self):
        for draft in (True, False):
            request = Mock(return_value={"draft": draft})
            self.publish(request)
            request.assert_called_once_with("GET", "/releases/tags/lrcget-2.2.1")

    def test_backfill_does_not_replace_latest(self):
        request = Mock(side_effect=[None, {"tag_name": "lrcget-2.10.0"}, {"html_url": "test"}])
        self.publish(request, "2.9.0")
        self.assertEqual(request.call_args.args[2]["make_latest"], "false")

    def test_first_release_becomes_latest(self):
        request = Mock(side_effect=[None, None, {"html_url": "test"}])
        self.publish(request)
        self.assertEqual(request.call_args.args[2]["make_latest"], "true")

    def test_invalid_version_never_calls_api(self):
        request = Mock()
        with self.assertRaises(ValueError):
            self.publish(request, "2.2.1\nbad")
        request.assert_not_called()

    def test_api_errors_are_not_treated_as_missing_releases(self):
        for status in (403, 429, 500):
            error = urllib.error.HTTPError("url", status, "error", {}, None)
            with patch.object(release.urllib.request, "urlopen", side_effect=error), self.assertRaises(urllib.error.HTTPError):
                release.github_request("owner/repo", "test-token", "GET", "/releases/latest")

    def test_only_get_404_means_absent(self):
        error = urllib.error.HTTPError("url", 404, "missing", {}, None)
        with patch.object(release.urllib.request, "urlopen", side_effect=error):
            self.assertIsNone(release.github_request("owner/repo", "test-token", "GET", "/releases/latest"))
            with self.assertRaises(urllib.error.HTTPError):
                release.github_request("owner/repo", "test-token", "POST", "/releases", {})


if __name__ == "__main__":
    unittest.main()
