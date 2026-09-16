# EOG project instructions

This repository uses its own EOG definition below as the canonical engineering method.

## Experience Optimality Gate (EOG)

EOG 1.1 is the unified, always-on decision and execution method for all coding
and engineering work. It is intended to absorb the pinned Ponytail and Loopy local
engineering workflows, but replacement readiness is not claimed until behavioral
parity is verified under `ABSORPTION_COMPLETION_PLAN.md`.
It never expands the selected task, authority, or canonical owners. Restore an
outage first; EOG governs the lasting repair. Depth follows uncertainty and
consequence, not an optional mode or compulsory form. Historical names preserve
provenance, not parallel gates.

### 1. Consumer experience is the objective

Establish who consumes the changed boundary, their context and intent, and the
complete process and result they should experience. Consumers include humans,
agents, API/MCP clients, library callers, services, programs and devices. Include
materially affected consumers; internal optimization must not degrade the
experience it serves. The target is the experience, not a feature list or an
implementation. Define success, unacceptable outcomes and failure experience:
what remains preserved, observable and actionable, and how work resumes.
Derive functional/lifecycle/quality requirements from this experience, not an
invented technical checklist. An explicitly consumed protocol may be a target;
an internal technology preference may not. Separate requirements from
preferences; expose consumer conflicts and preserve user priorities. Never
silently reduce acceptance, change business meaning or invent favorable metrics.

For material work, record this in the existing task/work owner or directly affected
design owner before commitment. State observable acceptance at the consumer
boundary. A small deterministic change may use concise internal judgment.

### 2. Derive, do not fossilize, requirements

Every material derived goal must have a reasoned path to at least one target
experience. The acyclic supports graph expresses justified contribution, not
proof of sufficiency or necessity. Model joint AND requirements, OR alternatives
and candidate-specific goals. Revise goals when evidence changes; do not reject
a better solution because it avoids the first solution's mechanism.

Keep hard constraints separate with actual source/authority: user limits,
safety, security, rights, external contracts and canonical owners. They are not
optional costs. Every material implementation element traces to an experience,
supporting goal or constraint. Investigate untraced items; neither unfamiliar
code nor an absent label justifies deletion. Traceability alone does not prove
that code, a dependency or an abstraction is needed.

### 3. Mandatory existing-wheel search

Before material new implementation, actually search by consumer outcome and
underlying problem, not just a proposed solution name. A list of candidate
categories is not a search. Inspect relevant project behavior/code/data/practice,
stdlib, native platform capabilities, installed approved tools, industry
standards/protocols/specifications, established theory and patterns, maintained
products/services and maintained open source. Search both the whole outcome and
its reusable parts. Consider configuration, composition, adaptation, extension,
no change and waiting.

Use current primary evidence for material external decisions: source, version,
capability, requirements, limitations, maintenance, relevant price/license,
failure behavior and exit cost. Inspect actual API/source when it decides fit.
Keep private context out of public queries. Investigation does not authorize
installation, payment, publication or privilege expansion.

Retain actual inspections, closest options, concrete fit/gaps and a justified
search stopping boundary in the existing owner. Explain irrelevant categories;
a known local fix needs no unrelated market survey. Unavailable evidence is not
evidence that a wheel does not exist. Never claim exhaustive worldwide absence
or global mathematical optimality. A plausible stronger option or decisive
unknown keeps selection provisional: only bounded investigation or an approved
reversible experiment, not production commitment.

### 4. Gap justification before novelty

New code is a conditional candidate, not the default. Each material novel part
needs a source-grounded residual gap: unmet experience/constraint, existing
options and adaptations checked, why insufficient, and the smallest new
responsibility needed. Functional, total-cost, safety, continuity or exitability
deficits need evidence; preference, unfamiliarity and ability to build do not.

Prefer reuse -> configure -> compose -> adapt -> extend -> build when experience
and constraints hold without material disadvantage. Compose existing wheels;
an adapter gap never licenses replacement of a working runtime. New glue,
schemas, validators, tests, and this gate itself are subject to the same rule.
Scope negative search evidence; invent no competing product.

### 5. Experience, feasibility and total burden

Exclude violations of required experience or hard constraints. Compare relevant
non-dominated options on consumer benefit and total delivery/ownership burden:
time, cash, tokens/compute, engineering, maintenance, operation, failure and
collision risk, migration, lock-in, exitability, irreversible commitment and
cognitive load. Use supported estimates, not arbitrary weights, fake precision,
line-count goals or endless perfectionism.

Experience equivalence alone does not prove dominance. Dominance means no worse
on every material axis and better on at least one. Existing products can lose
on cost/risk. Reuse when no evidenced advantage justifies new ownership. Among
experience-equivalent feasible options prefer lower burden and reversible
commitment. Minimality never weakens validation, data-loss handling, security,
accessibility or explicit requirements. No replaceable tool may solely own
unrecoverable records, provenance, rights or operating continuity.

