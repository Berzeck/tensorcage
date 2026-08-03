# TensorCage installation and filesystem layout

This document describes the files, directories, persistent state,
transient state, service integration, and externally managed system state
used by TensorCage.

The TensorCage source remains the implementation authority. In
particular, `managed_integrity_paths()` is the authoritative list of
integrity-managed files. This document is an operational and audit
reference, not an alternative configuration source.

## Path classifications

TensorCage paths are classified as:

1. **Installed program files** — TensorCage executables and wrappers.
2. **Integrity-managed files** — regular non-symbolic-link files recorded
   in the managed integrity manifest.
3. **Persistent state** — lifecycle state, integrity metadata, and
   rollback snapshots.
4. **Generated integration files** — systemd units and drop-ins created
   or reconciled by TensorCage but not all included in the integrity
   manifest.
5. **Externally modified system configuration** — package-owned files or
   service-managed state for which TensorCage manages only specific
   settings.
6. **Runtime-only state** — files under `/run` that are recreated and must
   not be treated as persistent backups.
7. **Preserved user data** — wallet data that TensorCage does not own or
   remove.

## Integrity-managed files

The following nine files are recorded in
`/var/lib/tensorcage/managed-configs.v2.tsv`.

The manifest records SHA-256, size, mode, owner, group, and path. A
symbolic link, missing file, metadata mismatch, or content mismatch
causes integrity verification to fail.

| Path | Purpose | Validated owner and mode |
|---|---|---|
| `/etc/unbound/unbound.conf` | Local validating DNS resolver configuration | `root:unbound 0640` |
| `/etc/unbound/allowlist/domains.conf` | TensorCage DNS destination policy | `root:root 0644` |
| `/etc/sockd.conf` | Local Dante SOCKS server configuration | `root:root 0600` |
| `/etc/socks.conf` | Native SOCKS client routing configuration | `root:root 0644` |
| `/etc/chrony.conf` | Pinned time-source configuration | `root:root 0644` |
| `/usr/local/bin/btc` | Native SOCKS-aware Bittensor wrapper | `root:root 0755` |
| `/usr/local/bin/tensorcage` | Main TensorCage executable | `root:root 0755` |
| `/usr/local/sbin/tensorcage-nft-apply` | Root-only nftables policy loader | `root:root 0700` |
| `/etc/systemd/system/tensorcage-nft.service` | Persistent nftables containment unit | `root:root 0644` |

Integrity-managed paths must be regular files and must not be symbolic
links.

## Installed program and Python runtime

| Path | Purpose | Persistence |
|---|---|---|
| `/usr/local/bin/tensorcage` | TensorCage CLI and lifecycle implementation | Persistent |
| `/usr/local/bin/btc` | Bittensor CLI wrapper | Persistent |
| `/usr/local/sbin/tensorcage-nft-apply` | nftables policy loader | Persistent |
| `/opt/tensorcage/` | TensorCage-managed application root | Persistent |
| `/opt/tensorcage/venv/` | Root-managed Python virtual environment | Persistent |
| `/opt/tensorcage/venv/bin/python` | Virtual-environment Python entry point | Persistent |
| `/opt/tensorcage/venv/bin/btcli` | Locked Bittensor CLI entry point | Persistent |

On the validated openSUSE Leap 16 reference host:

- `/opt/tensorcage`, its virtual environment, and its `bin` directory were
  `root:root 0755`;
- the virtual-environment Python entry point resolved to the system
  Python 3.13 interpreter;
- Python 3.13.14 and Bittensor 11.0.1 were installed;
- the environment contained 35 Python distributions, including
  `bittensor`, `python-socks`, and `websockets`.

Package versions inside the virtual environment are governed by the
approved TensorCage lock input. This document intentionally does not
duplicate every internal virtual-environment file.

## Persistent TensorCage state

