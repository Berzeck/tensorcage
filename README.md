# TensorCage

**Host-level containment for dedicated Bittensor environments**

TensorCage applies a default-deny network policy, controlled DNS resolution,
native SOCKS routing, pinned time synchronization, managed-file integrity, and
hash-locked Bittensor dependency installation.

## Release status

Current application version: **2.0.3**

Validated platform: **openSUSE Leap 16.0 x86_64 only.**

No other operating system or openSUSE release is currently claimed as
supported or validated.

## Intended environment

TensorCage is intended for a dedicated, minimal-purpose wallet, validator, or
Bittensor operations host.

It is not intended for:

- a general desktop;
- normal web browsing;
- a multi-purpose server;
- an environment requiring unrestricted outbound connectivity;
- a host without tested recovery or out-of-band administrative access.

Enabling TensorCage applies restrictive containment. Maintain a tested recovery
path before installation or lifecycle changes.

## Security model

TensorCage is designed to reduce exposure to:

- network-based data exfiltration;
- unrestricted DNS resolution;
- unintended outbound connections;
- dependency substitution during Bittensor installation;
- silent drift in integrity-managed configuration;
- accidental weakening of firewall containment.

A SHA-256 lock proves artifact identity and reproducibility. It does not prove
that an upstream package is free from vulnerabilities. Vulnerability scanning,
SBOM generation, provenance recording, and offline signing remain separate
planned security milestones.

## Installation

From a reviewed repository checkout:

~~~bash
chmod 0755 tensorcage
sudo ./tensorcage install
~~~

A successful installation immediately enables containment.

Verify the installed state:

~~~bash
sudo /usr/local/bin/tensorcage status
sudo /usr/local/bin/tensorcage doctor
sudo /usr/local/bin/tensorcage info
~~~

Expected healthy status includes:

~~~text
Installed: YES
Enabled:   YES
Healthy:   YES
Integrity: PASS
~~~

## Public command reference

Only these commands are part of the supported public interface.

| Command | Purpose |
|---|---|
| `tensorcage install` | Perform a fresh installation and immediately enable containment |
| `tensorcage enable` | Reapply containment and validate the enabled state |
| `tensorcage disable [--dry-run]` | Enter maintenance mode while retaining TensorCage and Bittensor |
| `tensorcage status` | Report installation, enablement, health, and integrity |
| `tensorcage lock-create bittensor=<version> output=<path>` | Create a complete hash-locked Bittensor dependency manifest |
| `tensorcage lock-verify bittensor=<version> lock=<path> lock_hash=<sha256>` | Validate an approved lock without installation |
| `tensorcage update bittensor=<version> lock=<path> lock_hash=<sha256>` | Install only the wheel set authorized by the validated lock |
| `tensorcage doctor` | Run deep, read-only validation of enabled security components |
| `tensorcage info` | Show runtime, policy, integrity, and activity information |
| `tensorcage uninstall [--dry-run]` | Remove TensorCage application/runtime state while preserving wallets |
| `tensorcage help` | Display the supported public command interface |
| `tensorcage version` | Display application and internal format versions |

Underscore-prefixed compatibility aliases are unsupported implementation
details. Do not use them in operator documentation or automation.

## Hash-locked Bittensor installation

Create a complete lock:

~~~bash
tensorcage lock-create bittensor=11.0.1 output=./bittensor-11.0.1-cp313-linux-x86_64.lock
~~~

Record its SHA-256:

~~~bash
sha256sum ./bittensor-11.0.1-cp313-linux-x86_64.lock
~~~

Validate the exact lock without installation:

~~~bash
sudo /usr/local/bin/tensorcage lock-verify bittensor=11.0.1 lock=./bittensor-11.0.1-cp313-linux-x86_64.lock lock_hash=<sha256-of-lock-file>
~~~

Install only the locked wheel set:

~~~bash
sudo /usr/local/bin/tensorcage update bittensor=11.0.1 lock=./bittensor-11.0.1-cp313-linux-x86_64.lock lock_hash=<sha256-of-lock-file>
~~~

Do not substitute partial package hashes or manually selected direct
dependencies for a complete generated lock.

## Lifecycle operations

Inspect maintenance disablement:

~~~bash
sudo /usr/local/bin/tensorcage disable --dry-run
~~~

Enter maintenance mode:

~~~bash
sudo /usr/local/bin/tensorcage disable
~~~

Re-enable and validate containment:

~~~bash
sudo /usr/local/bin/tensorcage enable
sudo /usr/local/bin/tensorcage status
sudo /usr/local/bin/tensorcage doctor
~~~

Inspect uninstall behavior:

~~~bash
sudo /usr/local/bin/tensorcage uninstall --dry-run
~~~

Perform uninstall:

~~~bash
sudo /usr/local/bin/tensorcage uninstall
~~~

The current release does not implement `uninstall --purge`.

User wallets under `~/.bittensor/wallets` are preserved. Review the detailed
installation-layout document for exact handling of managed configuration,
rollback state, adjacent backups, packages, and external configuration.

<!-- BEGIN TENSORCAGE INSTALLATION LAYOUT -->

## Installed filesystem layout

TensorCage separates installed programs, integrity-managed configuration,
persistent security state, transient runtime files, and preserved wallet data.

| Path | Purpose |
|---|---|
| `/usr/local/bin/tensorcage` | Main lifecycle and diagnostic command |
| `/usr/local/bin/btc` | Bittensor CLI wrapper using native SOCKS transport |
| `/usr/local/sbin/tensorcage-nft-apply` | Root-only nftables containment loader |
| `/opt/tensorcage/venv/` | Root-managed Python and Bittensor runtime |
| `/var/lib/tensorcage/` | Root-private lifecycle, integrity, and rollback state |
| `/etc/unbound/unbound.conf` | Managed local DNS resolver configuration |
| `/etc/unbound/allowlist/domains.conf` | Managed DNS policy |
| `/etc/sockd.conf` | Managed Dante SOCKS server configuration |
| `/etc/socks.conf` | Managed native SOCKS client routing |
| `/etc/chrony.conf` | Managed pinned time-source configuration |
| `/etc/systemd/system/tensorcage-nft.service` | Persistent nftables containment unit |

TensorCage verifies nine regular, non-symbolic-link managed files through
`/var/lib/tensorcage/managed-configs.v2.tsv`. Runtime material under `/run` is
transient. User wallets under `~/.bittensor/wallets` are preserved and are not
owned, inventoried, or removed by TensorCage.

The complete path inventory, ownership and modes, rollback contents, systemd
integration, external configuration effects, disable behavior, and uninstall
behavior are documented in
[`docs/installation-layout.md`](docs/installation-layout.md).

<!-- END TENSORCAGE INSTALLATION LAYOUT -->

## Release documentation

- [TensorCage 2.0.3 release notes](docs/releases/2.0.3.md)
- [Detailed installation layout](docs/installation-layout.md)

## Repository validation

Run the complete documentation regression suite without generating bytecode:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
~~~

Validate Bash syntax and whitespace:

~~~bash
bash -n tensorcage
git diff --check
~~~
