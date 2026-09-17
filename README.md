# EOG — Experience Optimality Gate

EOG 2.0 is judgment support for capable engineering agents. It unifies the useful responsibilities of UOG, Ponytail, and Loopy without turning intelligent work into a compulsory deterministic process.

The ordinary model is:

`Experience -> Choice -> Minimality -> Feedback -> Integrity`

## What changed in 2.0

- The always-present layer is a concise cognitive policy, not a mandatory state machine.
- Original UOG strengths are explicit again: entry, interaction, wait/pay cost, continuity, failure/recovery, durable truth, exitability, total burden, non-dominated alternatives, and no-ceremony handling for obvious low-risk work.
- Newer EOG strengths remain: human and nonhuman consumers, requirements-not-mechanisms, residual-gap novelty, decision-relevant uncertainty, current-evidence invalidation, and consumer-boundary completion.
- Ponytail is capability-complete, including task-scoped `auto/off/lite/full/ultra` depth compatibility without persistent mode state.
- Loopy client operations are available through EOG: discover/find/compare/craft/adapt/audit/repair/run/debrief/save/publish. External Loop Library hosting remains an external wheel.
- Deterministic enforcement is narrow: authority, durable-write integrity, stale evidence, canonical ownership, unsupported machine-readable completion, external consequence, and protected data. It does not choose architecture or replace agent judgment.
- Capability existence and verification evidence are separate axes.

## Quick start

Requirements: Python 3.11+; Node 22+ only for the portable launcher/adapters/MCP.

```bash
git clone https://github.com/lee5312/experience-optimality-gate.git
cd experience-optimality-gate
python -m pip install -r requirements.txt
node bin/eog.mjs --root /path/to/project init
node bin/eog.mjs --root /path/to/project prompt --workflow review --depth auto
```

`prompt` supplies detailed reasoning context to the existing agent; it does not pretend the review or loop has run. Ordinary work does not require invoking it.

## Deep methods

`plan search review audit debt impact discover find compare craft adapt loop-audit repair run debrief save publish handoff doctor help`

These are optional operations, not sequential gates. Pinned Ponytail/Loopy procedures remain hash-locked under `skill/references/` and are loaded only for the selected operation.

## Compatibility and closure

`capabilities.json` records the strict-superset contract. Every useful upstream capability resolves to `absorbed`, `generalized`, `compatibility_alias`, or `external_service_reuse`. Capability state (`absent/mapped/implemented/compatible`) is independent of evidence state (`unverified/contract_verified/native_verified`).

Capability closure is complete in the package; native-host verification remains host-specific and is never inferred from inventory or unit tests.

## Hard guards and optional representations

Schemas, observations, receipts, CAS writes, and native guards exist to protect integrity or preserve useful provenance. They are not the normal workflow. A structurally valid record is not automatically true, a successful hook is not permission, and a component test is not consumer completion.

## External Loop Library

EOG reuses the existing provider for catalog/hosting/account/voting. It implements the client workflow around that wheel rather than cloning the service. Local save is not publication; publication retains the provider's real current approval and human-verification boundaries.

## Provenance

EOG includes pinned MIT-licensed Ponytail and Loopy procedure text with exact revisions and hashes in `reference-lock.json` and `THIRD_PARTY_NOTICES.md`. UOG originated as Paralloff's experience-optimality method and is generalized into the EOG Judgment/Optimality core.

## License

MIT. See `LICENSE`.