| Path | Purpose | Expected owner and mode |
|---|---|---|
| `/var/lib/tensorcage/` | Root-private TensorCage state root | `root:root 0700` |
| `/var/lib/tensorcage/managed-configs.v2.tsv` | Managed-file integrity manifest | `root:root 0600` |
| `/var/lib/tensorcage/lifecycle.state` | Current lifecycle state such as `ENABLED` | `root:root 0600` |
| `/var/lib/tensorcage/rollback/` | Root-private rollback snapshot root | `root:root 0700` |
| `/var/lib/tensorcage/rollback/<UTC>-<reason>/` | One timestamped pre-operation snapshot | `root:root 0700` |
| `/var/lib/tensorcage/rollback/<UTC>-<reason>/files/` | Root-private copies of managed files | `root:root 0700` |
| `/var/lib/tensorcage/rollback/<UTC>-<reason>/firewalld-direct.rules` | Captured runtime direct-rule state | `root:root 0600` |
| `/var/lib/tensorcage/rollback/<UTC>-<reason>/tensorcage.nft` | Captured TensorCage nftables table | `root:root 0600` |

TensorCage 2.0.3 enforces both the state root and rollback root as
non-symbolic-link directories owned by `root:root` with mode `0700`.
Existing broader rollback-root metadata is normalized before a new
snapshot is written.

Snapshot creation also rejects an already existing timestamped
destination. Snapshot copies are made root-private; they are rollback and
forensic material, not user-editable configuration.

TensorCage currently creates rollback snapshots but does not expose a
general-purpose automatic snapshot-restoration command. Restoration must
be performed by a reviewed deployment or recovery procedure.

## Adjacent configuration backups

Before replacing selected existing files, TensorCage uses the following
backup naming convention:

~~~text
<original-path>.bak.YYYY-MM-DD-HHMMSS
~~~

These adjacent backups preserve the source file through `cp -a`. They are
not members of the managed integrity manifest and may remain after later
lifecycle operations for recovery or forensic review.

## Systemd integration

| Path or unit | Purpose | Integrity-managed |
|---|---|---:|
| `/etc/systemd/system/tensorcage-nft.service` | Loads persistent nftables containment | Yes |
| `/etc/systemd/system/sockd.service.d/override.conf` | Orders Dante after networking and enables restart-on-failure | No |
| `/etc/systemd/system/unbound.service.d/runtime.conf` | Defines Unbound runtime-directory creation | No |
| `firewalld.service` | Persistent IPv4 and IPv6 direct-rule backend | No |
| `sockd.service` | Local SOCKS server on loopback | No |
| `unbound.service` | Local DNS resolver on loopback | No |
| `chronyd.service` | Pinned time synchronization | No |
| `tensorcage-nft.service` | Independent nftables containment | Unit file is managed |

A healthy enabled installation expects all five services to be enabled
and active. `tensorcage-nft.service` is a one-shot unit and may report
`active (exited)` after loading its table.

## Runtime-only paths

These paths reside under `/run` and are transient:

| Path | Purpose |
|---|---|
| `/run/unbound/` | Unbound runtime directory |
| `/run/unbound/unbound.pid` | Unbound process identifier |
| `/run/tensorcage.nft` | Generated active nftables policy input |
| `/run/tensorcage-maintenance.nft` | Temporary maintenance-mode nftables policy input |

`/run` is normally backed by `tmpfs`. Its contents are recreated as
services and TensorCage lifecycle operations run. These files must not be
treated as persistent backup material.

## Externally modified system configuration

TensorCage modifies or relies on the following system-owned locations.
Except where explicitly listed in the nine-file integrity manifest,
TensorCage manages only the relevant values or service state rather than
claiming ownership of the complete file.

| Path or state | TensorCage effect |
|---|---|
| `/etc/resolv.conf` | Resolver output points to local DNS; on the reference host it is a netconfig-managed symbolic link |
| `/etc/sysconfig/network/config` | Sets static DNS policy and local resolver address |
| `/etc/zypp/zypp.conf` | Disables delta RPM use and may manage proxy-related settings |
| `/etc/pip.conf` | May contain a local SOCKS proxy entry during applicable lifecycle states |
| `/etc/environment` | May contain process proxy variables during applicable lifecycle states |
| `/etc/profile.d/proxy.sh` | Optional shell proxy integration |
| `/etc/profile.d/proxy.sh.disabled` | Preserved inactive profile integration |
| `/etc/firewalld/direct.xml` | Persistent direct-rule storage generated and maintained by firewalld |
| firewalld default zone | Set to `drop` while containment is enabled |
| firewalld direct rules | Persistent and runtime IPv4/IPv6 outbound policy |
| nftables table `inet tensorcage` | Independent outbound containment table |

The validated reference host contained 30 runtime and 30 permanent
firewalld direct rules. That count is tied to the current policy version
and is validation evidence, not a permanent compatibility promise for
every future policy version.

