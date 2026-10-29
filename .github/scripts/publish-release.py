"""Create one GitHub release per successfully published LRCGET image version."""

import json
import os
import re
import urllib.error
import urllib.request


def version_tuple(version):
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Expected a stable major.minor.patch LRCGET version")
    return tuple(map(int, version.split(".")))


def publish(version, sha, repository, run_id, request):
    target = version_tuple(version)
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Expected the workflow commit SHA")
    tag = f"lrcget-{version}"
    existing = request("GET", f"/releases/tags/{tag}")
    if existing is not None:
        print(f"Release {tag} already exists; leaving it unchanged.")
        return existing
    latest = request("GET", "/releases/latest")
    make_latest = True
    if latest and latest["tag_name"].startswith("lrcget-"):
        make_latest = target > version_tuple(latest["tag_name"][len("lrcget-"):])
    image = f"ghcr.io/{repository}:{version}"
    body = (
        f"LRCGET **{version}** is available in the unofficial Unraid container.\n\n"
        f"**Docker image:** `{image}`\n\n"
        f"[Upstream LRCGET {version} release notes]"
        f"(https://github.com/tranxuanthang/lrcget/releases/tag/{version})\n\n"
        f"[Image publication or availability check]"
        f"(https://github.com/{repository}/actions/runs/{run_id})\n\n"
        "In Unraid, check for Docker updates and apply the update. "
        "Use the versioned image above to select this exact LRCGET version.\n\n"
        "This release tracks the packaged LRCGET version. Existing wrapper-version "
        "releases are preserved. The tag records the workflow revision that confirmed "
        "the image was available; the image may have been published by an earlier run.\n"
    )
    result = request("POST", "/releases", {
        "tag_name": tag, "target_commitish": sha,
        "name": f"LRCGET {version} for Unraid",
        "body": body, "draft": False, "prerelease": False,
        "make_latest": "true" if make_latest else "false",
    })
    print(f"Published {result['html_url']}")
    return result


def github_request(repository, token, method, path, payload=None):
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json",
                 "User-Agent": "lrcget-unraid-release-publisher"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if method == "GET" and error.code == 404:
            return None
        raise


if __name__ == "__main__":
    repository = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GH_TOKEN"]
    publish(os.environ["PUBLISHED_VERSION"], os.environ["GITHUB_SHA"],
            repository, os.environ["GITHUB_RUN_ID"],
            lambda method, path, payload=None: github_request(repository, token, method, path, payload))
