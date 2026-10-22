# Core contract and review boundary

## Inputs

`schemas/evidence.schema.json` describes one asserted meeting window with sources and stable utterance IDs. ISO timestamps must have timezones. Sources and utterances share a unique ID namespace. Human `boundary_reviewed` and `adjacent_sources_checked` must both be true; these are attestations, not verified completeness. Exclusions and non-overlapping capture gaps are explicit. Unknown speakers require uncertainty disclosure. No utterance may fall outside the window or intersect a gap. Only canonical JSON is accepted (not audio, VTT, Word or platform URLs).

`schemas/draft.schema.json` describes model/human synthesis: a messaging spine (`summary`), classified ledger (`items`), caveats and review. Every claim needs exact nonempty quote refs. Owners and deadlines need their own refs or literal `unknown` with empty respective arrays. Refs establish pointers, **not semantic entailment**. The human must determine whether speaker labels and attribution support an owner, a deadline or corporate authority.

## Classification

- `ratified_decision`: human-confirmed authority after evidence review; never initial model ratification.
- `apparent_agreement`: transcript agreement, not formal authorization.
- `aligned_direction`: shared direction without a binding decision.
- `proposal`: something suggested, not approved.
- `reported_current`: current-state claim reported by a participant, not independently verified.
- `context`: background, including unverified external claims.
- `committed_action`: supported participant commitment, not task activation.
- `editorial_action`: suggested follow-up, not a participant commitment.
- `open_question`: unresolved issue, not an inferred answer.

## Operations

| Primitive | CLI | REST/tool payload | Result |
|---|---|---|---|
| ingest | `ingest SOURCE --out NEW_DIR` | `{evidence}` | Canonical evidence + source manifest |
| validate | `validate SOURCE DRAFT` | `{evidence,draft}` | Structure and exact-anchor checks |
| render | `render SOURCE DRAFT --out ROOT` | `{evidence,draft}` | Restricted preview HTML + non-activated CSV |

REST paths: POST `/ingest`, `/validate`, `/render`. GET `/health` requires the same bearer auth. OpenAI names: `rock_ingest`, `rock_validate`, `rock_render`. No release, send, publish or task-activation tool exists. REST is stateless/in-memory; ingest there hashes canonical serialization, not original HTTP body/upstream export bytes.

CLI `ingest` and `render` retain supplied input JSON bytes. Edition output contains `original.json`, `canonical.json`, `source-manifest.json`, `draft.json`, `recap.html`, `actions.csv`, `artifact-manifest.json`. These include private evidence; restrict the entire folder. Recap includes quote excerpts but not the full transcript. Artifact manifest hashes the six other files. Hashes establish byte integrity only.

## Human release (local, manual only)

1. Inspect full evidence, boundaries, gaps, identities, each claim/anchor, authority, owners/timing, missing context, consent and sensitive content. Exact substrings can still be misleading.
2. A named human—not the model—edits review to `evidence_reviewed: true`, `release_approved: true`, with their name and timezone-aware ISO `approved_at`. These local values are attestations, **not authenticated identity or RBAC**.
3. Increase edition when revising. Validate again. Example operator command:
   `python3 -m rocknote render private/meeting.json private/human-reviewed-draft.json --out artifacts/approved --release`
4. Verify the output says approved local artifact, not published. Distribution requires a separate approved human channel. Production requires an independent approval system; do not let an agent with unrestricted terminal access impersonate this manual gate.

No success message means semantic approval. Models must leave approval fields false/unknown. Syntax-only schemas cannot encode every cross-field/window/reference invariant; `rocknote.core` is the authoritative semantic-constraint validator (but not a semantic synthesis verifier).
