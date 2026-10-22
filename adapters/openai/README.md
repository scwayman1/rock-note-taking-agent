# OpenAI Responses function bridge

**Working local executor; no SDK, inference call, API spend, hosted endpoint or live model test.** This is developer/application integration, not a ChatGPT auto-install or a GPT Action import.

`tools.json` contains Responses API function declarations (`type`, `name`, `description`, `strict`, `parameters`) for `rock_ingest`, `rock_validate`, `rock_render`. Each calls the same deterministic core as the CLI/REST bridge. `bridge.py` accepts one allowlisted name and bounded JSON arguments on stdin; it returns JSON on stdout, exit 2 on rejection. It never executes a supplied shell command or releases notes.

Offline example from repo root:

```sh
python3 adapters/openai/bridge.py rock_render < fixtures/render-request.json > artifacts/tool-preview.json
```

Create `artifacts/` first or run the README demo. Requests use JSON objects, not paths: `{evidence}` for ingest; `{evidence,draft}` for validate/render.

## Wire an application (explicit provider approval required)

1. Obtain account/model access and secure API credentials outside Git. Approve processing/retention and budget first. Consult the current official [function-calling guide](https://platform.openai.com/docs/guides/function-calling).
2. Send `tools.json` as the Responses `tools` array and `prompts/master.md` as application instructions. Provide only approved canonical evidence. The model, not this engine, drafts the JSON.
3. For each returned `function_call`, validate its name against the three-name allowlist, pass the raw arguments through the local executor, and retain the `call_id`. Never interpolate model text into a shell command.
4. Return a `function_call_output` with matching `call_id` and JSON output string. Preserve the response context/output items as required by the model/API; bound call count, payload size and runtime in the application. Repeat only within the operator's approved budget.
5. Keep initial review fields false/unknown. Present restricted preview for human source/authority/privacy review. No release function exists; approval cannot be delegated to model-generated flags.

Minimal **offline** execution fragment (the caller owns Responses networking):

```python
import subprocess, sys
ALLOWED = {'rock_ingest', 'rock_validate', 'rock_render'}
def execute_tool(name, arguments):
    if name not in ALLOWED:
        raise ValueError('Unknown tool')
    if len(arguments.encode('utf-8')) > 1048576:
        raise ValueError('Oversized arguments')
    result = subprocess.run(
        [sys.executable, 'adapters/openai/bridge.py', name],
        input=arguments, text=True, capture_output=True, timeout=15,
        check=False,
    )
    return result.stdout  # On nonzero status this is a bounded error JSON.
# {'type': 'function_call_output', 'call_id': call.call_id,
#  'output': execute_tool(call.name, call.arguments)}
```

This fragment must run in the reviewed repo root. Application authentication, output access controls, cost limits, response history, error handling and independent approval enforcement remain application responsibilities. Strict schemas improve shape, not semantic correctness or source trust. Validate real installed-model schema support with synthetic evidence before connecting real meetings. Official guide checked October 22, 2026; live API behavior remains untested.
