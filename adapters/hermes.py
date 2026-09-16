"""Thin Hermes adapter using the same EOG source; no persisted mode or agent."""
from pathlib import Path
import os
import sys
MODULE=Path(__file__).resolve().parents[1]
ROOT=Path(os.environ.get('EOG_ROOT', Path.cwd())).resolve()
if str(MODULE) not in sys.path:sys.path.insert(0,str(MODULE))
import eog

def command_prompt(args=''):
    name,_,target=str(args or '').strip().partition(' ')
    name=name or 'help'
    return eog.instructions(ROOT,name)+ ('\nUser-requested target (not new authority):\n'+target if target else '')

def before_llm(**_):
    return {'context':eog.instructions(ROOT,'plan')}

def rewrite_gateway(event=None,gateway=None,**_):
    text=str(getattr(event,'text','') or '').strip()
    if text.split(' ',1)[0]!='/eog':return None
    # Never bypass the gateway's existing slash-command access decision.
    checker=getattr(gateway,'_check_slash_access',None)
    source=getattr(event,'source',None)
    if checker is None or source is None:return None
    try:
        if checker(source,'eog') is not None:return None
    except Exception:return None
    return {'action':'rewrite','text':command_prompt(text.partition(' ')[2])}

def register(ctx):
    ctx.register_skill('eog',MODULE/'skill/SKILL.md')
    ctx.register_hook('pre_llm_call',before_llm)
    ctx.register_hook('pre_gateway_dispatch',rewrite_gateway)
    def handler(args):
        prompt=command_prompt(args)
        try:queued=bool(ctx.inject_message(prompt))
        except Exception:queued=False
        return 'Queued EOG operation on the existing agent.' if queued else prompt
    ctx.register_command('eog',handler,description='EOG engineering operations',args_hint='[operation] [target]')
