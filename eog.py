#!/usr/bin/env python3
"""EOG operational support. No model, scheduler, permission broker, or task store."""
from __future__ import annotations
import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Any
from urllib.parse import urlparse
import urllib.request

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = Path.cwd()
VERSION = '1.1.0'
MAX_BYTES = 2 * 1024 * 1024
CATALOG = 'https://signals.forwardfuture.com/loop-library/catalog.json'
HEADING = '## Experience Optimality Gate (EOG)'
EVENTS = ('session', 'turn', 'resume', 'compact', 'delegate', 'verify')
HOOK_EVENTS = {
    'codex': {'SessionStart','UserPromptSubmit','SubagentStart','PostCompact'},
    'claude': {'SessionStart','UserPromptSubmit','SubagentStart'},
    'cursor': {'sessionStart','postToolUse'},
    'copilot': {'SessionStart'},
    'qoder': {'UserPromptSubmit'},
}
RULE_PATHS = {
    'cursor-rule': '.cursor/rules/eog.mdc', 'windsurf': '.windsurf/rules/eog.md',
    'cline': '.clinerules/eog.md', 'kiro': '.kiro/steering/eog.md',
    'qoder-rule': '.qoder/rules/eog.md', 'antigravity': '.agents/rules/eog.md',
    'copilot-rule': '.github/copilot-instructions.md', 'gemini': 'GEMINI.md',
    'junie': '.junie/guidelines.md', 'claude-rule': 'CLAUDE.md',
}
CONFIG_PATHS = {'codex':'.codex/hooks.json','claude':'.claude/settings.json',
                'cursor':'.cursor/hooks.json'}
MARK_START='<!-- BEGIN GENERATED EOG -->'
MARK_END='<!-- END GENERATED EOG -->'


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def strict_json(raw: bytes, limit: int=MAX_BYTES) -> Any:
    if len(raw)>limit: raise ValueError('JSON exceeds input limit')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result: raise ValueError('duplicate JSON key')
            result[k]=v
        return result
    def bad(_): raise ValueError('non-finite JSON number')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=bad)


def read_json(path: Path) -> Any:
    with path.open('rb') as f: return strict_json(f.read(MAX_BYTES+1))


def dumps(value: Any) -> str:
    return json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)


def policy(root: Path) -> dict[str,Any]:
    p=root/'AGENTS.md'
    with p.open('rb') as f: raw=f.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES: raise ValueError('policy exceeds input limit')
    text=raw.decode('utf-8-sig').replace('\r\n','\n').replace('\r','\n')
    # Ignore headings inside fenced examples: they are data, not policy owners.
    sections=[]; offset=0; fence=None
    for line in text.splitlines(keepends=True):
        stripped=line.strip()
        mark=re.match(r"^ {0,3}(`{3,}|~{3,})",line)
        if mark:
            token=mark.group(1)
            if fence is None: fence=(token[0],len(token))
            elif token[0]==fence[0] and len(token)>=fence[1] and not stripped[len(token):]: fence=None
        elif fence is None and line.startswith('## '):
            sections.append((offset,stripped))
        offset+=len(line)
    matches=[i for i,x in enumerate(sections) if x[1]==HEADING]
    if len(matches)!=1: raise ValueError('exactly one canonical EOG section required')
    i=matches[0]; start=sections[i][0]
    stop=sections[i+1][0] if i+1<len(sections) else len(text)
    body=text[start:stop].rstrip()+'\n'
    return {'version':VERSION,'policy_sha256':digest(body.encode()),
            'policy_path':str(p.resolve()),'policy_bytes':len(body.encode()),
            'agents_bytes':len(raw),'text':body}


def workflows() -> dict[str,Any]:
    return read_json(HERE/'workflows.json')['workflows']


def instructions(root: Path, workflow: str, event: str='turn') -> str:
    from operation_support import compact_core, references, resolve_workflow
    if event not in EVENTS: raise ValueError('unsupported context event')
    workflow=resolve_workflow(workflow)
    p=policy(root); w=workflows()
    if workflow not in w: raise ValueError('unknown EOG workflow')
    return (f"EOG {VERSION} | policy_sha256={p['policy_sha256']} | event={event}\n"
            +compact_core(p)+'\n## Requested EOG operation: '+w[workflow]['title']+'\n'
            +w[workflow]['instructions']+'\n'+references(w[workflow]))


def refresh(root: Path) -> str:
    from operation_support import compact_core
    return compact_core(policy(root))


