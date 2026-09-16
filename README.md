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

## Absorption status

EOG now ships pinned detailed procedures, native-text loop clients, observation-backed admission, portable packaging, and executable compatibility tests. Mapping and procedure delivery are still not proof of every native-host behavior. The public release does **not** yet claim replacement readiness for either project.

The completion standard is defined in [`ABSORPTION_COMPLETION_PLAN.md`](ABSORPTION_COMPLETION_PLAN.md): a capability progresses from `mapped` to `implemented`, `parity_verified`, and only then `replacement_ready`. Native hosts remain inventory entries until observed in the real host. External Loop Library infrastructure remains external; EOG must still provide parity for the client workflow around it.

## Quick start

Use the rules with your existing agent; no new agent or service is installed.
Small edits do not require a JSON record. Load detailed procedures only for the
operation you need. Compact refresh is used only for the exact bundled policy;
custom or amended EOG policy is delivered in full, never silently compressed away.

Requirements: Python 3.11+; Node 22+ for the portable launcher, adapters or MCP.

```bash
git clone https://github.com/lee5312/experience-optimality-gate.git
cd experience-optimality-gate
python -m pip install -r requirements.txt
node bin/eog.mjs --root /path/to/project init
```

The last command previews adding EOG to an existing AGENTS.md without overwriting
foreign instructions. Apply that exact preview using its before_sha256:

```bash
node bin/eog.mjs --root /path/to/project init --apply --expected <before_sha256-or-absent>
node bin/eog.mjs --root /path/to/project prompt --workflow review
```

The existing agent executes the requested procedure using its normal tools.
The prompt command itself only supplies instructions, not a completed review.
On Windows the launcher tries the installed Python launcher (`py -3`) before
Python executables; EOG_PYTHON can explicitly select an executable. It never
installs Python or changes a user profile. The Python CLI also works directly.

## Operations, not another runtime

The package retains the full pinned Ponytail review/audit/debt/gain/help and
Loopy discover/find/compare/craft/adapt/audit/repair/run/debrief/save/publish
procedures under skill/references. reference-lock.json binds their exact upstream
revision and bytes; a changed or missing reference fails loading. EOG's current
policy and user authority take precedence over historical mode or budget rules.
The semantic work stays with your existing agent, as in the original skills.

New deterministic client operations work on real data:

```bash
node bin/eog.mjs --root /path/to/project saved-loops
node bin/eog.mjs --root /path/to/project find-loop "documentation drift"
node bin/eog.mjs --root /path/to/project save-text --title "Docs sweep" --explanation "Fix documentation drift and stop on no progress." --prompt-file accepted-prompt.txt --expected <LOOPS.md-sha256-or-absent>
node bin/eog.mjs --root /path/to/project compare-loops candidates.json
```

Native Loopy Markdown and EOG JSON blocks coexist in LOOPS.md. Saving preserves
the exact accepted prompt, dates/source metadata and unrelated bytes. Updates
also require the exact old entry digest (`--replace-entry`). Catalog retrieval
returns at most three lexical candidates for the agent to compare semantically;
an unavailable live provider is not reported as an empty published catalog.

`prepare-publication candidate.json` checks provider field limits and live
overlap and returns a preview. It does not POST. Complete approved submissions
through the existing official browser/owner surface, including its human
verification and exact current ownership/license attestation. An accepted
suggestion is not a published loop. `verify-publication` checks a live catalog
entry against an exact prompt digest; it does not claim the detail page was checked.

## Evidence-backed admission

The default record gate checks structure and revision consistency, not truth.
For a CI/reviewer-controlled boundary, capture a real explicitly authorized
command against explicit subject files:

```bash
node bin/eog.mjs --root /path/to/project observe --owner <work-owner> --revision <current-git-sha> --subject src/example.py -- python -m unittest > observation.json
node bin/eog.mjs --root /path/to/project gate record.json --stage completion --owner <work-owner> --revision <current-git-sha> --observations observation.json --observations-sha256 <trusted-observation-digest>
```

This verifies the recorded command outcome, current subject bytes, checkout,
policy and owner binding. Failed commands, changed files and tampered records
are rejected. The expected digest must come from a trusted CI/reviewer channel;
letting an author choose both the receipt and trusted digest is not independent
verification. This does not certify unlisted files, all acceptance checks, search
truthfulness or user experience. Native permission checks still apply.

## Material decisions

For consequential choices where structured traceability materially helps, use
`record.schema.json`. Do not require these fields for every edit or textual loop:

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

Candidate delivery paths are listed in `integrations.json`; that inventory is not a support certification. The npm package declares the actual OpenCode default export and Pi skill/extension paths; Codex and Claude instruction-plugin manifests are included. Native acceptance is recorded separately.

## Optional MCP carrier

MCP is a carrier here, not a replacement agent runtime. With `@modelcontextprotocol/sdk@1.30.0` installed:

```bash
EOG_ROOT=/path/to/project node mcp_server.mjs
```

It exposes read-only EOG instructions, validation, status, saved-loop reading, loop finding, and exact-record comparison. Catalog text never executes through these tools. It does not grant permission, schedule work, or create a second agent.

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
python -m pip install -r requirements.txt
python -m unittest discover -v
python scripts/parity.py
npm ci --ignore-scripts
node --test test_adapters.mjs test_mcp.mjs
```

The portable operation suite runs on Linux, Windows and macOS in CI. POSIX shell-hook
installation is tested separately; Windows shell hooks remain intentionally unclaimed.
No claimed model-effectiveness or savings result follows from these tests.

## Provenance

EOG 1.1 unified an earlier internal experience-optimization method with useful ideas and adapter patterns from Ponytail and Loopy. The latter remain independently owned projects; their pinned provenance and MIT notices are preserved in `THIRD_PARTY_NOTICES.md`. External Loop Library hosting remains external rather than being cloned into EOG.

## License

EOG is released under the MIT License. See LICENSE.
