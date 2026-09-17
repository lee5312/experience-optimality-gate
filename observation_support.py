"""Direct execution observations, not a truth oracle or a permission broker."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import tempfile
import time
import eog


def subjects(root, paths):
    if not paths or len(paths)!=len(set(paths)): raise ValueError('distinct explicit subject paths required')
    return [{'path':path,'sha256':eog.file_state(eog.confined(root,path))} for path in paths]


def observe(root, argv, paths, timeout=60, owner=None, revision=None):
    from library_support import SECRET
    if not argv or any(not isinstance(a,str) or '\0' in a for a in argv):
        raise ValueError('explicit command argv required; shell strings are not expanded')
    if SECRET.search(' '.join(argv)): raise ValueError('do not place credentials in recorded arguments')
    if not 0<timeout<=3600: raise ValueError('timeout must be between 0 and 3600 seconds')
    if bool(owner) != bool(revision): raise ValueError('owner and exact subject revision must be provided together')
    head=None
    if revision:
        head=eog.revision_sha(root,revision)
        if eog.git(root,'rev-parse','HEAD').decode().strip()!=head:
            raise ValueError('observation revision is not the current checkout')
    before=subjects(root,paths); started=time.monotonic(); timed_out=False
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            run=subprocess.run(argv,cwd=root,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
                               timeout=timeout,check=False,shell=False)
            code=run.returncode
        except subprocess.TimeoutExpired:
            code=None;timed_out=True
        stdout.seek(0);out=stdout.read(eog.MAX_BYTES+1)
        stderr.seek(0);err=stderr.read(eog.MAX_BYTES+1)
    truncated=len(out)>eog.MAX_BYTES or len(err)>eog.MAX_BYTES
    record={'schema':'eog-observation-1','observed_at':datetime.now(timezone.utc).isoformat(),
            'argv':argv,'exit_code':code,'timed_out':timed_out,'output_limit_exceeded':truncated,
            'duration_seconds':round(time.monotonic()-started,6),'before':before,'after':subjects(root,paths),
            'stdout_sha256':eog.digest(out),'stderr_sha256':eog.digest(err),
            'outcome':'passed' if code==0 and not truncated and not timed_out else 'failed',
            'policy_sha256':eog.policy(root)['policy_sha256'],
            'truth_verified':False,'permission_granted':False}
    if head:
        record['work_owner']=owner; record['subject_revision']=head
        if eog.git(root,'rev-parse','HEAD').decode().strip()!=head:
            record['outcome']='failed';record['checkout_changed']=True
    return record


def check_observations(root, record, expected):
    errors=[]
    if not isinstance(record,dict): raise ValueError('observation must be an object')
    if eog.digest(eog.dumps(record).encode())!=expected: errors.append('observation digest mismatch')
    if record.get('subject_revision'):
        try:
            if eog.git(root,'rev-parse','HEAD').decode().strip()!=record['subject_revision']:
                errors.append('observation checkout changed')
        except (OSError,ValueError): errors.append('observation checkout unavailable')
    if record.get('schema')!='eog-observation-1': errors.append('unknown observation schema')
    if record.get('policy_sha256')!=eog.policy(root)['policy_sha256']: errors.append('stale observation policy')
    if record.get('exit_code')!=0 or record.get('outcome')!='passed' or record.get('timed_out') is not False or record.get('output_limit_exceeded') is not False:
        errors.append('command did not complete successfully')
    rows=record.get('after')
    if not isinstance(rows,list) or not rows: errors.append('no observed subjects')
    else:
        paths=[r.get('path') for r in rows if isinstance(r,dict)]
        if len(paths)!=len(rows) or any(not isinstance(p,str) for p in paths) or len(set(paths))!=len(paths):
            errors.append('invalid observation subjects')
        else:
            for r in rows:
                try:
                    current=eog.file_state(eog.confined(root,r['path']))
                    if current!=r.get('sha256'): errors.append('subject changed: '+r['path'])
                except (OSError,ValueError): errors.append('subject unavailable or outside owner')
    return {'consistent':not errors,'errors':errors,'truth_verified':False,'permission_granted':False,
            'note':'Caller must bind the expected digest via its trusted CI/reviewer channel. A matching self-authored report is not independent truth or consumer acceptance.'}


def admission(root, record, observation_record, expected, owner, revision):
    result=check_observations(root,observation_record,expected)
    errors=list(result['errors'])
    if observation_record.get('work_owner')!=owner: errors.append('observation work owner mismatch')
    if observation_record.get('subject_revision')!=revision: errors.append('observation subject revision mismatch')
    if record.get('scope',{}).get('subject_revision')!=revision: errors.append('record subject revision mismatch')
    return dict(result,consistent=not errors,errors=errors,
                observation_digest=expected,
                coverage='Explicit subject files and one observed command only; not all acceptance checks or semantic truth.')
