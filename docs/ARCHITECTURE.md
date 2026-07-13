# Architecture — CERMv2

## Project #24 preservation profile

Source of truth: `docs/ARCHITECTURE.yaml`. Tracking issue: https://github.com/googa27/arxiv-implementation-lab/issues/22. Profile: `legacy`; enforcement: Advisory.

This repository is preserved as `Fork / Legacy`. The governance files are intentionally advisory and additive: they document provenance, risks, and revival gates without refactoring inherited code or claiming active maintenance.

## Archival, supersession, and provenance

- Archival notice: historical/reference preservation only; not production-ready, maintained, secure, or operationally validated.
- Supersession notice: prefer upstream or maintained libraries for new work.
- Canonical/provenance: upstream fork; preserve upstream compatibility and attribution
- Upstream: https://github.com/hayleealyssalynanderson/CERMv2.git
- License/provenance warning: No root LICENSE detected in this snapshot; verify upstream/subtree licensing before reuse or redistribution.
- Security/private-data warning: Legacy Streamlit/notebook code is not hardened; do not expose it to untrusted networks or inputs without a security review. Do not add private loan books, counterparty identifiers, secrets, credentials, or non-public portfolio data.

## Research-backed defaults

| Decision | Evidence | Repository application |
|---|---|---|
| Agent context | Hermes context files; AGENTS.md convention | Root `AGENTS.md`; progressive detail in this architecture document. |
| AI tool escalation | MCP tools specification | Stable local contracts first; no repo-specific plugin/MCP during preservation. |
| Python source layout | PyPA src-layout guidance | No forced migration for legacy/fork/hardware preservation. |
| Test layout | pytest good practices | Unit/integration/e2e/architecture directories exist; empty suites declare activation triggers. |
| Module budget | Pylint too-many-lines rationale plus AI review locality | 500-line default is a no-growth ratchet where runtime source roots are activated. |
| Evolution | Evolutionary architecture | Revival requires executable fitness functions and explicit exceptions. |
| Data layers | Medallion architecture | Applied only if revived with real data; current posture is advisory. |
| Python protocols | Python data model; NumPy dispatch | Dunders are not decoration; API/protocol redesign waits for revival. |

## Maintained-library decision table

| Capability | Selected route | Alternatives | Boundary / custom-code rule |
|---|---|---|---|
| numerical/dataframe runtime | NumPy, SciPy, pandas | Custom array/dataframe implementations | Keep adapters at script/API boundaries; validate numerical behavior against reference cases. |
| interactive UI | Streamlit after version/security review | Ad hoc web server or notebook-only UI | UI must remain read-only/demo until data custody and threat model are approved. |
| architecture bootstrap | Python standard-library json over JSON-subset YAML | Hand-written YAML parser | Dependency-free advisory gate only. |

## Data, security, and privacy posture

Legacy local CSV/pickle/dump files only; loan, climate, and portfolio data require source, license, classification, and lineage review before reuse.

Do not add private loan books, counterparty identifiers, secrets, credentials, or non-public portfolio data.

Legacy Streamlit/notebook code is not hardened; do not expose it to untrusted networks or inputs without a security review.

## AI and human interface

- AI interface: Minimal AGENTS with upstream-sync and safe-run guidance; no repo-specific MCP/plugin.
- Human/notebook interface: Current Streamlit/notebook entry points may be documented as historical examples; typed package/API redesign only after independent revival.
- Core posture: No core coupling unless formally revived.

## Revival gates

- Identify canonical upstream commit and reconcile fork divergence before runtime edits.
- Resolve license/provenance for code, CSV files, pickle/dump artifacts, and any derived portfolio data.
- Create a minimal reproducible public-synthetic dataset and oracle numerical checks before changing algorithms.
- Pin supported Python/dependency versions and add real tests before claiming active maintenance.
- Perform Streamlit/input/security review before any network-exposed demo.

## Research anchors

- https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files
- https://agents.md/
- https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- https://docs.pytest.org/en/stable/explanation/goodpractices.html
- https://docs.python.org/3/reference/datamodel.html
- https://numpy.org/doc/stable/user/basics.dispatch.html
- https://evolutionaryarchitecture.com/precis.html
- https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion
