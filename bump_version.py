#!/usr/bin/env python3
"""
bump_version.py — K1 EDB Knowledge Platform version bumper
=============================================================
Updates the version number consistently across all project files.

Usage:
  python3 bump_version.py                     # show current versions
  python3 bump_version.py patch               # bump patch: x.y.Z+1
  python3 bump_version.py minor               # bump minor: x.Y+1.0
  python3 bump_version.py major               # bump major: X+1.0.0
  python3 bump_version.py set 1.3.0           # set an explicit version
  python3 bump_version.py patch --dry-run     # preview changes only
  python3 bump_version.py patch --note "..."  # add custom CHANGELOG note
"""

import re
import json
import sys
import datetime
from pathlib import Path

# ─── Config ────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent

# Files and how to find/replace their version strings
# Each entry: (path, description, find_fn, replace_fn)
# find_fn(content) -> current_version_str or None
# replace_fn(content, new_ver) -> updated_content

def _html_find(content):
    m = re.search(r'("version"\s*:\s*")(\d+\.\d+\.\d+)(")', content)
    return m.group(2) if m else None

def _html_replace(content, new_ver):
    return re.sub(
        r'("version"\s*:\s*")(\d+\.\d+\.\d+)(")',
        lambda m: f'{m.group(1)}{new_ver}{m.group(3)}',
        content, count=1
    )

def _json_find(path):
    def fn(content):
        try:
            data = json.loads(content)
            return data.get("_meta", {}).get("version")
        except Exception:
            return None
    return fn

def _json_replace(path):
    def fn(content, new_ver):
        try:
            data = json.loads(content)
            today = datetime.date.today().isoformat()
            if "_meta" in data:
                data["_meta"]["version"] = new_ver
                if "updated" in data["_meta"]:
                    data["_meta"]["updated"] = today
            return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        except Exception:
            return content
    return fn

def _readme_find(content):
    m = re.search(r'version-v(\d+\.\d+\.\d+)-', content)
    return m.group(1) if m else None

def _readme_replace(content, new_ver):
    today = datetime.date.today().strftime("%Y-%m-%d")
    # 1. Update version badge
    content = re.sub(
        r'(version-v)(\d+\.\d+\.\d+)(-)',
        lambda m: f'{m.group(1)}{new_ver}{m.group(3)}',
        content
    )
    # 2. Update 最後更新 date at bottom
    content = re.sub(
        r'(\*最後更新：)[\d-]+(\s*\|)',
        lambda m: f'{m.group(1)}{today}{m.group(2)}',
        content
    )
    return content

def _changelog_find(content):
    m = re.search(r'## \[v?(\d+\.\d+\.\d+)\]', content)
    return m.group(1) if m else None

def _changelog_insert(content, new_ver, note):
    today = datetime.date.today().strftime("%Y-%m-%d")
    entry = f"\n## [v{new_ver}] — {today}\n\n### Changed\n- {note}\n\n---\n"
    # Insert after the header (first ---) or at line 6
    insert_after = "---\n"
    idx = content.find(insert_after)
    if idx == -1:
        return content + entry
    pos = idx + len(insert_after)
    return content[:pos] + entry + content[pos:]

# ─── File registry ─────────────────────────────────────────────────────────
FILES = [
    {
        "path": REPO_ROOT / "k1-dashboard.html",
        "label": "k1-dashboard.html (INITIAL_DATA._meta.version)",
        "find": _html_find,
        "replace": _html_replace,
    },
    {
        "path": REPO_ROOT / "dev" / "knowledge" / "role_facts.json",
        "label": "dev/knowledge/role_facts.json (_meta.version)",
        "find": _json_find("role_facts.json"),
        "replace": _json_replace("role_facts.json"),
    },
    {
        "path": REPO_ROOT / "knowledge.json",
        "label": "knowledge.json (_meta.version)",
        "find": _json_find("knowledge.json"),
        "replace": _json_replace("knowledge.json"),
    },
    {
        "path": REPO_ROOT / "guidelines.json",
        "label": "guidelines.json (_meta.version)",
        "find": _json_find("guidelines.json"),
        "replace": _json_replace("guidelines.json"),
    },
    {
        "path": REPO_ROOT / "README.md",
        "label": "README.md (version badge)",
        "find": _readme_find,
        "replace": _readme_replace,
    },
]

CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"

# ─── Helpers ───────────────────────────────────────────────────────────────

def bump(version_str, bump_type):
    parts = [int(x) for x in version_str.split(".")]
    if bump_type == "major":
        return f"{parts[0]+1}.0.0"
    elif bump_type == "minor":
        return f"{parts[0]}.{parts[1]+1}.0"
    elif bump_type == "patch":
        return f"{parts[0]}.{parts[1]}.{parts[2]+1}"
    else:
        raise ValueError(f"Unknown bump type: {bump_type}")

