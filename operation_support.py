"""Pinned procedure delivery for the user's existing agent, not another runtime."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ALIASES = {
    'ponytail': 'plan', 'ponytail-review': 'review', 'ponytail-audit': 'audit',
    'ponytail-debt': 'debt', 'ponytail-gain': 'impact', 'gain': 'impact',
    'ponytail-help': 'help', 'loopy': 'help', 'loop-library': 'help',
    'repair': 'loop-repair', 'loop-doctor': 'loop-audit',
}


def resolve_workflow(name):
    return ALIASES.get(name.lstrip('/'), name.lstrip('/'))


def compact_core(policy):
    return (
        '## Experience Optimality Gate (EOG)\n'
        'Consumer experience is the objective, including failure and continuity. '
        'Derive requirements; preserve explicit scope, constraints and authority.\n'
        '### Mandatory existing-wheel search\n'
        'Inspect relevant actual code, callers, standard/native capabilities and existing '
        'tools before material novelty. Compare reuse/configure/compose/adapt/extend/build; '
        'justify the residual gap. Do not turn a known local fix into a market survey.\n'
        'Prefer the lowest-burden solution that meets the required experience, not the '
        'fewest lines at the expense of security, data, accessibility or requested behavior. '
        'Observe, choose one bounded action, act, verify, then continue only with informative '
        'feedback. Re-read consequential state. Preserve unrelated work and user Stop.\n'
        'Component tests are not consumer completion; structural validity is not truth, '
        'permission or deployment. Bind observations to the current subject revision. '
        'Report failures and missing evidence rather than inventing success.\n'
        'Use the current agent and tools. Small deterministic edits need concise judgment, '
        'not a JSON form. Load the requested detailed operation only when needed. '
        'Do not invent a schedule, budget, metric, owner or approval. '
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
