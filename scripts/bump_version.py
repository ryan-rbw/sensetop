#!/usr/bin/env python3
"""
Version bumping script for SenseTop.

Automatically updates version numbers across all project files following semantic versioning.

Usage:
    python scripts/bump_version.py major|minor|patch|<version>

Examples:
    python scripts/bump_version.py minor          # 0.1.0 -> 0.2.0
    python scripts/bump_version.py patch          # 0.1.0 -> 0.1.1
    python scripts/bump_version.py 1.0.0          # Explicit version
"""

import re
import sys
from pathlib import Path
from typing import Tuple


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse semantic version string to tuple."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    return tuple(int(x) for x in match.groups())


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple to string."""
    return f"{major}.{minor}.{patch}"


def bump_version(
    current: str, bump_type: str
) -> str:
    """Bump version based on type (major, minor, patch) or explicit version."""
    if bump_type in ("major", "minor", "patch"):
        major, minor, patch = parse_version(current)

        if bump_type == "major":
            return format_version(major + 1, 0, 0)
        elif bump_type == "minor":
            return format_version(major, minor + 1, 0)
        else:  # patch
            return format_version(major, minor, patch + 1)
    else:
        # Explicit version - validate format
        parse_version(bump_type)
        return bump_type


def update_file(file_path: Path, old_version: str, new_version: str) -> bool:
    """Update version in a file. Returns True if changed."""
    try:
        content = file_path.read_text(encoding="utf-8")
        new_content = content.replace(old_version, new_version)

        if content != new_content:
            file_path.write_text(new_content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    bump_type = sys.argv[1]
    project_root = Path(__file__).parent.parent

    # Files to update
    files_to_update = [
        project_root / "sensetop" / "__init__.py",
        project_root / "setup.py",
        project_root / "setup.cfg",
    ]

    # Read current version
    init_file = files_to_update[0]
    init_content = init_file.read_text(encoding="utf-8")
    match = re.search(r'__version__ = "([^"]+)"', init_content)
    if not match:
        print("Error: Could not find current version in sensetop/__init__.py")
        sys.exit(1)

    current_version = match.group(1)
    # Remove -dev suffix if present
    if current_version.endswith("-dev"):
        current_version = current_version[:-4]

    # Calculate new version
    try:
        new_version = bump_version(current_version, bump_type)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Bumping version: {current_version} -> {new_version}")

    # Update all files
    changed_files = []
    for file_path in files_to_update:
        if file_path.exists():
            if update_file(file_path, current_version, new_version):
                changed_files.append(file_path.name)
                print(f"✅ Updated {file_path.name}")
            else:
                print(f"⏭️  No changes needed in {file_path.name}")
        else:
            print(f"⚠️  File not found: {file_path}")

    if changed_files:
        print(f"\n✨ Version bumped successfully to {new_version}")
        print(f"\nNext steps:")
        print(f"1. Review changes: git diff")
        print(f"2. Commit: git commit -am 'Bump version to {new_version}'")
        print(f"3. Tag: git tag v{new_version}")
        print(f"4. Push: git push origin master && git push origin v{new_version}")
        sys.exit(0)
    else:
        print("No files were updated")
        sys.exit(1)


if __name__ == "__main__":
    main()
