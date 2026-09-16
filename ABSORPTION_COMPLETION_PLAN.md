# Complete Absorption Plan

Status: required before EOG may claim Ponytail/Loopy replacement readiness.

## Objective

EOG is intended to be a functional successor to the pinned Ponytail and Loopy engineering-method capabilities, not merely a manifest that names their responsibilities.

The acceptance question is:

> With the pinned Ponytail and Loopy implementations absent or disabled, can a user complete the same supported workflows through EOG alone, with equivalent or better observable behavior, while preserving the external services that should remain external?

If not, absorption is incomplete.

## Pinned baselines

- Ponytail: `DietrichGebert/ponytail@e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156`
- Loopy: `Forward-Future/loopy@75966cbd572a4185064971c9fe5e9c52e8f8456d`

These exact revisions are the compatibility baselines. New upstream changes are separate work until deliberately adopted.

## Status model

`capabilities.json` is a coverage inventory, not proof of absorption. Every imported capability must progress through these states:

1. `mapped` — source responsibility and expected behavior are identified.
2. `implemented` — an EOG path exists without requiring the upstream local runtime.
3. `parity_verified` — behavioral acceptance passes against the pinned upstream expectation.
4. `replacement_ready` — parity passes with upstream local components disabled/absent, rollback is verified, and any required native host is observed.

An external hosted service may remain `external_reuse`; the EOG client experience around that service must still reach `parity_verified` before replacement readiness.

No row may be described as fully absorbed merely because an ID, prompt, schema, or adapter exists.

## Current gaps to close

The 1.1.0 public release has useful implementation, but the replacement claim is not yet proven:

- the capability manifest maps responsibilities more strongly than the current behavioral evidence supports;
- host inventory entries are all `native_verified: false` and therefore are inventory, not support claims;
- several Ponytail integrations were re-expressed as thin EOG adapters without native-host parity evidence;
- Ponytail optional mode semantics were intentionally replaced by proportional depth, but behavioral equivalence has not been demonstrated;
- Loopy operations are represented in EOG workflows, while end-to-end parity for the full discover/find/compare/audit/repair/adapt/craft/run/debrief/save/publish experience is not yet established;
- Loop Library hosting should remain external, but EOG must provide the complete compatible client-side experience around it;
- current regression tests include manifest-presence checks that prove inventory coverage, not replacement parity;
- `behavior_cases.json` remains `not_run`, so actual model/tool behavior is not yet evidence.

## Architecture boundary

EOG should absorb behavior, not duplicate healthy infrastructure.

```text
EOG core
  ├─ experience / requirements / constraints
  ├─ wheel search / residual gap / selection
  ├─ bounded execution / evidence / completion
  ├─ Ponytail-compatible engineering operations
  └─ Loopy-compatible bounded-loop operations
          └─ external Loop Library service when live catalog/hosting is needed
```

External hosted catalog/auth/voting/storage remain external wheels. A user must not need the local Ponytail or Loopy runtime to execute the supported EOG workflows.

## Ponytail parity matrix

Each row needs a fixture or native observation, not only a manifest entry.

| Family | Required EOG behavior | Replacement acceptance |
| --- | --- | --- |
| Core minimalism | YAGNI/reuse/native-first without correctness regression | same task avoids unnecessary implementation and preserves requirements |
| Causal tracing | inspect real flow and sibling callers | shared cause is found before symptom-only patch |
| Review | scoped complexity review | real diff/callers compared with simpler native/existing alternatives |
| Audit | repository-wide complexity audit | ranked evidence-backed ownership burden with explicit uninspected scope |
| Debt | preserve shortcuts, ceilings, triggers, legacy markers | tracked-source scan is lossless and does not auto-delete |
| Impact | measured impact only | real baseline/delta; no invented token/code savings |
| Help/dispatch | discoverable operations | every absorbed operation is reachable from EOG without upstream skill install |
| Lifecycle | session/resume/compaction refresh | current policy/task/revision survives supported lifecycle transitions |
| Delegation | subagent/handoff context binding | wrong task/revision/policy/tampered packet is rejected |
| Status | visible loading/source state | reports observed state without claiming compliance |
| Install/update/remove | modify only owned integration | preview + CAS + idempotency + foreign config preservation + rollback |
| Host portability | native instructions/rules/extensions | only natively observed hosts are called supported |
| OpenCode | every-turn extension behavior | native load + context injection + command collision behavior observed |
| Pi | fresh-turn context, commands, status, active queue | native load and active/idle behavior observed |
| Hermes | pre-LLM + skill/command + gateway boundary | native registration and permission preservation observed |
| MCP | portable user-invoked fallback | official MCP client roundtrip; no false always-on claim |
| Modes | utility of off/lite/full/ultra behavior | either compatibility exists or proportional-depth replacement proves equal/better behavior for representative cases |

## Loopy parity matrix

