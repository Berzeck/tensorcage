# 🛡️ TensorCage

**Host-level containment for Bittensor environments**

TensorCage is a security-first hardening tool designed to protect `btcli` and wallet environments from **network-based data exfiltration, supply-chain attacks, and covert channels**.

It enforces a **default-deny network model**, strict DNS control, and a **deterministic update mechanism**.

---

## ⚠️ Important

TensorCage is designed to run in a:

- **Dedicated virtual machine**
- Minimal-purpose environment (wallet / validator only)

It is **NOT intended** for:

- general desktop usage
- browsing
- multi-purpose servers

---

## 🚀 Quick Start

```bash
chmod +x tensorcage

sudo ./tensorcage install
Secure Update
sudo ./tensorcage update \
  btcli=9.20.0 \
  wallet=4.0.0 \
  btcli_hash=<sha256> \
  wallet_hash=<sha256>


🧪 Testing Recommendation

For accurate testing:

use a fresh VM or snapshot
avoid mixing multiple versions

To reset firewall:

sudo rm -f /etc/firewalld/direct.xml
sudo systemctl restart firewalld

⚠️ Limitations
Only supports:
openSUSE Leap 15.6 (tested)
Leap 16.x (experimental)
Not suitable for:
multi-user systems
desktop environments

<!-- BEGIN TENSORCAGE INSTALLATION LAYOUT -->

## 📁 Installed filesystem layout

TensorCage separates installed programs, integrity-managed configuration,
persistent security state, transient runtime files, and preserved wallet
data.

| Path | Purpose |
|---|---|
| `/usr/local/bin/tensorcage` | Main TensorCage lifecycle and diagnostic command |
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
`/var/lib/tensorcage/managed-configs.v2.tsv`. Runtime material under
`/run` is transient. User wallets under `~/.bittensor/wallets` are
preserved and are not owned, inventoried, or removed by TensorCage.

The complete path inventory—including ownership, modes, persistence,
rollback contents, systemd integration, external configuration effects,
disable behavior, and uninstall behavior—is documented in
[`docs/installation-layout.md`](docs/installation-layout.md).

Useful integrity commands:

~~~bash
sudo /usr/local/bin/tensorcage status
sudo /usr/local/bin/tensorcage doctor
sudo /usr/local/bin/tensorcage _diff
~~~

Repository documentation regression check:

~~~bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
~~~

<!-- END TENSORCAGE INSTALLATION LAYOUT -->
