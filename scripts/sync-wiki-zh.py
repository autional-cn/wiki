#!/usr/bin/env python3
"""Sync Chinese API wiki HTML from the AuthMS monorepo into this portal.

Source (generated in the monorepo):
    cd D:\\go\\auth_ms_new
    python scripts/generate/generate_api_wiki.py --html

This script then normalizes the generator's hardcoded URLs/branding for the
`.cn` portal and copies the result to `public/wiki/api/`.

Usage:
    python scripts/sync-wiki-zh.py
"""

import os
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

AUTH_WIKI = r"D:\go\auth_ms_new\document\generated\wiki\html"
PORTAL_WIKI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "wiki", "api")

REPLACEMENTS = [
    # Spec download links (generator emits a path without file extension)
    (re.compile(r"https://iam\.tianv\.com/docs/specs/([a-z0-9-]+)"), r"https://reference.autional.cn/specs/\1.json"),
    # Scalar explorer deep links
    (re.compile(r"https://iam\.tianv\.com/docs/([a-z0-9-]+)"), r"https://reference.autional.cn/\1/"),
    (re.compile(r"https://iam\.tianv\.com/docs/"), "https://reference.autional.cn/"),
    # Portal hosts
    ("https://wiki.iam.tianv.com", "https://wiki.autional.cn"),
    ("https://iam.tianv.com", "https://www.autional.cn"),
    ("iam.tianv.com →", "www.autional.cn →"),
    ("iam.tianv.com", "www.autional.cn"),
    # Generator bug: `docs.autional.com/referenceX` / `.../referencespecs/` are
    # malformed; they belong to the reference portal.
    (re.compile(r"https://docs\.autional\.com/reference([a-z])"), r"https://reference.autional.cn/\1"),
    ("https://docs.autional.com/referencespecs/", "https://reference.autional.cn/specs/"),
    ('"https://docs.autional.com/reference"', '"https://reference.autional.cn"'),
    # Any remaining `.com` hosts -> `.cn`
    (re.compile(r"https://(?:(docs|reference|wiki|developer|demos)\.)?autional\.com"), r"https://\1.autional.cn"),
    ("https://autional.cn", "https://www.autional.cn"),
    # Branding
    ("AuthMS", "Autional"),
    # The generator emits legacy `/api/...` paths; the portal serves the same
    # pages at clean root paths (see src/pages/[service].astro, [...slug].astro).
    ('href="/api/', 'href="/'),
    ("https://wiki.autional.cn/api/", "https://wiki.autional.cn/"),
]


# A quote right after `href="/` means a replacement ate the closing quote and
# left the rest of the URL as stray text (see the `href="/api/` rule above).
MALFORMED_HREF = re.compile(r'href="/"[A-Za-z]')


def normalize(content: str) -> str:
    for old, new in REPLACEMENTS:
        if isinstance(old, re.Pattern):
            content = old.sub(new, content)
        else:
            content = content.replace(old, new)
    return content


def main() -> int:
    if not os.path.isdir(AUTH_WIKI):
        print(f"ERROR: source not found: {AUTH_WIKI}")
        print("Run first: python scripts/generate/generate_api_wiki.py --html")
        return 1

    os.makedirs(PORTAL_WIKI, exist_ok=True)

    copied = 0
    written = set()

    for root, _dirs, files in os.walk(AUTH_WIKI):
        # The generator nests everything under `api/`; the portal root is already
        # `public/wiki/api`, so that segment must be dropped (not doubled).
        rel = os.path.relpath(root, AUTH_WIKI)
        parts = [] if rel == "." else rel.split(os.sep)
        if parts[:1] == ["api"]:
            parts = parts[1:]
        rel = os.path.join(*parts) if parts else "."
        dst_dir = PORTAL_WIKI if rel == "." else os.path.join(PORTAL_WIKI, rel)
        os.makedirs(dst_dir, exist_ok=True)

        for name in files:
            if not (name.endswith(".html") or name.endswith(".xml")):
                continue
            src = os.path.join(root, name)
            dst = os.path.join(dst_dir, name)
            with open(src, encoding="utf-8") as fh:
                content = normalize(fh.read())
            if MALFORMED_HREF.search(content):
                print(f"ERROR: malformed href remains after normalization: {src}")
                return 1
            with open(dst, "w", encoding="utf-8", newline="") as fh:
                fh.write(content)
            written.add(os.path.normcase(os.path.normpath(dst)))
            copied += 1

    removed = 0
    for root, _dirs, files in os.walk(PORTAL_WIKI, topdown=False):
        for name in files:
            if not (name.endswith(".html") or name.endswith(".xml")):
                continue
            path = os.path.normcase(os.path.normpath(os.path.join(root, name)))
            if path not in written:
                os.remove(path)
                removed += 1
        if root != PORTAL_WIKI and not os.listdir(root):
            os.rmdir(root)

    print(f"synced {copied} files, removed {removed} stale -> {PORTAL_WIKI}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