def initialize(root: Path, expected: str|None=None, apply: bool=False) -> dict[str,Any]:
    target=confined(root,'AGENTS.md')
    before=file_state(target)
    text=target.read_bytes().decode('utf-8-sig') if target.exists() else ''
    if HEADING in text:
        policy(root)  # Reject duplicates/malformed owners rather than overwrite them.
        return {'path':'AGENTS.md','applied':False,'already_configured':True,'before_sha256':before}
    raw=(text+('\n\n' if text else '')+policy(HERE)['text']).encode()
    if not apply:
        return {'path':'AGENTS.md','applied':False,'before_sha256':before,'after_sha256':digest(raw),'proposed':raw.decode()}
    if expected is None: raise ValueError('--expected is required for writes')
    with write_lock(target): sha=atomic_write(target,raw,expected)
    return {'path':'AGENTS.md','applied':True,'sha256':sha,'native_loading_verified':False}


def hook(root: Path, host: str, event: str, data: Any) -> dict[str,Any]:
    if not isinstance(data,dict): raise ValueError('hook input must be an object')
    if host not in HOOK_EVENTS or event not in HOOK_EVENTS[host]:
        raise ValueError('event does not support EOG context on this host')
    if data.get('hook_event_name',event)!=event: raise ValueError('hook event mismatch')
    p=policy(root)
    # Never read an untrusted transcript path or use prompt/cwd as policy authority.
    # Native AGENTS/rules carry the full core. A bounded refresh avoids spilling
    # an entire constitution into the context on every turn.
    text=(f"EOG {VERSION}; canonical={p['policy_path']}; sha256={p['policy_sha256']}. "
          'Before material decisions use the current EOG: consumer experience first; '
          'ACTUALLY SEARCH existing wheels and justify each residual novel part; '
          'retain goal/constraint traceability, bounded feedback and consumer acceptance. '
          'Load the canonical section if absent or its digest changed. '
          'Use the same existing agent, not legacy Ponytail/Loopy installations. '
          'Carry current task, authority, subject revision, gaps and stops into delegation. '
          'A successful hook is not permission or proof of compliance.')
    if event in ('SubagentStart','PostCompact') or data.get('source') in ('resume','compact'):
        text+=' Re-read the exact parent handoff/current work owner; never substitute another task.'
    if event in ('SessionStart','sessionStart','SubagentStart','PostCompact') or data.get('source') in ('resume','compact') or host=='qoder':
        text+='\n\n'+p['text']
    if host=='cursor': return {'additional_context':text}
    if host=='copilot': return {'additionalContext':text}
    out={'hookSpecificOutput':{'hookEventName':event,'additionalContext':text}}
    return out


def stage_check(record: Any, stage: str, revision: str, owner: str) -> dict[str,Any]:
    from validate import validate_record
    if stage not in ('design','completion'): raise ValueError('unknown gate stage')
    errors=validate_record(record)
    if not errors:
        if record['scope']['subject_revision']!=revision: errors.append('subject revision mismatch')
        if record['scope']['work_owner']!=owner: errors.append('work owner mismatch')
        if record['decision']['status']!='design_pass': errors.append('design decision is not ready')
        if stage=='completion' and record['execution']['outcome'] not in ('success','clean_noop'):
            errors.append('consumer completion is not evidenced')
    return {'consistent':not errors,'stage':stage,'errors':errors,
            'truth_verified':False,'permission_granted':False}


def handoff(root: Path, record: Any, owner: str, revision: str,
            authority_ref: str, stops: list[str]) -> dict[str,Any]:
    from validate import validate_record
    errors=validate_record(record)
    if errors: raise ValueError('invalid EOG record: '+'; '.join(errors[:5]))
    if record['scope']['work_owner']!=owner or record['scope']['subject_revision']!=revision:
        raise ValueError('handoff owner/revision mismatch')
    if not authority_ref.strip() or not stops or any(not s.strip() for s in stops):
        raise ValueError('authority reference and stop conditions required')
    p=policy(root)
    packet={'schema':'eog-handoff-1','policy_sha256':p['policy_sha256'],
            'scope':record['scope'],'authority_ref':authority_ref,'stop_conditions':stops,
            'record':record,'permission_granted':False}
    packet['packet_sha256']=digest(dumps(packet).encode())
    return packet


def verify_handoff(root: Path, packet: Any, owner: str, revision: str) -> dict[str,Any]:
    if not isinstance(packet,dict): raise ValueError('handoff must be object')
    copy=dict(packet); recorded=copy.pop('packet_sha256',None)
    if digest(dumps(copy).encode())!=recorded: raise ValueError('packet digest mismatch')
    if packet.get('policy_sha256')!=policy(root)['policy_sha256']: raise ValueError('stale policy')
    if packet.get('schema')!='eog-handoff-1': raise ValueError('unknown handoff version')
    rebuilt=handoff(root,packet['record'],owner,revision,packet['authority_ref'],packet['stop_conditions'])
    if rebuilt!=packet: raise ValueError('handoff changed/extra data')
    return {'consistent':True,'truth_verified':False,'permission_granted':False}


def git(root: Path,*args: str) -> bytes:
    r=subprocess.run(['git','-C',str(root),*args],capture_output=True,timeout=30,check=False)
    if r.returncode: raise ValueError('native Git operation failed: '+r.stderr.decode(errors='replace')[:250])
    return r.stdout