def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else None

def show_current():
    print("\n📋  Current version inventory:\n")
    versions = set()
    for f in FILES:
        content = read(f["path"])
        if content is None:
            print(f"  ⚠️  {f['label']}: FILE NOT FOUND")
            continue
        ver = f["find"](content)
        if ver:
            versions.add(ver)
            print(f"  ✓  {f['label']}: {ver}")
        else:
            print(f"  ⚠️  {f['label']}: version not detected")
    if CHANGELOG_PATH.exists():
        cl = read(CHANGELOG_PATH)
        cv = _changelog_find(cl)
        print(f"  ✓  CHANGELOG.md (latest entry): {cv or 'not found'}")

    if len(versions) > 1:
        print(f"\n  ⚠️  WARNING: version mismatch detected across files: {sorted(versions)}")
        print("  Run 'python3 bump_version.py set <version>' to unify first.")
    elif versions:
        print(f"\n  Current unified version: {next(iter(versions))}")
    print()

# ─── Main ──────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    note_idx = next((i for i, a in enumerate(args) if a == "--note"), None)
    note = args[note_idx + 1] if note_idx is not None and note_idx + 1 < len(args) else None
    if note_idx is not None:
        args = args[:note_idx] + args[note_idx + 2:]

    # No args — show current state
    if not args:
        show_current()
        print("Usage: python3 bump_version.py [patch|minor|major|set <version>] [--dry-run] [--note '...']")
        return

    bump_type = args[0]  # patch / minor / major / set

    # Determine new version
    if bump_type == "set":
        if len(args) < 2 or not re.match(r"^\d+\.\d+\.\d+$", args[1]):
            print("❌  Usage: python3 bump_version.py set <x.y.z>")
            sys.exit(1)
        new_ver = args[1]
        # Detect current from HTML (primary source for display)
        html_content = read(REPO_ROOT / "k1-dashboard.html")
        old_ver = _html_find(html_content) if html_content else "unknown"
    elif bump_type in ("patch", "minor", "major"):
        # Detect current version — use html as primary, fallback to first json
        html_content = read(REPO_ROOT / "k1-dashboard.html")
        old_ver = _html_find(html_content) if html_content else None
        if not old_ver:
            # Fallback: check role_facts.json
            rj = read(REPO_ROOT / "dev" / "knowledge" / "role_facts.json")
            if rj:
                old_ver = _json_find("role_facts.json")(rj)
        if not old_ver:
            print("❌  Cannot detect current version. Use 'set' to specify explicitly.")
            sys.exit(1)
        new_ver = bump(old_ver, bump_type)
    else:
        print(f"❌  Unknown command: {bump_type}")
        print("Usage: python3 bump_version.py [patch|minor|major|set <version>] [--dry-run] [--note '...']")
        sys.exit(1)

    if not note:
        note = f"版本 {old_ver} → {new_ver}"

    print(f"\n{'🔍 DRY RUN — ' if dry_run else ''}版本更新: {old_ver} → {new_ver}\n")

    # Process each file
    for f in FILES:
        content = read(f["path"])
        if content is None:
            print(f"  ⚠️  SKIP {f['label']} — file not found")
            continue
        old = f["find"](content)
        if old is None:
            print(f"  ⚠️  SKIP {f['label']} — version string not detected")
            continue
        new_content = f["replace"](content, new_ver)
        changed = new_content != content
        status = "✓ " if changed else "— (no change)"
        print(f"  {status} {f['label']}: {old} → {new_ver}")
        if not dry_run and changed:
            f["path"].write_text(new_content, encoding="utf-8")

    # CHANGELOG
    if CHANGELOG_PATH.exists():
        cl = read(CHANGELOG_PATH)
        new_cl = _changelog_insert(cl, new_ver, note)
        print(f"  ✓  CHANGELOG.md — insert [v{new_ver}] entry: \"{note}\"")
        if not dry_run:
            CHANGELOG_PATH.write_text(new_cl, encoding="utf-8")
    else:
        print("  ⚠️  SKIP CHANGELOG.md — file not found")

    if dry_run:
        print("\n🔍 Dry run complete — no files modified.\n")
        print(f"Run without --dry-run to apply changes:")
        print(f"  python3 bump_version.py {' '.join(sys.argv[1:]).replace(' --dry-run','')}\n")
    else:
        print(f"\n✅  Version bumped to {new_ver} across all files.\n")
        print("Next steps:")
        print(f"  cd ~/Downloads/Claude-edb-knowledge && git add k1-dashboard.html dev/knowledge/role_facts.json knowledge.json guidelines.json README.md CHANGELOG.md && git commit -m \"chore: bump version to v{new_ver}\" && git pull --rebase && git push origin main\n")

if __name__ == "__main__":
    main()
