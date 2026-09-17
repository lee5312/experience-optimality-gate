"""Lossless native-text loop storage and real catalog discovery; never executes prompts."""
from __future__ import annotations
from datetime import date
import re
from pathlib import Path
from urllib.parse import urlparse
import eog

SECRET = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{24,}|sk-(?:proj-)?[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16})|\bBearer\s+[A-Za-z0-9._~+/-]{16,}', re.I)


def safe_text(text: str) -> None:
    if not isinstance(text, str) or not text.strip():
        raise ValueError('nonempty accepted text required')
    if len(text.encode('utf-8')) > eog.MAX_BYTES:
        raise ValueError('text exceeds managed file limit')
    if SECRET.search(text):
        raise ValueError('secret-shaped content: sanitize before saving or publishing')


def source_url(value: str) -> str:
    u = urlparse(value)
    if u.scheme not in ('http', 'https') or not u.hostname or u.username or u.password:
        raise ValueError('public HTTP(S) source URL without credentials required')
    if u.query or u.fragment:
        raise ValueError('remove query/fragment credentials from source URL before saving')
    return value


def saved_entries(root: Path, relative='LOOPS.md') -> list[dict]:
    p = eog.confined(root, relative)
    if eog.file_state(p) == 'absent':
        return []
    text = p.read_bytes().decode('utf-8')
    # Preserve native structured EOG entries and historical human-readable Loopy sections.
    entries = [dict(x, origin='project', format='eog-loop') for x in eog.saved_loops(text)]
    starts = []; structured_starts = []; fence = None; offset = 0
    for line in text.splitlines(keepends=True):
        m = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if m:
            token = m[1]
            if fence is None:
                fence = (token[0], len(token))
                if line.strip() == '```eog-loop': structured_starts.append(offset)
            elif token[0] == fence[0] and len(token) >= fence[1] and line.strip() == token: fence = None
        elif fence is None and line.startswith('## '):
            starts.append((offset, line[3:].strip()))
        offset += len(line)
    for i, (start, title) in enumerate(starts):
        end = starts[i+1][0] if i+1 < len(starts) else len(text)
        # A structured block appended after a native section is a separate entry.
        # Markers inside the native prompt's longer fence are intentionally ignored.
        end = min([pos for pos in structured_starts if start < pos < end], default=end)
        block = text[start:end]
        entry = {'title': title, 'origin':'project', 'format':'loopy-markdown',
                 'source_path':relative, 'raw':block, 'entry_sha256':eog.digest(block.encode()),
                 'prompt':None, '_start':start, '_end':end}
        # A final separator newline is outside the exact prompt. Internal headings/fences survive.
        m = re.search(r'^Prompt:\s*\n(`{3,}|~{3,})(?:text|markdown)?\r?\n(.*?)\r?\n\1[ \t]*(?:\r?\n|$)', block, re.M|re.S)
        if m:
            entry['prompt'] = m[2]
        else:
            m = re.search(r'^Prompt:[ \t]*\r?\n((?:>[ \t]?.*(?:\r?\n|$))+)', block, re.M)
            if m: entry['prompt'] = '\n'.join(re.sub(r'^>[ ]?', '', line) for line in m[1].splitlines())
        for label,key in [('Saved','saved'),('Source','source_url'),('Source modified','source_modified')]:
            m = re.search(r'^'+label+r':[ \t]*(.+)$', block, re.M)
            if m: entry[key] = m[1].strip()
        if entry['prompt'] is not None:
            entry['prompt_sha256'] = eog.digest(entry['prompt'].encode())
        entries.append(entry)
    return entries


def save_text(root: Path, title: str, explanation: str, prompt: str, expected: str,
              relative='LOOPS.md', source=None, modified=None, saved=None, replace=None) -> dict:
    for text in (title, explanation, prompt): safe_text(text)
    if '\n' in title or '\r' in title or '\n' in explanation or '\r' in explanation:
        raise ValueError('title and explanation must each be one line')
    if source: source_url(source)
    if modified:
        if not source: raise ValueError('source modified date requires a source URL')
        date.fromisoformat(modified)
    day = saved or date.today().isoformat(); date.fromisoformat(day)
    runs = [len(m[0]) for m in re.finditer(r'`+', prompt)]
    fence = '`' * max(3, max(runs, default=0)+1)
    block = '## '+title+'\n\n'+explanation+'\n\nSaved: '+day+'\n'
    if source: block += 'Source: '+source+'\n'
    if modified: block += 'Source modified: '+modified+'\n'
    block += '\nPrompt:\n'+fence+'text\n'+prompt+'\n'+fence+'\n'
    p = eog.confined(root, relative)
    with eog.write_lock(p):
        if eog.file_state(p) != expected: raise ValueError('stale saved-loop document')
        text = p.read_bytes().decode('utf-8') if p.exists() else '# Project loops\n'
        matches = [r for r in saved_entries(root,relative) if r['title']==title]
        if replace:
            if len(matches)!=1 or matches[0].get('entry_sha256')!=replace:
                raise ValueError('exact native entry digest required for replacement')
            old=matches[0]; text=text[:old['_start']]+block+text[old['_end']:]
        else:
            if matches: raise ValueError('loop title already exists; use explicit replacement digest')
            text += '\n'+block
        sha=eog.atomic_write(p,text.encode(),expected)
    readback=[r for r in saved_entries(root,relative) if r['title']==title]
    if len(readback)!=1 or readback[0].get('prompt')!=prompt:
        raise OSError('saved prompt readback mismatch')
    return {'path':relative,'sha256':sha,'title':title,'prompt_sha256':eog.digest(prompt.encode()),
            'entry_sha256':readback[0]['entry_sha256'],'saved':True,'published':False}