def revision_sha(root: Path, ref: str) -> str:
    if not re.fullmatch(r'[0-9a-fA-F]{7,40}',ref): raise ValueError('an exact Git commit SHA is required')
    return git(root,'rev-parse','--verify',ref+'^{commit}').decode().strip()


def source_debt(root: Path) -> dict[str,Any]:
    rows=[]; skipped=[]
    paths=git(root,'ls-files','-z').split(b'\0')
    for raw in paths:
        if not raw: continue
        name=os.fsdecode(raw); p=root/name
        if p.is_symlink() or not p.is_file(): continue
        if any(x in {'.git','node_modules','vendor','dist','build'} for x in p.relative_to(root).parts): continue
        if p.stat().st_size>MAX_BYTES: skipped.append(name); continue
        try: text=p.read_text('utf-8')
        except (UnicodeError,OSError): continue
        for n,line in enumerate(text.splitlines(),1):
            m=re.match(r'^\s*(?:#|//|/\*|\*|--|;)\s*(ponytail|eog):\s*(.+?)\s*(?:\*/)?$',line,re.I)
            if m:
                marker,body=m.groups()
                # Legacy prose is deliberately not guessed into a schema.
                explicit=re.search(r'(?:trigger|revisit|upgrade)\s*:\s*(.+)',body,re.I)
                rows.append({'file':name,'line':n,'marker':marker.lower(),'text':body,
                             'trigger':explicit.group(1) if explicit else None,
                             'needs_semantic_trigger_review':explicit is None})
    return {'markers':rows,'count':len(rows),'unresolved_trigger_count':sum(r['trigger'] is None for r in rows),
            'skipped_large_files':skipped,'scan':'tracked text only; no automatic deletion','truth_verified':False}


def impact(root: Path, before: str, after: str) -> dict[str,Any]:
    a=revision_sha(root,before); b=revision_sha(root,after)
    raw=git(root,'diff','--numstat','--no-renames',a,b,'--').decode('utf-8','replace')
    added=removed=binary=0; files=[]
    for line in raw.splitlines():
        plus,minus,name=line.split('\t',2)
        if plus=='-': binary+=1
        else: added+=int(plus); removed+=int(minus)
        files.append({'path':name,'added':None if plus=='-' else int(plus),
                      'removed':None if minus=='-' else int(minus)})
    return {'before':a,'after':b,'added':added,'removed':removed,'binary_files':binary,
            'files':files,'savings_claim':None,'note':'Observed Git delta, not utility or counterfactual savings.'}


class SameOriginRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        u=urlparse(newurl)
        if u.scheme!='https' or u.hostname!='signals.forwardfuture.com' or u.port not in (None,443):
            raise ValueError('catalog redirect leaves approved public origin')
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def catalog() -> dict[str,Any]:
    # No arbitrary URL, credentials, local network endpoint, or automatic POST.
    request=urllib.request.Request(CATALOG,headers={'User-Agent':'EOG/1.1 catalog reader','Accept':'application/json'})
    with urllib.request.build_opener(SameOriginRedirect()).open(request,timeout=20) as response:
        raw=response.read(8*1024*1024+1)
        if len(raw)>8*1024*1024: raise ValueError('catalog exceeds transport limit')
    # Catalog has a larger transport limit but uses the same strict decoder.
    body=strict_json(raw,8*1024*1024)
    if not isinstance(body,(dict,list)): raise ValueError('catalog must be object or array')
    return {'source':CATALOG,'fetched_at':datetime.now(timezone.utc).isoformat(),
            'sha256':digest(raw),'untrusted_reference_data':True,'catalog':body}


def check_loop(loop: Any) -> list[str]:
    from jsonschema import Draft202012Validator
    schema=read_json(HERE/'loop.schema.json')
    errors=[e.message for e in Draft202012Validator(schema).iter_errors(loop)]
    if errors:return errors
    if loop['boundary']['kind']!='no_progress' and not loop['boundary'].get('source'):
        errors.append('finite boundary needs its actual user/definition source')
    return errors


def file_state(p: Path) -> str:
    if p.is_symlink(): raise ValueError('refuse symlink target')
    if not p.exists(): return 'absent'
    if not p.is_file(): raise ValueError('target must be regular file')
    if p.stat().st_size>MAX_BYTES: raise ValueError('target exceeds input limit')
    return digest(p.read_bytes())


def confined(root: Path, relative: str) -> Path:
    pure=Path(relative)
    if pure.is_absolute() or '..' in pure.parts: raise ValueError('relative path inside owner required')
    p=root/pure
    for part in [p,*p.parents]:
        if part==root.parent: break
        if part.is_symlink(): raise ValueError('symlink in managed path')
    if not p.resolve().is_relative_to(root.resolve()): raise ValueError('path outside owner')
    return p


