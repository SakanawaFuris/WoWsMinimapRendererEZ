"""
CIビルド前にminimap_rendererのバージョンファイルを
renderer/versions/配下にダウンロードするスクリプト。
"""
import json
import pathlib
import urllib.request

import renderer

GITHUB_API_BASE = "https://api.github.com/repos/WoWs-Builder-Team/minimap_renderer"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/WoWs-Builder-Team/minimap_renderer/master"

versions_dir = pathlib.Path(renderer.__file__).parent / "versions"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "CI-build"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    data = json.loads(fetch(f"{GITHUB_API_BASE}/contents/src/renderer/versions"))
    remote_versions = [
        item["name"]
        for item in data
        if item["type"] == "dir" and item["name"][0].isdigit()
    ]

    print(f"Found {len(remote_versions)} versions: {remote_versions}")

    for version in remote_versions:
        print(f"  Downloading {version}...")
        base_path = f"src/renderer/versions/{version}"
        vdir = versions_dir / version
        (vdir / "layers").mkdir(parents=True, exist_ok=True)
        (vdir / "resources").mkdir(parents=True, exist_ok=True)

        (vdir / "__init__.py").write_bytes(
            fetch(f"{GITHUB_RAW_BASE}/{base_path}/__init__.py")
        )

        try:
            files = json.loads(fetch(f"{GITHUB_API_BASE}/contents/{base_path}/layers"))
            for f in files:
                if f["name"].endswith(".py"):
                    (vdir / "layers" / f["name"]).write_bytes(fetch(f["download_url"]))
        except Exception as e:
            print(f"    layers error: {e}")

        try:
            files = json.loads(fetch(f"{GITHUB_API_BASE}/contents/{base_path}/resources"))
            for f in files:
                (vdir / "resources" / f["name"]).write_bytes(fetch(f["download_url"]))
        except Exception as e:
            print(f"    resources error: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
