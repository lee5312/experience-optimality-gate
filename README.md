# EOG — Experience Optimality Gate

EOG is an experience-first engineering method for AI coding agents and humans. It makes the desired consumer experience the root objective, forces an actual search for existing solutions before new implementation, requires evidence for every residual novel part, and separates design readiness from observed completion.

EOG is not an agent, model, scheduler, task database, permission broker, or replacement runtime. It runs on the agent and tools you already use.

## The core loop

```text
consumer experience
        ↓
derived requirements + hard constraints
        ↓
actual existing-wheel search
        ↓
residual-gap justification
        ↓
lowest-burden viable option
        ↓
bounded implementation
        ↓
consumer-boundary verification
```

The important asymmetry is deliberate: new code is a candidate, not the default. If an existing, configurable, composable, or adaptable solution delivers the same required experience with lower total burden, EOG prefers it. If EOG itself adds more burden than it removes, it should not be used.

## What is in this repository

- `AGENTS.md` — normative EOG 1.1 definition.
- `skill/SKILL.md` and `workflows.json` — agent-facing operations such as plan, search, review, audit, debt, impact, and bounded loops.
- `record.schema.json` + `validate.py` — machine-checkable representation of experiences, goals, constraints, candidates, wheel searches, gaps, checks, and evidence.
- `eog.py` — deterministic CLI for validation, stage checks, impact/debt inspection, lifecycle adapters, handoff/loop receipts, and native integration support.
- `adapters/` — thin OpenCode, Pi, and Hermes integrations.
- `mcp_server.mjs` — optional read-only MCP carrier using the official MCP SDK.
- `capabilities.json` / `integrations.json` — responsibility and host-integration inventories; they are not claims that every host was actually tested.
- `behavior_cases.json` — model-behavior cases. They remain `not_run` until real model/tool evidence exists.

## Quick start

Requirements: Python 3.11+; Node 22+ only for JS adapters/MCP.

```bash
git clone <this-repository>
cd eog
python -m pip install -r requirements.txt
python -m unittest discover -v
node --test test_adapters.mjs
```

To use EOG on another repository, add the normative `## Experience Optimality Gate (EOG)` section from this repository's `AGENTS.md` to that project's root `AGENTS.md`, then point the CLI at the project:

```bash
python /path/to/eog/eog.py --root /path/to/project prompt --workflow plan
python /path/to/eog/eog.py --root /path/to/project doctor
```

`prompt` returns the selected EOG operation for the existing agent. It does not claim the operation has run.

## Material decisions

For consequential or nontrivial engineering choices, represent the decision with `record.schema.json` and validate it:

```bash
python validate.py example.json
python eog.py --root /path/to/project gate example.json \
  --stage design \
  --owner <work-owner> \
  --revision <subject-revision>
```

A `design_pass` means the recorded choice is structurally ready for authorized implementation. It does **not** mean the claimed search is truthful, permissions exist, the implementation works, or the consumer experience was delivered.

Completion requires current evidence at the consumer boundary:

```bash
python eog.py --root /path/to/project gate record.json \
  --stage completion \
  --owner <work-owner> \
  --revision <subject-revision>
```

## Existing-wheel search

EOG requires real inspection, not a list of categories. For material novelty, inspect the relevant project behavior and existing code, standard/native platform capabilities, installed tools, standards/protocols, established patterns/theory, maintained products/services, and maintained open source when applicable.

The resulting question is not “can we build this?” but:

> What useful responsibility remains after the best existing options and adaptations have been checked?

Every material novel part must trace to that residual gap.

## Native delivery

EOG prefers native instruction loading first. For hosts that need another delivery mechanism, `eog.py install` can preview a bounded native hook/rule change:

```bash
python eog.py --root /path/to/project install --host cursor-rule
python eog.py --root /path/to/project install --host cursor-rule \
  --apply --expected <preview-before-sha-or-absent>
```

Writes use exact old-content preconditions, preserve unrelated configuration, and report loading as unverified until the actual host is observed. Windows shell-hook installation is not claimed; use the host's native instruction/rule path where appropriate.

Supported generated/native paths are listed in `integrations.json`.

## Optional MCP carrier

MCP is a carrier here, not a replacement agent runtime. With `@modelcontextprotocol/sdk@1.30.0` installed:

```bash
EOG_ROOT=/path/to/project node mcp_server.mjs
```

It exposes read-only EOG instructions, validation, and status. It does not grant permission, schedule work, or create a second agent.

## Honest claims

EOG intentionally distinguishes:

- structural validity from truth,
- design readiness from delivery,
- a source digest from actual host loading,
- a passing component test from consumer acceptance,
- instruction injection from a security boundary,
- observed Git deltas from counterfactual “code/token savings.”

The test suite covers structural and local runtime behavior. Mocked callback tests are not native-product certification. Model behavior cases are separate from deterministic tests.

## Tests

```bash
python -m unittest discover -v
node --test test_adapters.mjs
npm ci
node --test test_mcp.mjs
```

## Provenance

EOG 1.1 unified an earlier internal experience-optimization method with useful ideas and adapter patterns from Ponytail and Loopy. The latter remain independently owned projects; their pinned provenance and MIT notices are preserved in `THIRD_PARTY_NOTICES.md`. External Loop Library hosting remains external rather than being cloned into EOG.

## License

EOG is released under the MIT License. See LICENSE.
