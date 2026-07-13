# AGENTS.md — CERMv2

Purpose: Project #24 legacy preservation. This repository is classified as `Fork / Legacy` with `legacy` profile and Advisory enforcement. Do not make unsupported maturity, security, maintenance, or production-readiness claims.

Canonical docs:
- `README.md` root preservation notice
- `docs/ARCHITECTURE.yaml` machine-readable source of truth
- `docs/ARCHITECTURE.md` rationale and maintained-library/revival notes

Provenance and attribution:
- Origin owner: `googa27`; issue: https://github.com/googa27/arxiv-implementation-lab/issues/22
- Upstream/canonical reference: https://github.com/hayleealyssalynanderson/CERMv2.git
- Preserve history, existing public names, authorship, copyright notices, and file contents. Do not delete, rewrite, or hide inherited material in this preservation change.

Safety boundaries:
- License/provenance: No root LICENSE detected in this snapshot; verify upstream/subtree licensing before reuse or redistribution.
- Data posture: Legacy local CSV/pickle/dump files only; loan, climate, and portfolio data require source, license, classification, and lineage review before reuse.
- Private-data rule: Do not add private loan books, counterparty identifiers, secrets, credentials, or non-public portfolio data.
- Security/hardware warning: Legacy Streamlit/notebook code is not hardened; do not expose it to untrusted networks or inputs without a security review.

Exact commands:
- Setup: no supported automated setup is declared; treating runtime setup as a revival gate is required.
- Tests: no inherited runtime test suite is claimed; run the architecture checker only.
- Lint/format: no lint/format command is declared.
- Architecture: `python scripts/check_portfolio_architecture.py`

Implementation rules for future work:
- Research upstream/current maintained libraries, standards, datasets, licenses, and security posture before changing runtime code.
- Prefer maintained libraries; custom code must be limited to domain semantics, adapters, composition, or genuinely missing algorithms with oracle/reference tests.
- Avoid invasive refactors of inherited code. Record exact no-growth exceptions and compatibility risks before structural changes.
- Do not introduce generated caches, secrets, private identifiers, restricted data, or fabricated outputs.
- Keep AI-facing contracts deterministic and local. Add Hermes skills for recurring workflows only; plugin/MCP needs stable public contracts, measured multi-client need, least privilege, and separate verification.
- Human/notebook interface: Current Streamlit/notebook entry points may be documented as historical examples; typed package/API redesign only after independent revival.
- Core posture: No core coupling unless formally revived.

Revival gates:
- Identify canonical upstream commit and reconcile fork divergence before runtime edits.
- Resolve license/provenance for code, CSV files, pickle/dump artifacts, and any derived portfolio data.
- Create a minimal reproducible public-synthetic dataset and oracle numerical checks before changing algorithms.
- Pin supported Python/dependency versions and add real tests before claiming active maintenance.
- Perform Streamlit/input/security review before any network-exposed demo.

Definition of done for preservation edits:
- README, AGENTS, `docs/ARCHITECTURE.yaml`, `docs/ARCHITECTURE.md`, and tests agree.
- `python scripts/check_portfolio_architecture.py` passes.
- Only advisory governance files are changed unless a separate reviewed revival task authorizes runtime edits.
