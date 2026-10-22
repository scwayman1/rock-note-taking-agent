# Rock Note Taking Agent · v0.1

## START HERE — choose your path

A portable, evidence-first meeting-note kit. **Local working starter, not a hosted service.** Python 3.9+; no runtime dependencies, model key, tenant, inference or paid API call required for the demo.

| I want to… | Start here | What is actually included |
|---|---|---|
| Try it now | Commands below | Synthetic evidence → validated draft → HTML/CSV and hash manifests |
| Use Hermes | [Platform setup](docs/platforms.md#hermes) | Reusable skill + shared local CLI |
| Use OpenClaw | [Platform setup](docs/platforms.md#openclaw) | Reusable skill + shared local CLI |
| Use OpenAI | [OpenAI bridge](adapters/openai/README.md) | Responses function definitions + allowlisted local executor; not inference |
| Use Microsoft Copilot Studio | [Copilot setup](adapters/copilot/README.md) | Swagger 2 JSON REST-tool contract; tenant/hosting work remains |
| Implement with a group | [Editable worksheet](docs/implementation-worksheet.md) · [Four-page PDF](docs/implementation-worksheet.pdf) · [Print HTML](docs/implementation-worksheet.html) | Owners, environment, approvals, pilot gates and rollback |
| See the approved PRC companion | [One-page PDF](docs/companion/PRC-Rock-Note-Taking-Agent.pdf) · [HTML](docs/companion/PRC-Rock-Note-Taking-Agent.html) | Exact approved companion; not implementation evidence |

Clone this private repo with an authorized account, then run **from its root**:

```sh
git clone https://github.com/scwayman1/rock-note-taking-agent.git
cd rock-note-taking-agent
python3 -m rocknote setup --platform local
python3 -m rocknote demo --out artifacts/demo-01
python3 -m unittest discover -s tests -v
```

Open `artifacts/demo-01/synthetic-rock-001/edition-0001/recap.html`. Run again with a new output directory: editions never overwrite. `artifacts/` is ignored. The demo uses an **authored synthetic expected draft**, not model-generated notes. No background server, provider connection or platform installation is started.

## How it works

```text
Approved meeting window + canonical evidence JSON
  → ingest: strict bounds, source IDs, gaps, SHA-256 manifest
  → model/human: semantic drafting using prompts/master.md + draft schema
  → validate: structure, exact quote anchors, unknown owner/deadline rules
  → human evidence/authority/privacy review
  → render: restricted HTML + non-activated action CSV + edition manifest
  → optional human CLI release to local artifact only (never sends)
```

The model provides synthesis. The deterministic engine does **not** summarize a transcript, verify that a quote entails a claim, establish authority, transcribe audio or identify speakers. All platforms share [canonical schemas](schemas/), [master prompt](prompts/master.md) and the same `ingest`, `validate`, `render` primitives. A skill is instructions, not a new runtime or security sandbox. A GitHub URL alone does **not** install this into any platform.

## Work a real draft (synthetic until governance is approved)

```sh
python3 -m rocknote ingest fixtures/meeting.json --out artifacts/import-01
python3 -m rocknote prompt fixtures/meeting.json > artifacts/model-prompt.txt
# Give this prompt only to an approved model/provider; save its JSON draft separately.
python3 -m rocknote validate fixtures/meeting.json fixtures/draft.json
python3 -m rocknote render fixtures/meeting.json fixtures/draft.json --out artifacts/review-01
```

The operator must first convert authorized exports to `schemas/evidence.schema.json`, attest the window/adjacent-source review and retain upstream originals separately. Native Teams, Graph, Bee and recording ingestion are **not implemented**. Unknown identity, capture gaps and exclusions remain visible. Use increasing editions for corrections; put cross-meeting follow-ups in new evidence, never invented memory.

`ratified_decision` requires a named human evidence-review record; apparent agreement is not a decision. Owner/deadline evidence is required or the value is `unknown`. Editorial suggestions remain distinct from participant commitments. Review instructions and release details: [Core contract](docs/core-contract.md).

## Local HTTP bridge (optional)

```sh
export ROCKNOTE_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
python3 -m rocknote serve --port 8765
```

Loopback only, 1 MiB input limit, full `Authorization: Bearer <token>` required; `.env` is **not automatically loaded**. See [SECURITY.md](SECURITY.md). **Never expose/port-forward this development server.** Hosted HTTPS + organizational identity, authorization and retention are separate implementation work.

## Maintain and verify

```sh
python3 scripts/build_contracts.py
python3 scripts/build_worksheet.py
python3 scripts/security_scan.py
python3 -m unittest discover -s tests -v
```

Generated files are committed so the kit works without build tooling. Rebuild from the canonical builder, not hand-edited platform schemas. [Verification record](docs/verification.md) distinguishes local checks from untested tenant/model integrations. Platform documentation was checked October 22, 2026; recheck before rollout. Private repository, **all rights reserved**; see [NOTICE](NOTICE). No PRC or platform trademark license is granted.