A `design_pass` means a scoped, evidenced choice is ready for authorized
implementation; it does not mean the experience has been delivered. Retain
selection, alternatives, minimum novelty, acceptance, remaining non-decisive
risks and invalidation triggers. Decisive unknowns block design_pass. Structural
validity, design readiness and actual completion are different claims.

### 6. Fresh-reality execution

Observe -> choose one bounded action -> act -> verify -> retain durable meaning
in the existing owner -> repeat or stop. Re-read state/authority before
consequential action. Preserve unrelated work. Trace real flow and callers;
repair the smallest correct shared causal boundary, not merely one symptom or
an unrelated deeper system. Evidence can invalidate solutions, goals and their
dependents. Re-derive and compare again; never redefine the root to excuse code.
Correct misunderstood intent from user/contract evidence, with approval for
changes to business meaning, authority or hard requirements.

Honor supplied limits; invent no iteration budget. Stop when progress has ceased
and no new evidence can change the next useful action. Investigation is bounded too. Work
without informative feedback is one-shot, not a manufactured loop.

### 7. Consumer-boundary completion

Separate planned checks, observations and inference. Record subject revision,
conditions, observation and result; changes invalidate affected evidence.
Components, PRs, HTTP 200, healthy processes and self-written success labels do
not replace consumer acceptance. Use independent review or a separate acceptance
signal where self-approval/overfitting is material.

Success and clean_noop require current required root experience and constraints
to be observed. Otherwise name blocked, approval_required, exhausted (an actual
supplied limit) or stagnated with the exact residual; running is not terminal.
Waiting is not success unless requested. Design-only completion concerns the
design deliverable, never the proposed product's unobserved behavior.

### 8. Full operations, one existing agent

Use the packaged `skill/` entry and `workflows.json` for
review, repo audit, debt, impact, loop discovery/find/craft/adapt/audit/run/
debrief/save/publish, handoff, diagnosis and help. These specialized operations
run on the current agent, not a new model, engine or scheduler.

Review actual code/callers, not just trace labels. Preserve shortcut ceilings,
upgrade paths and revisit triggers, including legacy `ponytail:` markers. Report
observed impact or attributed benchmarks, not invented unspent code/tokens.
Require two observed instances for recurrence; otherwise label inference. Read
saved loops and the live catalog; unavailable access is not absence and memory
cannot replace live publication truth.

Bind exact loop text/revision/digest, experience, informative feedback, bounded
action, verification, owner, authority and stops. Craft/adapt does not execute;
run does not schedule. Debrief actual receipts. Preserve LOOPS.md, debt and
provenance; save through the existing owner only when requested. Publication
requires exact preview, separate approval, current provider contract and
readback. Reuse the external catalog/hosting, not a cloned marketplace.

### 9. One source, native lifecycle integration

This section owns EOG meaning; schemas, CLI, workflows and adapters in
this repository are subordinate support. Material records stay in
the existing task/design owner. A valid record proves structure only, not truth.
Reuse native AGENTS loading first. Add the supplied native hook/rule/extension
only for the actual host's delivery gap. Generated copies carry a source digest,
not independent policy. Installation/update preserves foreign settings and work
through preview and exact old-content preconditions.

On session/resume/compaction/delegation/context changes verify current policy,
task/owner, experience, goals, constraints, wheels/gaps, revision, evidence,
authority and stops. Inspect actual native overrides and combined context budget.
Do not overwrite active work or restart healthy services to refresh instructions.
Instruction injection is guidance, not an unbypassable reference monitor.
Typed stage/PreToolUse checks reject inconsistent records at their configured
boundary, never grant permission or infer arbitrary shell effects. Native tool
permissions, owner transactions and protected CI retain authority. Missing
material evidence blocks the claim, not unrelated safe investigation.

### 10. Absorption completion and honest conformance

The capability manifest is a coverage inventory. `mapped` means that an upstream
responsibility and expected behavior have been identified; it does not mean the
behavior has been absorbed. A capability becomes replacement-ready only after an
EOG implementation exists, behavioral parity is verified against the pinned
baseline, and the replacement trial passes with the upstream local component
absent or disabled. External hosted services may remain reused, but EOG still
needs parity for the client workflow around them.

Optional Ponytail modes are currently a deliberate policy change to proportional
depth, not presumed equivalence. Their utility must be covered by compatibility
or behavioral evidence before replacement readiness. User Stop remains immediate.
Status is observed loading, not compliance; foreign benchmarks retain attribution.

Separate schema/CLI, adapter-contract, parity, actual-host and model-behavior
tests. Manifest-presence tests establish inventory coverage only. Before
retirement, inventory exact versions/configs, preserve loops/debt/customizations/
provenance, verify rollback and test every required host with legacy components
absent or disabled. Offline/untested hosts remain unverified. No blind deletion,
privilege expansion or automatic uninstall from a self-written receipt.

No EOG mode file, separate database, scheduler, agent runtime, or receipt store.
EOG must save more total burden than its own machinery adds.
