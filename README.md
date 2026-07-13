## Project #24 Preservation notice

Status: Fork / Legacy (`legacy` profile, Advisory enforcement). This repository is preserved for historical/reference value and is not presented as maintained, production-ready, secure, or suitable for new operational use.

Supersession: prefer the canonical upstream or maintained libraries for new work. Canonical/provenance note: upstream fork; preserve upstream compatibility and attribution. Upstream: https://github.com/hayleealyssalynanderson/CERMv2.git

License/provenance: No root LICENSE detected in this snapshot; verify upstream/subtree licensing before reuse or redistribution.

Security/private-data warning: Legacy Streamlit/notebook code is not hardened; do not expose it to untrusted networks or inputs without a security review. Do not add private loan books, counterparty identifiers, secrets, credentials, or non-public portfolio data.

Revival gates:
- Identify canonical upstream commit and reconcile fork divergence before runtime edits.
- Resolve license/provenance for code, CSV files, pickle/dump artifacts, and any derived portfolio data.
- Create a minimal reproducible public-synthetic dataset and oracle numerical checks before changing algorithms.
- Pin supported Python/dependency versions and add real tests before claiming active maintenance.
- Perform Streamlit/input/security review before any network-exposed demo.

See `AGENTS.md` and `docs/ARCHITECTURE.yaml` for the advisory preservation contract.

---

# CERMv2 -- StreamLit (Version 2)

Streamlit App can be found here -> amaltheafs-cerm_advanced-f2c913bc33b2/main/greenStreamlit.py

Installation:

pip install streamlit

streamlit run greenStreamlit.py
