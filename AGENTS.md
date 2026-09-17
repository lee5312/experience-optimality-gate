# EOG project instructions

This repository uses the EOG definition below as its canonical engineering method.

## Experience Optimality Gate (EOG)

EOG 2.0 helps a capable agent make better engineering decisions. It does not replace judgment with a compulsory process. It absorbs the useful responsibilities of UOG, Ponytail, and Loopy into one mental model while preserving their useful compatibility surfaces. Their names are provenance and compatibility, not three gates that must run in sequence.

The ordinary model is: understand the experience -> choose intelligently -> minimize unnecessary ownership -> execute with useful feedback -> verify the real result. Depth follows the decision. Simple work stays simple.

### Judgment Core

These are reasoning heuristics, not mandatory workflow states.

#### Experience before machinery

Understand the consumer and the materially relevant experience before committing to machinery. A consumer may be a human, agent, API/MCP client, service, program, device, or combination of them. When it can change the decision, consider entry, successful outcome, interaction and effort, waiting or latency, monetary/compute/token cost, continuity across reload/restart/update/network loss/migration/replacement, failure experience, recovery, durable truth ownership, exitability, and observable completion.

Do not turn that list into paperwork. Include what can materially change the decision. The target is the experience, not a feature list, implementation, technology preference, or process artifact.

#### Requirements are not mechanisms

Derive requirements from the desired experience and real hard constraints. Do not preserve an early implementation assumption merely because it appeared first. A material requirement needs a reasoned relationship to an experience or actual constraint. Explicit DAGs, AND/OR graphs, matrices, schemas, and formal records are optional representations and should exist only when they improve reasoning.

Revise derived requirements when evidence changes. Do not reject a better candidate merely because it avoids the mechanism assumed by an earlier candidate. Keep authority, safety, security, rights, contracts, canonical ownership, durability, and explicit user limits distinct from preferences.

#### Existing solutions are first-class candidates

New implementation is one candidate, never the automatic default. When it can change the decision, inspect applicable existing behavior/code/records/practice, standard-library and language capabilities, operating-system and native-platform capabilities, approved dependencies and tools, standards/protocols/specifications, established theory and patterns, maintained products/services, maintained open source, configuration, composition, adaptation/extension, no change, and waiting.

Search by the consumer outcome and underlying problem, not only the first proposed solution name. Inspect only as deeply as useful to the current decision; do not perform ceremonial surveys of irrelevant categories. Unavailable information is not evidence that an option does not exist, and EOG never claims exhaustive worldwide absence.

#### Own only residual responsibility

After examining the strongest applicable existing options, identify the useful responsibility that remains unsatisfied. New code, glue, schemas, validators, tests, infrastructure, agents, and EOG machinery itself require such a residual responsibility.

Prefer reuse -> configure -> compose -> adapt -> extend -> build when required experience and constraints remain satisfied. An adapter gap does not justify rebuilding a sound system. Ability to build, unfamiliarity, aesthetic preference, or architectural purity is not by itself a residual gap.

#### Compare without fake precision

Eliminate candidates that violate required experience or hard constraints. Among the remainder, eliminate a candidate when another feasible candidate is no worse on every material dimension and better on at least one. Material dimensions may include consumer outcome, time, money, tokens/compute, engineering effort, maintenance, operation, failure/collision risk, cognitive burden, migration, lock-in, exitability, reversibility, and irreversible commitment.

Do not invent numeric weights or arbitrary scores merely to force an ordering. When feasible candidates remain genuinely incomparable, use actual user priorities, constraints, uncertainty, and reversibility.

#### Investigate decision-relevant uncertainty

Do not try to remove all uncertainty. Investigate an unknown when learning its answer could plausibly change feasibility, a hard-constraint judgment, the non-dominated candidate set, the amount of residual novelty, or the selected commitment. Otherwise retain the uncertainty and proceed. Investigation itself has cost; stop when more information cannot reasonably change the next useful decision.

#### Claim only what current reality supports

A plan, schema, PR, component test, process status, HTTP response, generated receipt, or self-written success label is not automatically the consumer outcome. Claim completion only at the boundary actually changed. If the requested result is not established, use an honest state such as running, clean_noop, blocked, approval_required, exhausted, or stagnated. Never redefine the objective to make an implementation appear successful.

### Optional Deep Methods

The Judgment Core is sufficient for ordinary work. Load a deeper method only when it can materially improve reasoning or perform a requested specialized operation. Available operations include plan, search, review, audit, debt, impact, discover, find, compare, craft, adapt, loop-audit, repair, run, debrief, save, publish, handoff, diagnose, doctor, and help.

These are tools for an intelligent agent, not stages every task must pass through. A deterministic, obvious, low-risk change may use concise judgment without a decision record, candidate matrix, goal graph, or receipt.

### Optimality — UOG absorbed and generalized

For materially consequential choices, deepen the Judgment Core using this reasoning model: experience -> hard constraints -> plausible candidates -> feasible/non-dominated candidates -> decision-relevant uncertainty -> residual responsibility -> reversible or committed choice -> consumer-boundary completion. This is a reasoning model, not a mandatory state machine.

Preserve the useful UOG concerns when relevant: entry, successful path, what the consumer sees and does, waiting, payment and compute cost, continuity, failure, recovery, durable truth, exitability, total burden, fresh primary evidence, non-dominated alternatives, decisive unknowns, concise treatment of deterministic low-risk work, and no separate process artifact merely to prove the method ran.

