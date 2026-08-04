from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
SOURCE_PATH = ROOT / "tensorcage"

EXPECTED_COMMANDS = {
    "install",
    "enable",
    "disable",
    "status",
    "lock-create",
    "lock-verify",
    "update",
    "doctor",
    "info",
    "uninstall",
    "help",
    "version",
}


class ReadmePublicContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.readme = README_PATH.read_text(encoding="utf-8")
        cls.source = SOURCE_PATH.read_text(encoding="utf-8")

        result = subprocess.run(
            [str(SOURCE_PATH), "help"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "tensorcage help failed: "
                + result.stdout
                + result.stderr
            )

        cls.help_output = result.stdout

    def test_source_platform_contract_is_only_leap_16(self) -> None:
        source_lines = set(self.source.splitlines())

        self.assertIn(
            'SUPPORTED_OPENSUSE_RELS=("16.0")',
            source_lines,
        )
        self.assertIn(
            'TESTED_OPENSUSE_REL="16.0"',
            source_lines,
        )
        self.assertNotIn("15.6", self.source)
        self.assertIn(
            "TensorCage currently supports openSUSE Leap "
            "16.0 only.",
            self.source,
        )

    def test_readme_states_the_exact_validated_platform(self) -> None:
        self.assertIn(
            "Validated platform: **openSUSE Leap 16.0 "
            "x86_64 only.**",
            self.readme,
        )
        self.assertNotIn("15.6", self.readme)
        self.assertNotIn("Leap 16.x", self.readme)
        self.assertNotIn("experimental", self.readme)

    def test_readme_documents_every_public_help_command(self) -> None:
        usage_section = self.help_output.split(
            "Usage:\n",
            1,
        )[1].split(
            "\n\nLifecycle:",
            1,
        )[0]

        actual_commands = {
            line.strip().split()[1]
            for line in usage_section.splitlines()
            if line.startswith("  tensorcage ")
        }

        self.assertEqual(actual_commands, EXPECTED_COMMANDS)

        for command in sorted(EXPECTED_COMMANDS):
            self.assertIn(
                f"| `tensorcage {command}",
                self.readme,
            )

    def test_readme_rejects_stale_or_internal_instructions(self) -> None:
        forbidden_text = (
            "btcli=9.20.0",
            "wallet=4.0.0",
            "wallet_hash=",
            "/etc/firewalld/direct.xml",
            "systemctl restart firewalld",
            "tensorcage _diff",
            "tensorcage _test",
            "tensorcage _selftest",
        )

        for text in forbidden_text:
            self.assertNotIn(text, self.readme)

    def test_readme_links_current_operational_documents(self) -> None:
        required_text = (
            "<!-- BEGIN TENSORCAGE INSTALLATION LAYOUT -->",
            "<!-- END TENSORCAGE INSTALLATION LAYOUT -->",
            "docs/installation-layout.md",
            "docs/releases/2.0.3.md",
            "/usr/local/bin/tensorcage",
            "/usr/local/bin/btc",
            "/usr/local/sbin/tensorcage-nft-apply",
            "/opt/tensorcage/venv/",
            "/var/lib/tensorcage/",
            "/etc/unbound/unbound.conf",
            "/etc/unbound/allowlist/domains.conf",
            "/etc/sockd.conf",
            "/etc/socks.conf",
            "/etc/chrony.conf",
            "/etc/systemd/system/tensorcage-nft.service",
        )

        for text in required_text:
            self.assertIn(text, self.readme)


if __name__ == "__main__":
    unittest.main()