def catalog_entries(snapshot: dict) -> list[dict]:
    body=snapshot['catalog']
    rows=body if isinstance(body,list) else body.get('loops') if isinstance(body,dict) else None
    if not isinstance(rows,list): raise ValueError('provider catalog is missing its loop array')
    result=[]; seen=set()
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get('title'),str) or not row['title'].strip():
            raise ValueError('invalid catalog loop')
        u=urlparse(row.get('url',''))
        if u.scheme!='https' or u.hostname!='signals.forwardfuture.com' or u.username or u.password or u.port not in (None,443) or not u.path.startswith('/loop-library/loops/') or u.query or u.fragment:
            raise ValueError('catalog entry leaves official published-loop origin')
        if row['url'] in seen: raise ValueError('duplicate catalog loop URL')
        seen.add(row['url'])
        result.append(dict(row, origin='published', definition_sha256=eog.digest(eog.dumps(row).encode()),
                           catalog_sha256=snapshot['sha256'], fetched_at=snapshot['fetched_at']))
    return result


def rank_entries(rows: list[dict], query: str, limit=3) -> list[dict]:
    if not isinstance(limit,int) or not 1<=limit<=3: raise ValueError('recommend at most three loops')
    terms=set(re.findall(r'\w+',query.casefold()))
    if not terms: raise ValueError('nonempty search terms required')
    ranked=[]
    for row in rows:
        fields=[row.get(k,'') for k in ['title','description','useWhen','prompt','verification','steps','keywords','experience','context','verify']]
        words=set(re.findall(r'\w+',eog.dumps(fields).casefold()))
        matches=sorted(terms & words)
        if matches:
            clean={k:v for k,v in row.items() if not k.startswith('_')}
            ranked.append(dict(clean,matched_terms=matches,match_count=len(matches)))
    return sorted(ranked,key=lambda r:(-r['match_count'],r['title']))[:limit]


def find_loops(root: Path, query: str, relative='LOOPS.md', published=True) -> dict:
    rows=saved_entries(root,relative); availability='not_requested'; error=None
    if published:
        try:
            rows += catalog_entries(eog.catalog()); availability='available'
        except (OSError,ValueError,KeyError,TypeError) as exc:
            availability='unavailable'; error=type(exc).__name__
    return {'matches':rank_entries(rows,query), 'published_discovery':availability,
            'provider_error':error,'ranking':'lexical retrieval only; existing agent compares outcome, tools, authority, verification and stop',
            'untrusted_reference_data':True,'executed':False}


def compare_loops(rows: list[dict]) -> dict:
    if not isinstance(rows,list) or not 2<=len(rows)<=3 or any(not isinstance(r,dict) for r in rows):
        raise ValueError('two or three exact loop records required')
    dimensions={'outcome':['experience','description','useWhen'], 'verification':['verify','verification'],
                'authority':['authority'], 'feedback':['observe','choose','steps'],
                'stop':['stop','boundary'], 'inputs':['context','useWhen']}
    compared=[]
    for row in rows:
        if not row.get('title'): raise ValueError('loop title required')
        values={key:{f:row[f] for f in fields if f in row} for key,fields in dimensions.items()}
        compared.append({'title':row['title'],'definition_sha256':eog.digest(eog.dumps(row).encode()),
                         'dimensions':values,'missing_dimensions':[k for k,v in values.items() if not v]})
    return {'candidates':compared,'winner':None,'note':'No inferred authority or fabricated fit. The existing agent compares these exact records.'}


def prepare_suggestion(root: Path, candidate: dict) -> dict:
    # Field limits match pinned official validation; current surface and attestation still control submission.
    if not isinstance(candidate,dict) or set(candidate)-{'loop_title','instructions','name','x_handle','source_url'}:
        raise ValueError('unknown suggestion fields; approval/permission cannot be supplied in a candidate')
    for key,limit in [('loop_title',120),('instructions',3000)]:
        safe_text(candidate.get(key,''))
        if len(candidate[key])>limit: raise ValueError(key+' exceeds provider limit')
    for key,limit in [('name',80),('x_handle',16),('source_url',300)]:
        if key in candidate:
            safe_text(candidate[key])
            if len(candidate[key])>limit: raise ValueError(key+' exceeds provider limit')
    if candidate.get('source_url'): source_url(candidate['source_url'])
    if candidate.get('x_handle') and not re.fullmatch(r'@?[A-Za-z0-9_]{1,15}',candidate['x_handle']):
        raise ValueError('invalid contributor handle')
    snapshot=eog.catalog()  # Failure blocks preview readiness; never fake a duplicate check.
    overlaps=rank_entries(catalog_entries(snapshot),candidate['loop_title']+' '+candidate['instructions'])
    packet={'destination':'https://signals.forwardfuture.com/loop-library/', 'requested_state':'suggestion',
            'candidate':candidate,'possible_overlap':overlaps,'catalog_sha256':snapshot['sha256'],
            'submission':'official browser surface; preserve human verification and exact current license attestation',
            'attestation_confirmed':False,'submitted':False,'published':False}
    packet['preview_sha256']=eog.digest(eog.dumps(packet).encode())
    return packet


def verify_publication(slug: str, expected_prompt: str) -> dict:
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug): raise ValueError('invalid published slug')
    rows=catalog_entries(eog.catalog()); found=[r for r in rows if r.get('slug')==slug]
    matches=len(found)==1 and eog.digest(found[0].get('prompt','').encode())==expected_prompt
    return {'catalog_entry_verified':matches,'record':found[0] if len(found)==1 else None,
            'published_by_this_client':False,'detail_page_verified':False,
            'note':'Verify the live detail page as well before claiming publication complete.'}
