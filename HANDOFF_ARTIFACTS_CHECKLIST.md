Project DIAL — Handoff Artifacts Checklist

Purpose: Concrete list of artifacts to include in the Sovereign handoff package for the Vanguard Engine.

Core repository artifacts
- [ ] Smart contract sources (Solidity) — /contracts/
- [ ] Compiled ABIs & bytecode — /artifacts/contracts/
- [ ] Deployment manifests and migration scripts — /deployments/
- [ ] Etherscan verification snapshots and links

Off-chain & infra
- [ ] Reputation Oracle source — /oracle/
- [ ] Chainlink adapter config and logs — /oracle/chainlink/
- [ ] Serverless deployment manifests — cloud functions / cloud run records
- [ ] Cloud provider logs and invocation traces (Cloud Functions)

dApp & front-end
- [ ] Frontend source — /dapp/
- [ ] Build artifacts and hosting config — /dapp/build/
- [ ] Demo recording and interaction checklist — /demo/

Tests & CI
- [ ] Unit tests and fixtures — /tests/
- [ ] Integration test scripts and testnet run logs — /tests/integration/
- [ ] CI configuration and logs — /.github/workflows/ or CI provider

Security & audit
- [ ] Internal security review notes — /security/
- [ ] Static analysis results — /security/reports/
- [ ] External audit report (when available)
- [ ] Threat model doc and prioritized remediation backlog

Governance & tokenomics
- [ ] Token specification (DGT, DRT) — /tokenomics/
- [ ] Governance flow diagrams and state machine — /docs/diagrams/

Legal & compliance
- [ ] Preliminary legal memos — /legal/
- [ ] Jurisdictional notes and distribution constraints

Operational artifacts
- [ ] Runbooks for deployment/rollbacks — /ops/runbooks/
- [ ] Monitoring dashboards & alert rules — /ops/monitoring/
- [ ] Contact list & owner map — /ops/owners/

Meta
- [ ] Project decision package — `PROJECT_DIAL_DECISION_PACKAGE.md`
- [ ] Sprint 1 commercialization roadmap — `PROJECT_DIAL_SPRINT1_ROADMAP.md`
- [ ] Hephaestus bootstrap snippet & guide — `.vscode/HEPHAESTUS_BOOTSTRAP.code-snippets`, `HEPHAESTUS_BOOTSTRAP_GUIDE.md`

Notes:
- Populate each path with the exact files (or pointers to external logs/console pages) before handoff.
- For any sensitive data (keys/credentials), ensure they are NOT committed; provide secure transfer instructions instead.

