"""Pinned procedure delivery for the user's existing agent, not another runtime."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ALIASES = {
    'ponytail': 'plan', 'ponytail-review': 'review', 'ponytail-audit': 'audit',
    'ponytail-debt': 'debt', 'ponytail-gain': 'impact', 'gain': 'impact',
    'ponytail-help': 'help', 'loopy': 'help', 'loop-library': 'help',
    'loop-repair': 'repair', 'loop-doctor': 'loop-audit', 'uog': 'plan',
}


def resolve_workflow(name):
    return ALIASES.get(name.lstrip('/'), name.lstrip('/'))


def compact_core(policy):
    # Compact cognitive guidance is valid only for the exact bundled policy.
    # Custom/amended policy is delivered in full rather than silently compressed.
    from eog import policy as read_policy
    if policy['policy_sha256'] != read_policy(HERE)['policy_sha256']:
        return policy['text']
    return (
        '## Experience Optimality Gate (EOG)\n'
        'EOG assists judgment; it is not a compulsory state machine. Experience before machinery. '
        'Requirements are not mechanisms. Existing solutions are first-class candidates.\n'
        'For material novelty, inspect only decision-relevant existing/native/installed/standard/'
        'product/OSS options and own only the residual responsibility. Prefer reuse/configure/'
        'compose/adapt/extend/build when experience and constraints hold.\n'
        'Compare feasible candidates without fake precision; investigate only uncertainty that can '
        'change feasibility, the non-dominated set, residual novelty, or commitment.\n'
        'Use useful feedback: observe, take one bounded action, verify, and continue only when new '
        'evidence can change the next action. Do not manufacture loops or ceremony.\n'
        'Hard guards are narrow: authority, write integrity, stale evidence, canonical ownership, '
        'unsupported machine-readable completion, external consequence, and protected data. '
        'They do not choose architecture or search depth.\n'
        'Component success is not consumer completion; structural validity is not truth or permission. '
        'Small deterministic edits need concise judgment, not a JSON form. Load a deep method only '
        'when it can change the decision or perform a requested operation.\n'
        'For material decisions or changed instructions, read the full current policy at '
        + policy['policy_path'] + '; sha256=' + policy['policy_sha256'] + '.\n'
    )


def references(workflow):
    """Load exact pinned text; a missing or modified reference is never silently skipped."""
    lock = json.loads((HERE/'reference-lock.json').read_text('utf-8'))['files']
    blocks = []
    for name in workflow.get('references', []):
        if name not in lock or Path(name).name != name:
            raise ValueError('unknown workflow reference')
        path = HERE/'skill'/'references'/name
        if path.is_symlink():
            raise ValueError('reference must not be a symlink')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != lock[name]['sha256']:
            raise ValueError('pinned workflow reference changed: '+name)
        blocks.append('## Preserved upstream procedure: '+name+'\n'
                      'Source: '+lock[name]['source']+'\n\n'+raw.decode('utf-8'))
    if not blocks:
        return ''
    return (
        '\n## Procedure integration contract\n'
        'The procedures below preserve the pinned upstream detail, not a running legacy '
        'installation. Apply them through this EOG operation on the SAME existing agent. '
        'Current user authority and root EOG policy take precedence. Upstream command names '
        'map to EOG operations (ponytail-gain -> impact; Loop Doctor -> loop-audit). '
        'Do not install another agent or invoke the original tools. Upstream off/lite/full/ultra '
        'are reference behavior, not permission to disable EOG constraints; proportional depth '
        'and explicit user Stop remain authoritative. Any quoted benchmark belongs to its '
        'original project and is NOT an EOG result. Follow EOG for supplied limits/no-progress '
        'where the pinned run guide differs. Native Loopy text is accepted without schema '
        'conversion; preserve its exact prompt/check/stop fields.\n\n'+'\n\n'.join(blocks)
    )