@contextlib.contextmanager
def write_lock(p: Path):
    p.parent.mkdir(parents=True,exist_ok=True)
    lock=p.with_name('.'+p.name+'.eog-write-lock')
    # Cooperative lock only; native external editors must retain their own CAS.
    fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        os.write(fd,str(os.getpid()).encode()); os.close(fd); fd=-1
        yield
    finally:
        if fd!=-1:os.close(fd)
        lock.unlink()


def atomic_write(p: Path, raw: bytes, expected: str) -> str:
    if len(raw)>MAX_BYTES:raise ValueError('output exceeds managed file limit')
    if file_state(p)!=expected: raise ValueError('stale destination; re-read before writing')
    fd,temp=tempfile.mkstemp(prefix='.'+p.name+'.eog-',dir=p.parent)
    try:
        mode=p.stat().st_mode & 0o777 if p.exists() else 0o600
        os.fchmod(fd,mode) if hasattr(os,'fchmod') else None
        with os.fdopen(fd,'wb') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
        if file_state(p)!=expected: raise ValueError('destination changed during staging')
        os.replace(temp,p)
    finally:
        if os.path.exists(temp):os.unlink(temp)
    if p.read_bytes()!=raw:raise OSError('write readback mismatch')
    return digest(raw)


def saved_loops(text: str) -> list[dict[str,Any]]:
    result=[]; fence=None; capture=False; content=[]
    for line in text.splitlines(keepends=True):
        match=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',line.rstrip('\r\n'))
        if fence is None:
            if match:
                token,info=match.groups();fence=(token[0],len(token))
                capture=info.strip()=='eog-loop';content=[]
        elif match and match[1][0]==fence[0] and len(match[1])>=fence[1] and not match[2].strip():
            if capture: result.append(strict_json(''.join(content).encode()))
            fence=None;capture=False;content=[]
        elif capture: content.append(line)
    if capture:raise ValueError('unterminated structured loop block')
    return result


def save_loop(root: Path, relative: str, loop: Any, expected: str) -> dict[str,Any]:
    errors=check_loop(loop)
    if errors: raise ValueError('invalid loop: '+'; '.join(errors[:5]))
    p=confined(root,relative)
    with write_lock(p):
        if file_state(p)!=expected:raise ValueError('stale saved-loop document')
        text=p.read_bytes().decode('utf-8') if p.exists() else '# Project loops\n'
        if any(v.get('id')==loop['id'] for v in saved_loops(text)):
            raise ValueError('loop ID already exists; use owner review for revision')
        raw=(text+'\n\n```eog-loop\n'+dumps(loop)+'\n```\n').encode()
        if len(raw)>MAX_BYTES:raise ValueError('saved-loop document exceeds limit')
        sha=atomic_write(p,raw,expected)
    return {'path':relative,'sha256':sha,'saved':loop['id'],'published':False}


def hook_command(root: Path, host: str, event: str) -> str:
    parts=[sys.executable,str(HERE/'eog.py'),'--root',str(root),'hook','--host',host,'--event',event]
    # POSIX native hook shells. Windows users select rule delivery or render a
    # native PowerShell invocation explicitly; do not claim bash quoting works there.
    if os.name=='nt': raise ValueError('native Windows hook install not verified; use project-rule delivery')
    return shlex.join(parts)


def adapter(root: Path, host: str, before: bytes) -> tuple[str,bytes]:
    p=policy(root)
    if host in CONFIG_PATHS:
        old=strict_json(before) if before else {}
        if not isinstance(old,dict):raise ValueError('native config must be object')
        table=old.setdefault('hooks',{})
        if not isinstance(table,dict):raise ValueError('native hooks must be object')
        if host=='cursor':
            if old.get('version',1)!=1:raise ValueError('unsupported Cursor hook config version')
            old['version']=1
        for event in sorted(HOOK_EVENTS[host]):
            entries=table.setdefault(event,[])
            if not isinstance(entries,list):raise ValueError('native hook event must be array')
            command=hook_command(root,host,event)
            item={'command':command} if host=='cursor' else {'hooks':[{'type':'command','command':command,'timeout':5}]}
            if host=='codex':item['hooks'][0]['additionalContextLimit']=0
            if item not in entries:entries.append(item)
        return CONFIG_PATHS[host],(dumps(old)+'\n').encode()
    if host in RULE_PATHS:
        text=before.decode('utf-8') if before else ''
        if host=='cursor-rule' and text and not re.search(r'^alwaysApply:\s*true\s*$',text,re.M):
            raise ValueError('existing Cursor rule is not alwaysApply; preserve it and review native configuration')
        if text.count(MARK_START)!=text.count(MARK_END) or text.count(MARK_START)>1:
            raise ValueError('malformed generated EOG block')
        block=MARK_START+'\n'+p['text']+MARK_END
        if MARK_START in text:
            a=text.index(MARK_START);b=text.index(MARK_END)+len(MARK_END)
            text=text[:a]+block+text[b:]
        else:
            if not text and host=='cursor-rule':text='---\ndescription: Experience-first engineering gate\nalwaysApply: true\n---\n'
            if not text and host=='kiro':text='---\ninclusion: always\n---\n'
            if not text and host=='windsurf':text='---\ntrigger: always_on\n---\n'
            text=text.rstrip()+'\n\n'+block+'\n'
        return RULE_PATHS[host],text.encode()
    raise ValueError('host uses native AGENTS/skill or an external adapter; no implicit install')


