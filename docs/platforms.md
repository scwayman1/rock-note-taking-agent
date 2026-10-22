# Platform chooser and installation boundary

All paths below use the same local Python core. The CLI runs without installing a package. Install runtimes independently from their official documentation. `python3 -m rocknote setup --platform PLATFORM` is a **read-only report**, not auto-installation. No platform config was changed by this kit's build.

## Hermes

1. Clone/review this private repository in a location available to Hermes's execution backend; install/configure Hermes independently.
2. Copy `adapters/hermes/rock-note-taking/SKILL.md` into `skills/rock-note-taking/SKILL.md` under the **intended active Hermes home** (`$HERMES_HOME` if set, otherwise the selected profile home; default `~/.hermes`). Do not modify other profiles. This is an explicit operator copy, not an installer fetching a private URL.
3. Start a new session; check `hermes skills list` and ask it to load `rock-note-taking`. Supply the reviewed repo path; copied skills do not include the repo or its Python code.
4. Ask for the synthetic workflow first. Permit only approved local reads/writes and CLI commands. The model drafts; the core validates and renders. Human release stays outside the model workflow.
5. Record runtime/model versions, provider processing approval and synthetic output review in the worksheet. A skill present on disk does not prove model compliance or integration.

Official references: https://hermes-agent.nousresearch.com/docs/guides/work-with-skills and https://hermes-agent.nousresearch.com/docs/user-guide/features/skills . Skill discovery and local CLI were not exercised together in an agent session during this build.

## OpenClaw

1. Install/configure OpenClaw independently; select the intended agent workspace, not a global/shared workspace by accident.
2. Copy `adapters/openclaw/rock-note-taking/SKILL.md` into `<workspace>/skills/rock-note-taking/SKILL.md`.
3. Make the reviewed repo available inside its execution/sandbox filesystem. Start a fresh session, confirm the skill is discovered and give the repo location. A host path alone may not be available to a sandbox.
4. Run synthetic evidence/draft validation and render through the skill. Keep provider, files, tool permissions and review controls scoped to the pilot.

Official reference: https://docs.openclaw.ai/tools/skills . Workspace skills are an explicit discovery path; a repository URL is not an install. Live OpenClaw discovery and execution are **untested** here.

## Microsoft Copilot Studio / Teams

Use [the Copilot guide](../adapters/copilot/README.md). The shipped Swagger 2 JSON describes the actual local endpoints/auth. A cloud agent cannot call this machine's `127.0.0.1`. An approved hosted HTTPS service with organizational authentication/authorization must be implemented before remote synthetic testing. Do not solve the gap by exposing the dev server. Teams publishing is a later tenant/admin-controlled step, not a GitHub action.

## OpenAI

Use [the OpenAI guide](../adapters/openai/README.md). Function declarations do not execute themselves; the application must route each approved function call to the local bridge and return its output. The kit does not make API calls or bundle an SDK. Live model/API behavior is **untested**.

## What choosing a platform does not solve

Recording consent; transcript rights; canonical export conversion; organizational authority; semantic correctness; identities/roles; retention/deletion; provider costs and regional processing; approved hosting; auditability; Teams app policy. Complete the group worksheet and retain acceptance evidence before moving from synthetic to real data.
