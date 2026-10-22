# Action-oriented sales pilot — scoping worksheet

**Proposed next phase · planning only · not authority to connect, write or send**

## 1. Product outcome, not another note generator

Use the meeting-assistant pilot as the proof point. Productize the path from evidence to useful, governed outcomes: reviewable follow-up, approved distribution, and verified records in business systems. The pilot was built in Hermes. A Microsoft-native implementation using Copilot Studio agents and Azure development is the proposed next phase, not an implemented runtime swap.

Candidate bounded loop: meeting evidence → canonical account/context record → proposed follow-up and system changes → named human approval → authorized execution → readback and audit. The existing repository implements local evidence validation/rendering, not this external-action loop.

Fill in: business sponsor ______; sales owner ______; integration owner ______; security/data approver ______; pilot users ______; one workflow ______; success measure and baseline ______; explicit exclusions ______.

## 2. Define the first action product

Choose ONE initial workflow. Prefer read-only context plus unsent drafts before any business-system write.

| Candidate | Intended output | Owner / acceptance evidence |
|---|---|---|
| Follow-up | Evidence-backed email or task draft; no automatic send | ______ |
| Distribution | Explicit audience, approved content and controlled share | ______ |
| Creatio record | Proposed account/contact match, meeting summary, activity or next step; exact object/fields must be confirmed | ______ |
| Salesloft handoff | Proposed activity/task or follow-up handoff; supported object and permissions must be verified | ______ |

Decide the authoritative system for each field. A summary is not a verified CRM update. An email draft is not a send. Creating a task must not implicitly enroll a person in a cadence or change opportunity stage.

## 3. Reusable foundation and integration contract

Keep the application and data definitions above the control-plane discussion. Identify canonical meeting, person, account, evidence, decision and action records; do not assume an existing company schema. Map each proposed write to exact source evidence and a reviewed before/after diff.

The proposed control plane governs approval, execution policy, versions and audit. Agent IT supplies approved context, system connectors, secrets, runtime and operational logs. Improvement loops use corrections, evaluation failures and verified outcomes to revise candidate skills before release.

Fill in: canonical version ______; source system/record IDs ______; identity matching and ambiguity rules ______; authoritative fields ______; conflict/staleness rule ______; approved connector/API/version ______; development/sandbox scope ______.

## 4. External-action release gates

| Gate | Required design / evidence | Owner / status |
|---|---|---|
| Identity and scope | Tenant/user/account-level authorization; least privilege; allowed objects and fields; separate read and write permissions | ______ |
| Approval | Exact action, recipients, record target and payload; named approver; expiry; reapproval after edits or stale context | ______ |
| Execution | Allowlisted gateway; unique action/idempotency key; bounded retries; rate-limit handling; no blind replay after uncertain result | ______ |
| Verification | Read back the exact external record or send result; distinguish accepted, delivered, failed and unknown | ______ |
| Audit and recovery | Correlation IDs, reviewed payload/version, outcome evidence, exception owner; supported compensation/rollback or explicit irreversible boundary | ______ |
| Privacy and operations | Data classification, retention/deletion, secret handling, monitoring, incident response and cost owner | ______ |

Current starter does not implement these production controls. A local reviewed flag is not durable organizational approval. Connector availability, licensing, object permissions and account configuration remain to be verified.

## 5. Progression and definition of completion

Gate A: synthetic records and negative tests. Gate B: approved read-only real-data pilot. Gate C: human-reviewed proposals with manual execution. Gate D: one tightly scoped, approved write path after gateway, audit and readback tests. Wider rollout is a separate decision.

Test wrong user/tenant/account, ambiguous person match, modified payload after approval, expired approval, duplicate request, timeout after commit, API rate-limit response, concurrent update, partial failure and unavailable readback. An uncertain result stays unresolved until reconciled; never display success merely because a request was sent.

Fill in: entry gate ______; actual test evidence ______; pilot acceptance ______; unresolved gaps ______; authorized release owner/date ______; disable/rollback owner ______; next checkpoint ______.

## 6. Decisions for Ted, Katie and Jill

Which sales workflow first? Who owns its outcome? Which system is authoritative? What can the agent read, propose or execute? Who approves each external effect? What evidence earns a larger pilot? Agree those boundaries before implementation.

Vendor discovery references, not account verification: Creatio OData overview https://academy.creatio.com/docs/developer/integrations_and_api/data_services/odata/overview ; Salesloft API basics https://developers.salesloft.com/docs/platform/api-basics/ . Verify the actual tenant/product version and permissions before choosing integration mechanisms.