def install(root: Path, host: str, expected: str|None, apply: bool) -> dict[str,Any]:
    rel={**CONFIG_PATHS,**RULE_PATHS}.get(host)
    if not rel:raise ValueError('unsupported managed host')
    p=confined(root,rel)
    if not apply:
        file_state(p)
        before=p.read_bytes() if p.exists() else b''
        _,after=adapter(root,host,before)
        return {'path':rel,'before_sha256':file_state(p),'after_sha256':digest(after),
                'proposed':after.decode(),'applied':False}
    if expected is None:raise ValueError('--expected is required for writes')
    with write_lock(p):
        if file_state(p)!=expected:raise ValueError('stale host config')
        before=p.read_bytes() if p.exists() else b''
        _,after=adapter(root,host,before)
        sha=atomic_write(p,after,expected)
    return {'path':rel,'sha256':sha,'applied':True,'native_loading_verified':False}


def uninstall(root: Path, host: str, expected: str) -> dict[str,Any]:
    rel={**CONFIG_PATHS,**RULE_PATHS}.get(host)
    if not rel:raise ValueError('unsupported managed host')
    p=confined(root,rel)
    with write_lock(p):
        if file_state(p)!=expected:raise ValueError('stale host config')
        before=p.read_bytes()
        if host in RULE_PATHS:
            text=before.decode(); a=text.find(MARK_START);b=text.find(MARK_END)
            if a<0 or b<a or text.count(MARK_START)!=1 or text.count(MARK_END)!=1:raise ValueError('no single managed EOG block')
            actual=text[a:b+len(MARK_END)]
            approved=MARK_START+'\n'+policy(root)['text']+MARK_END
            if actual!=approved:raise ValueError('managed block edited or stale; review before uninstall')
            after=(text[:a]+text[b+len(MARK_END):]).encode()
        else:
            data=strict_json(before)
            for event in sorted(HOOK_EVENTS[host]):
                entries=data.get('hooks',{}).get(event,[])
                command=hook_command(root,host,event)
                item={'command':command} if host=='cursor' else {'hooks':[{'type':'command','command':command,'timeout':5}]}
                if host=='codex':item['hooks'][0]['additionalContextLimit']=0
                if item not in entries:raise ValueError('managed hook differs; refuse implicit removal')
                data['hooks'][event]=[v for v in entries if v!=item]
            after=(dumps(data)+'\n').encode()
        sha=atomic_write(p,after,expected)
    return {'path':rel,'sha256':sha,'removed_only':'exact managed EOG entries','legacy_tools_removed':False}


def doctor(root: Path, host: str|None) -> dict[str,Any]:
    p=policy(root); out={k:v for k,v in p.items() if k!='text'}
    out.update({'native_loading_verified':False,'model_compliance_verified':False,
                'warning':'Inspect actual global/nested overrides and total native instruction budget.'})
    if host:
        rel={**CONFIG_PATHS,**RULE_PATHS}.get(host)
        if rel:
            target=confined(root,rel)
            raw=target.read_bytes() if target.exists() else b''
            _,wanted=adapter(root,host,raw)
            out['adapter']={'path':rel,'present':target.exists(),'configured_and_current':bool(raw) and raw==wanted}
    return out