Structured decision records are optional representations for complex work, not prerequisites for thinking.

### Minimality — Ponytail fully absorbed

EOG owns Ponytail's useful minimality, causal, review, audit, debt, impact, lifecycle, delegation, status, installation, portability, integration, and regression responsibilities.

When relevant, reason roughly: does this need to exist? -> can current work be reused? -> is there a native capability? -> is an approved capability already installed? -> is there a maintained existing solution? -> what residual implementation is actually necessary? This ordering is a heuristic; do not perform meaningless steps merely because they are listed.

Trace actual flow and sibling callers before symptom-only repair when shared causality is plausible. Minimality never overrides correctness, validation, security, accessibility, data-loss handling, durability, or explicit requirements. Preserve meaningful debt markers, ceilings, upgrade paths, revisit triggers, and provenance. Report observed impact or clearly attributed external measurements, never invented counterfactual savings.

#### Depth compatibility

EOG uses `auto` depth by default: the agent chooses the smallest reasoning depth capable of changing the decision. Explicit task-scoped Ponytail compatibility hints remain valid: `off`, `lite`, `full`, and `ultra`.

`off` skips optional optimization procedures for the scope but never disables authority or integrity boundaries. `lite` requests a brief experience/reuse/minimality check. `full` requests detailed optimality and minimality review. `ultra` requests unusually exhaustive analysis when explicitly requested or materially justified. These are temporary scope hints, not persistent global modes; no EOG mode file is required.

### Feedback — Loopy fully absorbed

EOG owns the Loopy client workflow: discover, find, compare, craft, adapt, audit, repair, run, debrief, save, and publish.

The general execution heuristic is observe fresh reality -> choose one useful bounded action -> act -> verify -> retain durable meaning -> continue only if new feedback can change the next useful action. Do not manufacture iterations. Work with no informative feedback may be one-shot.

Stop when the requested result is achieved, the next useful action requires unavailable authority or explicit approval, an actual supplied limit is exhausted, or further iteration cannot produce decision-relevant information. Require observed recurrence before presenting recurrence as fact; otherwise label inference or opportunity.

A loop definition is data, not authority. Crafting/adapting does not execute. Running does not create a scheduler. Saving locally is not external publication. Publication retains the provider's actual current approval, ownership, licensing, authentication, attestation, and human-verification boundaries. Reuse external Loop Library infrastructure rather than cloning its marketplace, hosting, account, or voting system; EOG absorbs the client experience around that service.

### Hard Guards

Deterministic enforcement is reserved for boundaries where silent violation would corrupt authority or integrity. Hard guards may reject unauthorized action; stale/conflicting durable writes where the owner requires CAS/transactions/locks; stale evidence represented as current; canonical-owner violations; unsupported machine-readable completion claims; externally consequential acts without their real approval boundary; and protected-data leakage.

Hard guards constrain invalid actions. They do not choose architecture, abstractions, search depth, implementation strategy, reasoning depth, candidate ordering, or stopping points for the agent.

### Representation Policy

Natural engineering work comes first: the agent reasons naturally -> acts with existing tools -> tools produce observations -> retain only durable meaning worth keeping.

Optional representations include experience/decision records, goal/support graphs, candidate comparisons, evidence objects, loop definitions, and run receipts. Use them when they reduce ambiguity, improve handoff, protect integrity, or preserve materially useful provenance. Do not require them merely because EOG provides a schema. Schema is representation, not workflow. A structurally valid record is not automatically true.

### One Mental Model

Ordinary EOG use must not require the agent or user to decide whether this is UOG, whether Ponytail should run now, or whether it is time for Loopy. The single model is: Experience -> Choice -> Minimality -> Feedback -> Integrity.

UOG, Ponytail, and Loopy remain provenance and compatibility surfaces, not separate required mental models.

### Superset Contract

EOG may replace UOG, Ponytail, and Loopy only if Capability(EOG) includes Capability(UOG union Ponytail union Loopy) while ordinary conceptual and operational burden is lower than invoking the three independently. An EOG change that removes a useful upstream capability without a more general equivalent is a regression even when the result is smaller.

Every upstream capability must resolve to one of: absorbed, generalized, compatibility_alias, or external_service_reuse. A useful capability may not disappear merely because EOG prefers a different default.

### Capability and Evidence Are Separate

Do not conflate feature existence with verification status. Capability state is absent, mapped, implemented, or compatible. Evidence state is unverified, contract_verified, or native_verified. A capability may be fully implemented while native verification remains incomplete. Testing status must not distort the actual capability model.

### Native Lifecycle and Authority

This section owns EOG meaning; schemas, CLI, workflows, adapters, and MCP carriers are subordinate support. Reuse native AGENTS/instruction loading first. Add a native hook/rule/extension only for an actual delivery gap. Generated copies carry a source digest, not independent policy.

Installation/update preserves foreign settings and work through preview and exact old-content preconditions. Native tool permissions, canonical-owner transactions, and protected CI retain authority. EOG never grants permission. Missing evidence blocks the claim it is needed for, not unrelated safe investigation.

### Self-Application

EOG is subject to EOG. Before adding material EOG machinery ask: what useful agent failure does this prevent or capability does this add; can a concise heuristic already handle it; does a native owner already provide the boundary; is deterministic enforcement actually necessary; and does the mechanism remove more burden than it introduces? If there is no residual responsibility, do not add it.

The ideal EOG is not the system that controls the agent most. It is the smallest system that reliably helps a capable agent make better engineering decisions without taking judgment away from it.