| Operation | Required EOG behavior | Replacement acceptance |
| --- | --- | --- |
| Discover | identify repeated work from actual evidence | recurrence claims require observed evidence; strongest candidate is bounded |
| Find | query exact current saved/published loops | live provider failure is reported unavailable, never invented |
| Compare | compare candidate loops without hidden weakening | choice preserves intended outcome and authority boundaries |
| Audit | inspect weak checks/actions/stops | material defects identified without gratuitous redesign |
| Repair | fix only material loop defects | repaired definition preserves intended outcome |
| Adapt | modify exact-version loop | thresholds/tools/owners/checks can change without weakening feedback |
| Craft | design a bounded loop from goal/context | no invented cadence, technology, authority, or budget |
| Run | execute bounded steps on current agent/tools | exact definition/revision/authority/stops bound to the run |
| Debrief | learn only from actual receipt | claims trace to observed execution evidence |
| Save | preserve project loop through existing owner | save is atomic/revision-safe and is not publication |
| Publish | exact preview + separate approval + readback | no external publication before explicit authority; provider response verified |

The Loop Library backend itself is not to be cloned. `Find` and `Publish` may reuse it as the external provider while EOG owns the compatible client workflow.

## Parity harness

Add an executable compatibility suite rather than more manifest-presence tests.

For each baseline capability:

1. capture a minimal upstream fixture or behavior contract from the pinned source;
2. run the equivalent EOG operation with local Ponytail/Loopy components absent;
3. compare observable inputs, outputs, side effects, authority handling, failure behavior, and stopping behavior;
4. record whether the EOG result is equivalent, deliberately changed, or missing;
5. require evidence for deliberate changes showing why user utility is not reduced.

The suite must fail when a capability is merely listed but not executable.

## Native-host acceptance

`integrations.json` remains an inventory until actual host observations exist.

A host becomes `native_verified: true` only after an exact EOG revision is loaded by the real host and a representative lifecycle/workflow path is observed. Mocked adapter tests remain adapter-contract evidence only.

Unsupported or offline hosts stay unverified; they do not block unrelated hosts and may not be marketed as supported.

## Actual model behavior

After deterministic parity, execute `behavior_cases.json` on at least the primary supported agent path with transcript/tool evidence and independent rubric results.

This stage answers whether the integrated method changes agent behavior, not whether the schemas compile.

At minimum measure:

- existing solution inspected before material novelty;
- unnecessary new implementation avoided;
- residual gap grounded in evidence;
- false completion claims rejected;
- consumer-boundary verification attempted when observable;
- authority denial respected;
- total process burden, including extra ceremony.

## Ceremony constraint

Full material records are not the default for every edit.

- small deterministic work: concise EOG judgment through native instructions;
- consequential/nontrivial choice: structured record when it materially improves traceability or admission;
- audit/compliance need: durable record as required by the existing owner.

If structured machinery does not improve the task outcome enough to justify its cost, EOG must not require it.

## Public claim rules

Until the corresponding evidence exists:

- `mapped` must not be called absorbed;
- an inventory host must not be called supported;
- adapter tests must not be called native-host tests;
- schema validity must not be called truth validation;
- parity on one operation must not imply whole-project replacement;
- EOG must not claim Ponytail/Loopy replacement readiness.

The phrase `complete replacement` is reserved for a release whose required parity matrix is green with upstream local components disabled or absent.

## Execution order

### P0 — Correct claims and state model

- publish this plan;
- change public wording from completed replacement to absorption-in-progress;
- make the manifest distinguish coverage from parity;
- retain pinned provenance.

### P1 — Build parity harness

- replace manifest-presence acceptance with executable per-capability fixtures;
- add machine-readable parity status/evidence locators;
- fail CI on regression of a `parity_verified` capability.

### P2 — Finish Ponytail absorption

- close deterministic operation gaps first;
- run real OpenCode/Pi/Hermes/MCP/native-rule acceptance where available;
- resolve optional-mode compatibility with evidence rather than assertion.

### P3 — Finish Loopy absorption

- close discover/find/compare/audit/repair/adapt/craft/run/debrief/save/publish parity;
- keep Loop Library infrastructure external;
- verify unavailable-provider and publication-authority paths.

### P4 — Replacement trial

- disable/remove local Ponytail and Loopy components in the acceptance environment;
- execute the complete compatibility suite and representative native-host workflows;
- verify rollback before retiring any installation.

### P5 — Behavior and burden evidence

- run actual model/tool behavior cases;
- compare full EOG with simpler instruction-only and pinned upstream baselines;
- retain only machinery whose utility exceeds its burden.

## Release gate

A release may state that EOG fully absorbs the pinned Ponytail and Loopy local functionality only when:

- every required matrix row is `parity_verified` or explicitly `external_reuse` with client parity verified;
- upstream local components are absent/disabled during replacement acceptance;
- actual required hosts have native observations;
- rollback is proven;
- `behavior_cases.json` has real evidence for the primary supported path;
- no unsupported host or untested behavior is represented as verified;
- EOG still satisfies its own rule: the burden it removes exceeds the burden it adds.

If these conditions cannot be met without unjustified complexity, the correct result is to narrow EOG rather than preserve a replacement claim.
