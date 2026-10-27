"""Synchronize published versions and identify changes that can reuse an image."""

import os
from pathlib import Path
import re
import subprocess
import sys


VERSION = r"[0-9]+\.[0-9]+\.[0-9]+"
DOCKER_VERSION = re.compile(rf"^ARG LRCGET_VERSION=({VERSION})$", re.MULTILINE)
README_VERSION = re.compile(rf"(?<=ghcr\.io/crywolf203/lrcget-unraid:)({VERSION})(?![\w.-])")


def version_tuple(value):
    if not re.fullmatch(VERSION, value):
        raise ValueError("Expected a stable major.minor.patch version")
    return tuple(map(int, value.split(".")))


def updated_files(dockerfile, readme, published):
    target = version_tuple(published)
    matches = DOCKER_VERSION.findall(dockerfile)
    readme_matches = README_VERSION.findall(readme)
    if len(matches) != 1 or len(readme_matches) != 1:
        raise ValueError("Expected exactly one Dockerfile version and one README image version")
    # Do not let a stale run or an older manual build lower either version.
    if target < max(version_tuple(matches[0]), version_tuple(readme_matches[0])):
        return dockerfile, readme
    return (
        DOCKER_VERSION.sub(f"ARG LRCGET_VERSION={published}", dockerfile),
        README_VERSION.sub(published, readme),
    )


def metadata_only(changed_paths, before, after):
    if not changed_paths or not set(changed_paths) <= {"Dockerfile", "README.md"}:
        return False
    if len(DOCKER_VERSION.findall(before)) != 1 or len(DOCKER_VERSION.findall(after)) != 1:
        return False
    return DOCKER_VERSION.sub("ARG LRCGET_VERSION=<version>", before) == DOCKER_VERSION.sub(
        "ARG LRCGET_VERSION=<version>", after
    )


def classify(base):
    if not re.fullmatch(r"[0-9a-f]{40}", base or "") or base == "0" * 40:
        return False
    def git(*args):
        return subprocess.check_output(["git", *args], text=True, encoding="utf-8")
    try:
        paths = git("diff", "--name-only", base, "HEAD").splitlines()
        before = git("show", f"{base}:Dockerfile")
        after = git("show", "HEAD:Dockerfile")
        return metadata_only(paths, before, after)
    except subprocess.CalledProcessError:
        # Incomplete history or new files must take the normal build path.
        return False


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "classify":
        result = str(classify(os.environ.get("BASE_SHA", ""))).lower()
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(f"metadata_only={result}\n")
        print(f"Version/documentation-only change: {result}")
    elif len(sys.argv) == 3 and sys.argv[1] == "update":
        paths = [Path("Dockerfile"), Path("README.md")]
        originals = [path.read_text(encoding="utf-8") for path in paths]
        updates = updated_files(*originals, sys.argv[2])
        for path, original, updated in zip(paths, originals, updates):
            if original != updated:
                path.write_text(updated, encoding="utf-8", newline="\n")
                print(f"Updated {path} to {sys.argv[2]}")
    else:
        raise SystemExit("Usage: sync-version.py classify | update VERSION")


if __name__ == "__main__":
    main()
