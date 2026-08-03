"""Regression tests for TensorCage installation-layout documentation."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPOSITORY / "tensorcage"
GITIGNORE_PATH = REPOSITORY / ".gitignore"
README_PATH = REPOSITORY / "README.md"
LAYOUT_PATH = REPOSITORY / "docs" / "installation-layout.md"
RELEASE_PATH = REPOSITORY / "docs" / "releases" / "2.0.3.md"

README_BEGIN = "<!-- BEGIN TENSORCAGE INSTALLATION LAYOUT -->"
README_END = "<!-- END TENSORCAGE INSTALLATION LAYOUT -->"

VALIDATION_COMMAND = (
    "PYTHONDONTWRITEBYTECODE=1 "
    "python3 -m unittest discover "
    "-s tests -p 'test_*.py' -v"
)

FUNCTION_START = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)\(\)[ \t]*\{[ \t]*$",
    re.MULTILINE,
)

REQUIRED_OPERATIONAL_PATHS = (
    "/opt/tensorcage/",
    "/opt/tensorcage/venv/",
    "/opt/tensorcage/venv/bin/python",
    "/opt/tensorcage/venv/bin/btcli",
    "/var/lib/tensorcage/",
    "/var/lib/tensorcage/managed-configs.v2.tsv",
    "/var/lib/tensorcage/lifecycle.state",
    "/var/lib/tensorcage/rollback/",
    "/var/lib/tensorcage/rollback/<UTC>-<reason>/",
    "/etc/systemd/system/sockd.service.d/override.conf",
    "/etc/systemd/system/unbound.service.d/runtime.conf",
    "/run/unbound/",
    "/run/unbound/unbound.pid",
    "/run/tensorcage.nft",
    "/run/tensorcage-maintenance.nft",
    "/etc/resolv.conf",
    "/etc/sysconfig/network/config",
    "/etc/zypp/zypp.conf",
    "/etc/pip.conf",
    "/etc/environment",
    "/etc/profile.d/proxy.sh",
    "/etc/profile.d/proxy.sh.disabled",
    "/etc/firewalld/direct.xml",
    "~/.bittensor/",
    "~/.bittensor/wallets/",
)

REQUIRED_PACKAGES = (
    "firewalld",
    "iptables",
    "nftables",
    "xtables-plugins",
    "dante-server",
    "dante",
    "unbound",
    "chrony",
)


def read_regular_utf8(path: Path) -> str:
    """Read a required regular non-symbolic-link UTF-8 file."""

    if not path.is_file() or path.is_symlink():
        raise AssertionError(
            f"Missing or unsafe regular file: {path}"
        )

    text = path.read_text(encoding="utf-8")

    if not text.endswith("\n"):
        raise AssertionError(
            f"File lacks a trailing newline: {path}"
        )

    return text


def extract_function(source: str, function_name: str) -> str:
    """Extract one top-level Bash function through the next function."""

    matches = list(FUNCTION_START.finditer(source))
    positions = [
        index
        for index, match in enumerate(matches)
        if match.group(1) == function_name
    ]

    if len(positions) != 1:
        raise AssertionError(
            f"Expected one {function_name} definition, "
            f"found {len(positions)}"
        )

    position = positions[0]
    start = matches[position].start()

    if position + 1 < len(matches):
        end = matches[position + 1].start()
    else:
        end = len(source)

    return source[start:end]


def extract_managed_paths(source: str) -> tuple[str, ...]:
    """Extract absolute paths emitted by managed_integrity_paths()."""

    block = extract_function(source, "managed_integrity_paths")
    paths = tuple(
        line.strip()
        for line in block.splitlines()
        if line.strip().startswith("/")
    )

    if not paths:
        raise AssertionError(
            "managed_integrity_paths() emitted no absolute paths"
        )

    return paths


def extract_heading_section(text: str, heading: str) -> str:
    """Extract one level-two Markdown section."""

    marker = f"{heading}\n"

    if text.count(marker) != 1:
        raise AssertionError(
            f"Expected one heading {heading!r}, "
            f"found {text.count(marker)}"
        )

    start = text.index(marker) + len(marker)
    remainder = text[start:]
    next_heading = re.search(
        r"^## [^\n]+\n",
        remainder,
        re.MULTILINE,
    )

    if next_heading is None:
        return remainder

    return remainder[: next_heading.start()]


def extract_markdown_table_paths(section: str) -> tuple[str, ...]:
    """Extract backticked paths from Markdown-table first cells."""

    paths: list[str] = []

    for line in section.splitlines():
        stripped = line.strip()

        if not stripped.startswith("|"):
            continue

        cells = [
            cell.strip()
            for cell in stripped.strip("|").split("|")
        ]

        if not cells:
            continue

        match = re.fullmatch(r"`([^`]+)`", cells[0])

        if match:
            paths.append(match.group(1))

    return tuple(paths)


class InstallationLayoutDocumentationTests(unittest.TestCase):
    """Validate source-to-document installation-layout invariants."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = read_regular_utf8(SCRIPT_PATH)
        cls.gitignore = read_regular_utf8(GITIGNORE_PATH)
        cls.readme = read_regular_utf8(README_PATH)
        cls.layout = read_regular_utf8(LAYOUT_PATH)
        cls.release = read_regular_utf8(RELEASE_PATH)
        cls.managed_paths = extract_managed_paths(cls.source)

    def test_source_managed_paths_are_unique(self) -> None:
        self.assertEqual(
            len(self.managed_paths),
            len(set(self.managed_paths)),
            "managed_integrity_paths() contains duplicate paths",
        )
        self.assertEqual(
            len(self.managed_paths),
            9,
            "The current policy is expected to manage nine files",
        )

    def test_detailed_integrity_table_matches_source_exactly(
        self,
    ) -> None:
        section = extract_heading_section(
            self.layout,
            "## Integrity-managed files",
        )
        documented = extract_markdown_table_paths(section)

        self.assertEqual(
            len(documented),
            len(set(documented)),
            "The detailed managed-path table contains duplicates",
        )
        self.assertEqual(
            set(documented),
            set(self.managed_paths),
            "The detailed managed-path table drifted from the source",
        )

    def test_readme_summary_covers_all_managed_paths(self) -> None:
        self.assertEqual(self.readme.count(README_BEGIN), 1)
        self.assertEqual(self.readme.count(README_END), 1)

        begin = self.readme.index(README_BEGIN)
        end = self.readme.index(README_END, begin)
        section = self.readme[begin:end]
        documented = set(extract_markdown_table_paths(section))

        self.assertTrue(
            set(self.managed_paths).issubset(documented),
            "The README summary omits an integrity-managed path",
        )
        self.assertIn(
            "docs/installation-layout.md",
            section,
        )

    def test_operational_path_inventory_is_present(self) -> None:
        for path in REQUIRED_OPERATIONAL_PATHS:
            with self.subTest(path=path):
                self.assertIn(path, self.layout)

    def test_required_package_inventory_is_present(self) -> None:
        for package in REQUIRED_PACKAGES:
            with self.subTest(package=package):
                self.assertIn(f"`{package}`", self.layout)

    def test_runtime_lifecycle_distinction_matches_source(
        self,
    ) -> None:
        baseline = extract_function(
            self.source,
            "baseline_setup",
        )

        self.assertNotIn(
            "/opt/tensorcage",
            baseline,
            "baseline_setup unexpectedly manages the Bittensor runtime",
        )
        self.assertIn(
            "/opt/tensorcage/venv/bin/btcli",
            self.source,
        )
        self.assertNotIn(
            "- prepares `/opt/tensorcage`;",
            self.layout,
        )
        self.assertIn(
            "Baseline `tensorcage install`\n"
            "does not by itself create that virtual environment.",
            self.layout,
        )

    def test_regression_check_is_discoverable(self) -> None:
        self.assertIn(VALIDATION_COMMAND, self.readme)
        self.assertIn(VALIDATION_COMMAND, self.layout)
        self.assertIn(
            "`tests/test_installation_layout.py`",
            self.release,
        )

    def test_python_bytecode_and_kde_metadata_are_ignored(
        self,
    ) -> None:
        ignore_entries = {
            line.strip()
            for line in self.gitignore.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }

        self.assertTrue(
            {
                ".directory",
                "__pycache__/",
                "*.py[cod]",
            }.issubset(ignore_entries)
        )


if __name__ == "__main__":
    unittest.main()