def replacement_check(root: Path, receipt: Any) -> dict[str,Any]:
    manifest=read_json(HERE/'capabilities.json')
    errors=[]
    if not isinstance(receipt,dict):raise ValueError('replacement receipt must be object')
    if receipt.get('policy_sha256')!=policy(root)['policy_sha256']:errors.append('policy digest mismatch')
    if receipt.get('source_version')!=VERSION:errors.append('source version mismatch')
    required={c['id'] for c in manifest['capabilities'] if c['disposition']!='policy_change'}
    cases=receipt.get('capability_evidence',[])
    if not isinstance(cases,list):raise ValueError('capability_evidence must be array')
    ids=[c.get('capability') for c in cases if isinstance(c,dict)]
    if len(ids)!=len(set(ids)):errors.append('duplicate capability evidence')
    passed={c.get('capability') for c in cases if isinstance(c,dict) and c.get('result')=='passed'
            and c.get('locator') and c.get('kind') in ('actual_operation','reviewed_source_and_operation')}
    errors.extend('missing actual capability evidence: '+c for c in sorted(required-passed))
    hosts=receipt.get('hosts',[])
    if not isinstance(hosts,list) or not hosts:errors.append('actual host inventory is missing')
    else:
        if len({h.get('id') for h in hosts if isinstance(h,dict)})!=len(hosts):errors.append('invalid or duplicate host evidence')
        if not any(isinstance(h,dict) and h.get('required',True) for h in hosts):errors.append('no required host was tested')
        for h in hosts:
            if not isinstance(h,dict):errors.append('invalid host evidence');continue
            if h.get('required',True) and not (h.get('loading')=='passed' and h.get('workflow')=='passed'
              and h.get('legacy_absent_trial')=='passed' and h.get('locator') and h.get('kind')=='native_host'):
                errors.append('host replacement unverified: '+str(h.get('id')))
    for field in ['legacy_inventory_reviewed','saved_work_preserved','rollback_verified']:
        if receipt.get(field) is not True:errors.append(field+' required')
    # Deliberate policy changes must be visible, not counted as copied features.
    required_changes={c['id'] for c in manifest['capabilities'] if c['disposition']=='policy_change'}
    if not required_changes<=set(receipt.get('accepted_policy_changes',[])):
        errors.append('policy changes require explicit disposition acknowledgment')
    return {'receipt_consistent':not errors,'replacement_authorized':False,
            'truth_verified':False,'errors':errors,
            'note':'Only checks submitted evidence. Actual owner approval and source review remain required.'}



def pretool(root: Path, record: Any, expected_record: str, stage: str,
            revision: str, owner: str, host: str, *, expected_policy: str) -> dict[str,Any]:
    """Optional native admission adapter for a task-bound managed boundary.

    The native caller supplies the reviewed record hash/owner/revision, NOT the
    untrusted tool payload. Do not install a catch-all shell-effect classifier.
    A valid record returns no ALLOW decision; normal host authorization continues.
    """
    if host not in ('codex','claude','cursor'):raise ValueError('unsupported guard host')
    try:
        if policy(root)['policy_sha256']!=expected_policy:raise ValueError('policy digest mismatch')
        if digest(dumps(record).encode())!=expected_record:raise ValueError('record digest mismatch')
        result=stage_check(record,stage,revision,owner)
        why='; '.join(result['errors'][:4])
        valid=result['consistent']
    except Exception as e:
        # Missing validator/dependency must also produce a native deny, not fail-open.
        why=type(e).__name__+': admission evidence unavailable or inconsistent';valid=False
    if valid:return {}  # No new authority; host's permission checks still apply.
    reason='EOG task-bound admission failed: '+why
    if host=='cursor':return {'permission':'deny','user_message':reason}
    return {'hookSpecificOutput':{'hookEventName':'PreToolUse',
            'permissionDecision':'deny','permissionDecisionReason':reason}}


def check_receipt(receipt: Any) -> list[str]:
    from jsonschema import Draft202012Validator
    schema=read_json(HERE/'receipt.schema.json')
    errors=[e.message for e in Draft202012Validator(schema).iter_errors(receipt)]
    if errors:return errors
    loop=receipt['definition'];errors.extend(check_loop(loop))
    if errors:return errors
    if receipt['definition_sha256']!=digest(dumps(loop).encode()):errors.append('definition digest mismatch')
    steps=receipt['steps']
    if [s['sequence'] for s in steps]!=list(range(1,len(steps)+1)):errors.append('steps must be ordered without gaps')
    for step in steps:
        try:
            if datetime.fromisoformat(step['observed_at']).tzinfo is None:raise ValueError()
        except ValueError:errors.append('observation timestamp must include timezone')
    outcome=receipt['outcome']
    if outcome in ('success','clean_noop'):
        acceptance=receipt.get('acceptance')
        if not acceptance or acceptance['result']!='passed':errors.append('consumer acceptance missing or failed')
        elif acceptance['subject_revision']!=receipt['subject_revision']:errors.append('acceptance revision mismatch')
        if steps and steps[-1]['verification']['result']!='passed':errors.append('latest step did not pass')
    if outcome=='clean_noop' and any(s['changed'] for s in steps):errors.append('no-op receipt contains a mutation')
    if outcome=='exhausted' and loop['boundary']['kind']!='user_limit':errors.append('exhaustion requires supplied limit')
    if outcome=='stagnated' and (not steps or steps[-1]['next_learning'].strip()):errors.append('stagnation must record no remaining informative next action')
    return sorted(set(errors))


