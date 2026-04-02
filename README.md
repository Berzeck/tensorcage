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
