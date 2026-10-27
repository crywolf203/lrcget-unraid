import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("sync_version", Path(__file__).with_name("sync-version.py"))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class VersionSyncTests(unittest.TestCase):
    dockerfile = "FROM example:1\nARG LRCGET_VERSION=2.2.0\nRUN echo build\n"
    readme = "Image: ghcr.io/crywolf203/lrcget-unraid:2.2.0\nDefault: ghcr.io/crywolf203/lrcget-unraid:latest\n"

    def test_update_and_repeat(self):
        dockerfile, readme = sync.updated_files(self.dockerfile, self.readme, "2.2.1")
        self.assertIn("ARG LRCGET_VERSION=2.2.1", dockerfile)
        self.assertIn("lrcget-unraid:2.2.1", readme)
        self.assertIn("lrcget-unraid:latest", readme)
        self.assertEqual((dockerfile, readme), sync.updated_files(dockerfile, readme, "2.2.1"))

    def test_no_downgrades(self):
        self.assertEqual((self.dockerfile, self.readme), sync.updated_files(self.dockerfile, self.readme, "2.1.9"))
        newer_readme = self.readme.replace("2.2.0", "2.10.0")
        self.assertEqual((self.dockerfile, newer_readme), sync.updated_files(self.dockerfile, newer_readme, "2.9.0"))

    def test_numeric_version_order(self):
        self.assertIn("2.10.0", sync.updated_files(self.dockerfile, self.readme, "2.10.0")[0])

    def test_reject_invalid_versions(self):
        for value in ["", "v2.2.1", "2.2.1-rc1", "2.2.1\nevil", "$(echo bad)"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                sync.updated_files(self.dockerfile, self.readme, value)

    def test_fail_if_expected_fields_are_missing_or_duplicated(self):
        for dockerfile, readme in [("FROM example", self.readme), (self.dockerfile * 2, self.readme), (self.dockerfile, "missing"), (self.dockerfile, self.readme * 2)]:
            with self.subTest(dockerfile=dockerfile, readme=readme), self.assertRaises(ValueError):
                sync.updated_files(dockerfile, readme, "2.2.1")

    def test_version_only_and_readme_only(self):
        updated = self.dockerfile.replace("2.2.0", "2.2.1")
        self.assertTrue(sync.metadata_only(["Dockerfile", "README.md"], self.dockerfile, updated))
        self.assertTrue(sync.metadata_only(["README.md"], self.dockerfile, self.dockerfile))

    def test_real_build_changes_are_not_skipped(self):
        for paths, updated in [(["Dockerfile"], self.dockerfile.replace("example:1", "example:2")), (["Dockerfile"], self.dockerfile + "RUN echo changed\n"), (["startapp.sh"], self.dockerfile), ([".github/workflows/docker-publish.yml"], self.dockerfile), ([], self.dockerfile)]:
            with self.subTest(paths=paths, updated=updated):
                self.assertFalse(sync.metadata_only(paths, self.dockerfile, updated))

    def test_missing_base_builds_normally(self):
        for base in ["", "0" * 40, "invalid"]:
            self.assertFalse(sync.classify(base))


if __name__ == "__main__":
    unittest.main()