def main() -> int:
    # CLI pipes and MCP carry UTF-8 on every platform, independent of console locale.
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8',newline='\n')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=DEFAULT_ROOT)
    sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prompt');p.add_argument('--workflow',default='plan');p.add_argument('--event',choices=EVENTS,default='turn')
    p=sub.add_parser('hook');p.add_argument('--host',choices=sorted(HOOK_EVENTS),required=True);p.add_argument('--event',required=True)
    p=sub.add_parser('gate');p.add_argument('record',type=Path);p.add_argument('--stage',choices=['design','completion'],required=True);p.add_argument('--revision',required=True);p.add_argument('--owner',required=True);p.add_argument('--observations',type=Path);p.add_argument('--observations-sha256')
    p=sub.add_parser('validate-stdin')
    p=sub.add_parser('library-stdin')
    sub.add_parser('manifest')
    sub.add_parser('status')
    sub.add_parser('refresh')
    p=sub.add_parser('init');p.add_argument('--expected');p.add_argument('--apply',action='store_true')
    p=sub.add_parser('record-digest');p.add_argument('record',type=Path)
    p=sub.add_parser('pretool');p.add_argument('record',type=Path);p.add_argument('--record-sha256',required=True);p.add_argument('--policy-sha256',required=True);p.add_argument('--owner',required=True);p.add_argument('--revision',required=True);p.add_argument('--stage',choices=['design','completion'],default='design');p.add_argument('--host',choices=['codex','claude','cursor'],required=True)
    p=sub.add_parser('observe');p.add_argument('--subject',action='append',required=True);p.add_argument('--timeout',type=float,default=60);p.add_argument('--owner');p.add_argument('--revision');p.add_argument('argv',nargs=argparse.REMAINDER)
    p=sub.add_parser('check-observations');p.add_argument('record',type=Path);p.add_argument('--expected',required=True)
    p=sub.add_parser('check-receipt');p.add_argument('record',type=Path)
    for name in ['handoff','verify-handoff']:
        p=sub.add_parser(name);p.add_argument('record',type=Path);p.add_argument('--owner',required=True);p.add_argument('--revision',required=True)
        if name=='handoff':p.add_argument('--authority-ref',required=True);p.add_argument('--stop',action='append',required=True)
    sub.add_parser('debt')
    p=sub.add_parser('impact');p.add_argument('--before',required=True);p.add_argument('--after',required=True)
    sub.add_parser('catalog')
    p=sub.add_parser('find-loop');p.add_argument('query');p.add_argument('--path',default='LOOPS.md');p.add_argument('--local-only',action='store_true')
    p=sub.add_parser('compare-loops');p.add_argument('records',type=Path)
    p=sub.add_parser('save-text');p.add_argument('--title',required=True);p.add_argument('--explanation',required=True);p.add_argument('--prompt-file',type=Path,required=True);p.add_argument('--expected',required=True);p.add_argument('--path',default='LOOPS.md');p.add_argument('--source');p.add_argument('--source-modified');p.add_argument('--replace-entry')
    p=sub.add_parser('prepare-publication');p.add_argument('record',type=Path)
    p=sub.add_parser('verify-publication');p.add_argument('slug');p.add_argument('--prompt-sha256',required=True)
    p=sub.add_parser('check-loop');p.add_argument('record',type=Path)
    p=sub.add_parser('saved-loops');p.add_argument('--path',default='LOOPS.md')
    p=sub.add_parser('save-loop');p.add_argument('record',type=Path);p.add_argument('--path',default='LOOPS.md');p.add_argument('--expected',required=True)
    p=sub.add_parser('install');p.add_argument('--host',choices=sorted({**CONFIG_PATHS,**RULE_PATHS}),required=True);p.add_argument('--expected');p.add_argument('--apply',action='store_true')
    p=sub.add_parser('uninstall');p.add_argument('--host',choices=sorted({**CONFIG_PATHS,**RULE_PATHS}),required=True);p.add_argument('--expected',required=True)
    p=sub.add_parser('doctor');p.add_argument('--host',choices=sorted({**CONFIG_PATHS,**RULE_PATHS}))
    p=sub.add_parser('replacement-check');p.add_argument('record',type=Path)
    a=ap.parse_args();root=a.root.resolve();code=0
    try:
        if a.command=='prompt':print(instructions(root,a.workflow,a.event));return 0
        elif a.command=='refresh':print(refresh(root));return 0
        elif a.command=='init':result=initialize(root,a.expected,a.apply)
        elif a.command=='hook': result=hook(root,a.host,a.event,strict_json(sys.stdin.buffer.read(MAX_BYTES+1)))
        elif a.command=='record-digest':result={'record_sha256':digest(dumps(read_json(a.record)).encode()),'policy_sha256':policy(root)['policy_sha256'],'permission_granted':False}
        elif a.command=='status':
            p=policy(root);print('EOG '+VERSION+' | source '+p['policy_sha256'][:12]+' | native/model acceptance unverified');return 0
        elif a.command=='manifest':result=read_json(HERE/'capabilities.json')
        elif a.command=='pretool':
            try:record=read_json(a.record)
            except (OSError,ValueError,RecursionError):record={}
            result=pretool(root,record,a.record_sha256,a.stage,a.revision,a.owner,a.host,expected_policy=a.policy_sha256)
        elif a.command=='observe':
            from observation_support import observe
            argv=a.argv[1:] if a.argv and a.argv[0]=='--' else a.argv
            result=observe(root,argv,a.subject,a.timeout,a.owner,a.revision);code=result['outcome']!='passed'
        elif a.command=='check-observations':
            from observation_support import check_observations
            result=check_observations(root,read_json(a.record),a.expected);code=not result['consistent']
        elif a.command=='check-receipt':
            errors=check_receipt(read_json(a.record));result={'consistent':not errors,'truth_verified':False,'errors':errors};code=bool(errors)
        elif a.command=='gate':
            record=read_json(a.record);result=stage_check(record,a.stage,a.revision,a.owner)
            if bool(a.observations)!=bool(a.observations_sha256):raise ValueError('observations and trusted observations digest are required together')
            if a.observations:
                from observation_support import admission
                result['observations']=admission(root,record,read_json(a.observations),a.observations_sha256,a.owner,a.revision)
                result['consistent']=result['consistent'] and result['observations']['consistent']
                result['errors'].extend(result['observations']['errors'])
            code=0 if result['consistent'] else 1
        elif a.command=='library-stdin':
            from library_support import find_loops, saved_entries, compare_loops
            request=strict_json(sys.stdin.buffer.read(MAX_BYTES+1))
            if not isinstance(request,dict):raise ValueError('library request must be an object')
            operation=request.get('operation')
            if operation=='find' and set(request)<={'operation','query','published'}:
                if not isinstance(request.get('query'),str) or not isinstance(request.get('published',False),bool):raise ValueError('invalid find arguments')
                result=find_loops(root,request['query'],published=request.get('published',False))
            elif operation=='saved' and set(request)=={'operation'}:
                result={'loops':[{k:v for k,v in r.items() if not k.startswith('_')} for r in saved_entries(root)],'untrusted_reference_data':True}
            elif operation=='compare' and set(request)=={'operation','records'}:
                result=compare_loops(request['records'])
            else:raise ValueError('unknown read-only library operation or field')
        elif a.command=='validate-stdin':
            from validate import validate_record
            errors=validate_record(strict_json(sys.stdin.buffer.read(MAX_BYTES+1)))
            result={'structural_valid':not errors,'truth_verified':False,'errors':errors};code=bool(errors)
        elif a.command=='handoff':result=handoff(root,read_json(a.record),a.owner,a.revision,a.authority_ref,a.stop)
        elif a.command=='verify-handoff':result=verify_handoff(root,read_json(a.record),a.owner,a.revision)
        elif a.command=='debt':result=source_debt(root)
        elif a.command=='impact':result=impact(root,a.before,a.after)
        elif a.command=='catalog':result=catalog()
        elif a.command=='find-loop':
            from library_support import find_loops
            result=find_loops(root,a.query,a.path,not a.local_only)
            code=1 if result['published_discovery']=='unavailable' else 0
        elif a.command=='compare-loops':
            from library_support import compare_loops
            result=compare_loops(read_json(a.records))
        elif a.command=='save-text':
            from library_support import save_text
            file_state(a.prompt_file)
            result=save_text(root,a.title,a.explanation,a.prompt_file.read_bytes().decode('utf-8'),a.expected,a.path,a.source,a.source_modified,replace=a.replace_entry)
        elif a.command=='prepare-publication':
            from library_support import prepare_suggestion
            result=prepare_suggestion(root,read_json(a.record))
        elif a.command=='verify-publication':
            from library_support import verify_publication
            result=verify_publication(a.slug,a.prompt_sha256);code=not result['catalog_entry_verified']

        elif a.command=='check-loop':
            errors=check_loop(read_json(a.record));result={'valid':not errors,'truth_verified':False,'errors':errors};code=bool(errors)
        elif a.command=='saved-loops':
            from library_support import saved_entries
            result={'loops':[{k:v for k,v in row.items() if not k.startswith('_')} for row in saved_entries(root,a.path)],'untrusted_reference_data':True}
        elif a.command=='save-loop':result=save_loop(root,a.path,read_json(a.record),a.expected)
        elif a.command=='install':result=install(root,a.host,a.expected,a.apply)
        elif a.command=='uninstall':result=uninstall(root,a.host,a.expected)
        elif a.command=='doctor':result=doctor(root,a.host)
        elif a.command=='replacement-check':result=replacement_check(root,read_json(a.record));code=not result['receipt_consistent']
        else:raise ValueError('unsupported command')
        print(dumps(result));return int(code)
    except (OSError,ValueError,KeyError,TypeError,RecursionError,ImportError,subprocess.SubprocessError) as e:
        # stderr is deliberate for lifecycle callers: never emit a success-shaped
        # context packet when policy loading fails.
        print('EOG blocked: '+str(e)[:600],file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