## System package dependencies

TensorCage installs or requires the following openSUSE packages:

- `firewalld`;
- `iptables`;
- `nftables`;
- `xtables-plugins`;
- `dante-server`;
- `dante`;
- `unbound`;
- `chrony`.

Package-owned files remain governed by the operating-system package
manager. TensorCage documents required packages rather than duplicating
every file shipped by each RPM.

## Preserved user data

The following user-controlled paths are outside TensorCage ownership:

| Path | Behavior |
|---|---|
| `~/.bittensor/` | Preserved during disable and uninstall |
| `~/.bittensor/wallets/` | Wallet and key root; never removed by TensorCage |

TensorCage does not include wallet files in its managed integrity
manifest or rollback snapshot set. Wallet ownership, permissions,
encryption, offline backup, and key custody remain the operator's
responsibility.

Inventory and diagnostic procedures must not enumerate wallet names,
wallet files, key material, or wallet contents unless a separate,
explicit security procedure requires it.

## Lifecycle behavior

### Install

The baseline `tensorcage install` lifecycle:

- installs required system packages;
- writes or reconciles the managed configurations;
- creates the local DNS, SOCKS, time, firewalld, and nftables integration;
- enables required services;
- creates or refreshes the managed integrity manifest.

The root-managed `/opt/tensorcage/venv` Python and Bittensor environment is
created or refreshed by the separate cryptographically locked Bittensor
runtime installation or update workflow. Baseline `tensorcage install`
does not by itself create that virtual environment.

### Enable

Enable:

- creates a pre-operation rollback snapshot;
- enables and reconciles required services;
- reapplies DNS, firewalld, and nftables containment;
- refreshes the managed integrity manifest;
- records the enabled lifecycle state.

### Disable

Disable removes active containment and boot hooks while preserving
important installation material.

It preserves:

- `/opt/tensorcage` and the installed Python environment;
- `/usr/local/bin/tensorcage`;
- `/usr/local/bin/btc`;
- `~/.bittensor` wallet and key data;
- inactive configuration files and adjacent backups for review or reuse.

It removes or disables:

- active TensorCage firewalld direct rules;
- the `inet tensorcage` nftables table;
- `/etc/systemd/system/tensorcage-nft.service`;
- `/usr/local/sbin/tensorcage-nft-apply`;
- the `sockd` systemd override;
- active local proxy integration;
- TensorCage service enablement where applicable.

### Uninstall

Uninstall removes:

- `/usr/local/bin/tensorcage`;
- `/usr/local/bin/btc`;
- `/usr/local/sbin/tensorcage-nft-apply`;
- `/etc/systemd/system/tensorcage-nft.service`;
- `/etc/systemd/system/sockd.service.d/`;
- `/opt/tensorcage/`;
- `/var/lib/tensorcage/`;
- active TensorCage firewall and nftables state.

Uninstall preserves `~/.bittensor` wallets and keys. Inactive
configuration and adjacent backup files may also remain for forensic
review and controlled reuse.

## Persistence and filesystem boundaries

On the validated openSUSE Leap 16 reference host:

- `/usr/local`, `/opt`, `/var`, `/etc`, and `/home` were persistent Btrfs
  locations or subvolumes;
- `/run` was a transient `tmpfs`;
- the exact Btrfs subvolume layout was host-specific.

TensorCage relies on the semantic distinction between persistent and
runtime locations, not on one mandatory filesystem or subvolume layout.

## Integrity and audit commands

~~~bash
sudo /usr/local/bin/tensorcage status
sudo /usr/local/bin/tensorcage doctor
sudo /usr/local/bin/tensorcage _diff
~~~

`status` reports installation, enablement, health, and integrity state.

`doctor` performs parser, service, listener, firewall, DNS, time,
Bittensor runtime, and managed-file checks.

`_diff` reports content or metadata differences between the current
managed files and the integrity manifest.

## Documentation maintenance rule

A change that adds, removes, renames, reclassifies, or changes the
ownership or mode of an installed path must update:

1. `managed_integrity_paths()` when the file is integrity-managed;
2. this document;
3. the concise README layout section;
4. the applicable release notes;
5. lifecycle and uninstall handling;
6. the repository regression test in
   `tests/test_installation_layout.py`.

Run the documentation regression check with:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
~~~

Documentation must distinguish normative TensorCage behavior from
host-specific observations.
