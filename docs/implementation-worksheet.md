# Group implementation worksheet

**Rock Note Taking Agent v0.1 · editable working record · NOT authorization to go live**

Use one copy per environment/pilot. Keep completed copies, screenshots and sensitive identifiers in an approved restricted location, not this repository. Never enter passwords, tokens, transcript content or regulated data. Blank means **not verified**, never implicitly approved.

## 1. Ownership and decision record

| Field | Fill in |
|---|---|
| Group / project / meeting purpose | ____________________ |
| Business sponsor and accountable owner | ____________________ |
| Implementation lead / backup | ____________________ |
| Named evidence reviewer / release approver | ____________________ |
| Security, privacy and records approvers | ____________________ |
| Tenant admin / Power Platform admin / Teams app admin | ____________________ |
| Scope and explicit exclusions | ____________________ |
| Acceptance-evidence folder (restricted) | ____________________ |
| Review date / next gate / unresolved blockers | ____________________ |

## 2. Environment, licensing and budget

| Field | Fill in |
|---|---|
| Selected platform / installed runtime version | ____________________ |
| Repo approved commit / core and schema versions | ____________________ |
| Local sandbox, dev/test/prod boundaries | ____________________ |
| Microsoft tenant / environment / solution owner | ____________________ |
| Copilot Studio maker role / license / capacity confirmed by | ____________________ |
| Teams/Microsoft 365 availability / app policy owner | ____________________ |
| Model/provider / account / region / processing approval | ____________________ |
| Cost owner / budget / call limits / stop trigger | ____________________ |
| Who can use agent, read evidence, review, release | ____________________ |

## 3. Data and authorization controls

| Control | Owner / decision / evidence |
|---|---|
| Recording consent, transcript rights and approved ingestion window | ____________________ |
| Data classification and prohibited content | ____________________ |
| Source export location / canonical-conversion owner / originals retention | ____________________ |
| Adjacent-source review, exclusion and gap review | ____________________ |
| Provider processing / residency / subcontractor review | ____________________ |
| Evidence/draft/artifact access and sharing groups | ____________________ |
| Retention periods for originals, drafts, artifacts, logs and provider copies | ____________________ |
| Deletion owner, procedure, backup limits and verification evidence | ____________________ |
| DLP / audit logging / incident contact and escalation | ____________________ |
| Human authority and release workflow independent of model tool access | ____________________ |

## 4. Hosted HTTPS vs. local gap — STOP gate

The included server is loopback-only bearer-authenticated development code. It has no TLS, Entra validation, tenant/user RBAC, storage or production hardening. Cloud Copilot cannot call local 127.0.0.1. Never tunnel or expose it. This kit provisions no Cloudflare or Azure service; companion diagram context is not this repo's deployment evidence.

| Required for remote pilot | Owner / implemented design / evidence |
|---|---|
| Approved host, HTTPS certificate and network boundaries | ____________________ |
| Service implementation/hardening and operational ownership | ____________________ |
| Identity, meeting-scoped authorization, deny tests | ____________________ |
| Secret store, rotation and revocation | ____________________ |
| Request/rate/time bounds, output access and safe logs | ____________________ |
| Retention/deletion, monitoring, incidents and recovery | ____________________ |
| Deployed spec host/scheme/security matches actual service | ____________________ |
| Security approver authorizes remote synthetic-only testing | ____________________ |

## 5. Copilot tools and tenant setup (conditional)

- [ ] Maker/tenant/environment/solution/license confirmed by named admin.
- [ ] Current REST API tool preview suitability approved; if policy prohibits preview, STOP.
- [ ] Approved hosted HTTPS prerequisite complete; no local-dev tunneling.
- [ ] Deployment-specific Swagger 2 JSON import evidence saved; exact checksum recorded.
- [ ] Auth mechanism, secure connection and least-privilege identity verified.
- [ ] Only ingest/validate/render selected; model receives shared instructions/schema.
- [ ] Payload mapping and response display verified; HTML string is not assumed to be a Teams card.
- [ ] Wrong credentials, wrong tenant/user and wrong meeting denied by hosted service.
- [ ] Send/publish/task activation and model release remain unavailable.

Owner / result IDs / blockers: ____________________

## 6. Synthetic acceptance before real evidence

| Acceptance | Named tester / date / evidence / pass or fail |
|---|---|
| CLI setup, tests and demo on target machine | ____________________ |
| Source window, gap, unknown identity and original hashes preserved | ____________________ |
| Draft labels distinguish proposal, agreement, direction and ratification | ____________________ |
| Unsupported owner/deadline remain unknown; no reconstructed speech | ____________________ |
| Fabricated quote and unknown ref rejected | ____________________ |
| Preview escaped; CSV formula protection; sensitive output restricted | ____________________ |
| Unreviewed release rejected; named human review tested separately | ____________________ |
| Edition overwrite denied; prior artifacts and manifests retained | ____________________ |
| Selected runtime discovers skill/tools and invokes actual core | ____________________ |
| Live model/provider synthetic result reviewed for entailment and injection | ____________________ |
| Local vs hosted auth/network negative cases and output display | ____________________ |

## 7. Human release and restricted Teams pilot

- [ ] Evidence reviewer examined boundaries, all claim anchors, omissions and uncertainty.
- [ ] Authority owner confirmed decision labels; owners and timing reviewed without inference.
- [ ] Privacy reviewer approved exact output audience/content and retention.
- [ ] Independent named human release recorded with time/version and evidence location.
- [ ] Tenant operator published approved agent/version; Teams channel configured.
- [ ] Named pilot roster and access boundaries verified on actual user accounts.
- [ ] Organization catalog submission/admin approval/app policy recorded if applicable.
- [ ] Pilot users confirm correct invocation/output; no source-data over-sharing.
- [ ] Wider rollout is a separate explicit sponsor/security/admin decision.

Pilot owner / sponsor decision / approval evidence / date: ____________________

## 8. Version, rollback and final gate

| Field | Fill in |
|---|---|
| Accepted repo commit / schema / prompt / skill / tool versions | ____________________ |
| Hosted deployment and deployment-spec checksum | ____________________ |
| Copilot solution/agent published version and connection owner | ____________________ |
| Last-known-good version and restricted backups location | ____________________ |
| Rollback owner / disable access / revoke credentials procedure | ____________________ |
| Revert deployment + solution/agent + tool spec procedure | ____________________ |
| Synthetic retest after revert / prior notes remain immutable | ____________________ |
| Rollback drill evidence and recovery limitations | ____________________ |
| Final outcome: STOP / synthetic pilot only / real-data pilot approved | ____________________ |
| Named approvers, date and acceptance evidence | ____________________ |

**Definition of completion:** actual target-platform invocation and negative cases, independent human release, approved audience and retention, and rollback evidence—not a successful import, an install link, a private repo or a passing local demo alone.
