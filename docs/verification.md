# Verification scope · v0.1

Run the commands below from the repo root. The build's recorded local verification date is October 22, 2026. No production/tenant/model acceptance is implied.

```sh
python3 scripts/build_contracts.py
python3 scripts/build_worksheet.py
python3 -m unittest discover -s tests -v
python3 -m rocknote setup --platform copilot
python3 -m rocknote demo --out artifacts/verification-demo
python3 scripts/security_scan.py
```

Tests exercise real subprocess CLI and manual OpenAI executor, in-process core and actual loopback HTTP requests (not mocked network responses). Coverage includes boundaries/gaps, hashes/original bytes, reference integrity, unsupported owner/deadline, ratification/release gates, HTML/CSV escaping, immutable edition paths, bearer authentication, payload bounds and public-bind denial. The checked-in sample draft is authored synthetic expected output, not a claimed model result.

Generated contracts share one builder; artifact tests validate fixtures, tool names, route/auth alignment, skill structure and companion byte hashes. Static security scanning is bounded to repository files, excluding .git and ignored generated/private/runtime files. It checks common credential formats and machine-local paths, not all possible secrets, PII or vulnerabilities. Test token strings are labeled synthetic. Do not equate a clean scan with a professional audit.

## Not tested / not implemented

- Live Hermes/OpenClaw skill discovery + model behavior.
- Live OpenAI schema acceptance, Responses integration, inference or account configuration.
- Copilot Studio tenant import/auth/tool invocation, hosted HTTPS/Entra access controls, Teams publishing, app approval or user pilot.
- Audio/ASR, Teams/Graph transcript ingestion, automated export conversion, tenant/user identity, durable shared storage, audit/retention/deletion enforcement or distribution.
- Semantic entailment, real-world authority, consent, data completeness or model prompt-injection resistance beyond instructions and structural boundaries.

These remain worksheet acceptance gates, not hidden prerequisites that the demo pretends to satisfy. No external deployment, collaborator invite or platform installation is performed.
