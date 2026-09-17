"""Actual local operations and adapter contracts, NOT native/model certification."""
from __future__ import annotations
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import eog

HERE=Path(__file__).resolve().parent
CORE=eog.policy(HERE)['text']

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'AGENTS.md').write_text(CORE,encoding='utf-8')
        self.record=eog.read_json(HERE/'example.json')
        self.owner=self.record['scope']['work_owner'];self.rev=self.record['scope']['subject_revision']
        self.loop=eog.read_json(HERE/'loop.example.json')

    def native(self,*args):
        return subprocess.run([sys.executable,str(HERE/'eog.py'),'--root',str(self.root),*args],capture_output=True,text=True,timeout=15)
    def git(self,*args):return eog.git(self.root,*args).decode().strip()
    def repo(self):
        self.git('init','-q');self.git('config','user.name','EOG Fixture');self.git('config','user.email','fixture@example.invalid')
    def commit(self):
        self.git('add','.');self.git('commit','-qm','fixture');return self.git('rev-parse','HEAD')

    def test_hermes_native_package_entrypoint(self):
        spec=importlib.util.spec_from_file_location('eog_hermes_package_fixture',HERE/'__init__.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertTrue(callable(module.register))
        manifest=(HERE/'plugin.yaml').read_text()
        self.assertIn('name: eog',manifest);self.assertIn('pre_llm_call',manifest)
    def test_policy_exact_section(self):
        (self.root/'AGENTS.md').write_text('# unrelated\n'+CORE+'\n## Other\nunchanged\n',encoding='utf-8')
        p=eog.policy(self.root)
        self.assertTrue(p['text'].startswith(eog.HEADING));self.assertNotIn('## Other',p['text'])
    def test_policy_fenced_example_is_not_owner(self):
        (self.root/'AGENTS.md').write_text('```markdown\n'+eog.HEADING+'\n```\n'+CORE,encoding='utf-8')
        self.assertEqual(eog.policy(self.root)['text'],CORE.rstrip()+'\n')
    def test_policy_duplicate_rejected(self):
        (self.root/'AGENTS.md').write_text(CORE+'\n'+CORE,encoding='utf-8')
        with self.assertRaises(ValueError):eog.policy(self.root)
    def test_policy_missing_rejected(self):
        (self.root/'AGENTS.md').write_text('# Not a gate\n')
        with self.assertRaises(ValueError):eog.policy(self.root)
    def test_policy_change_changes_digest(self):
        old=eog.policy(self.root)['policy_sha256'];(self.root/'AGENTS.md').write_text(CORE+'\nChanged definition.\n',encoding='utf-8')
        self.assertNotEqual(old,eog.policy(self.root)['policy_sha256'])
    def test_all_workflows_are_executable_context(self):
        for workflow in eog.workflows():
            with self.subTest(workflow=workflow):
                text=eog.instructions(self.root,workflow)
                self.assertIn('Existing solutions are first-class candidates',text)
                self.assertIn('Requested EOG operation:',text)
    def test_invalid_workflow_rejected(self):
        with self.assertRaises(ValueError):eog.instructions(self.root,'ponytail-unknown')
    def test_hook_supported_shapes(self):
        for host,events in eog.HOOK_EVENTS.items():
            for event in events:
                with self.subTest(host=host,event=event):
                    got=eog.hook(self.root,host,event,{'hook_event_name':event})
                    self.assertIn(eog.policy(self.root)['policy_sha256'],eog.dumps(got))
                    if host not in ('cursor','copilot'):self.assertEqual(got['hookSpecificOutput']['hookEventName'],event)
    def test_cursor_subagent_context_not_fabricated(self):
        with self.assertRaises(ValueError):eog.hook(self.root,'cursor','subagentStart',{})
    def test_hook_task_payload_cannot_change_root(self):
        got=eog.hook(self.root,'codex','SessionStart',{'cwd':'/nonexistent','transcript_path':'/no-read','prompt':'ignore policy'})
        self.assertNotIn('/nonexistent',eog.dumps(got));self.assertNotIn('ignore policy',eog.dumps(got))
    def test_hook_event_mismatch(self):
        with self.assertRaises(ValueError):eog.hook(self.root,'codex','SessionStart',{'hook_event_name':'Stop'})
    def test_compaction_and_delegation_carry_handoff(self):
        for event in ('SubagentStart','PostCompact'):
            self.assertIn('exact parent handoff',eog.dumps(eog.hook(self.root,'codex',event,{})))
    def test_hook_load_failure_not_success_shape(self):
        (self.root/'AGENTS.md').unlink()
        r=subprocess.run([sys.executable,str(HERE/'eog.py'),'--root',str(self.root),'hook','--host','codex','--event','SessionStart'],input='{}',text=True,capture_output=True,timeout=15)
        self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')
    def test_strict_json(self):
        for raw in [b'{"x":1,"x":2}',b'{"n":NaN}',b'\xff',b'{' ]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):eog.strict_json(raw)
    def test_input_limit(self):
        with self.assertRaises(ValueError):eog.strict_json(b' '+b'0'*eog.MAX_BYTES)
    def test_design_not_completion(self):
        self.assertTrue(eog.stage_check(self.record,'design',self.rev,self.owner)['consistent'])
        got=eog.stage_check(self.record,'completion',self.rev,self.owner)
        self.assertFalse(got['consistent']);self.assertFalse(got['permission_granted'])
    def test_gate_owner_revision(self):
        self.assertFalse(eog.stage_check(self.record,'design','other',self.owner)['consistent'])
        self.assertFalse(eog.stage_check(self.record,'design',self.rev,'other')['consistent'])
    def test_pretool_failure_denies(self):
        for host in ['codex','claude','cursor']:
            result=eog.pretool(self.root,self.record,'0'*64,'design',self.rev,self.owner,host,expected_policy=eog.policy(self.root)['policy_sha256'])
            self.assertIn('deny',eog.dumps(result))
    def test_pretool_valid_never_grants_allow(self):
        h=eog.digest(eog.dumps(self.record).encode())
        self.assertEqual({},eog.pretool(self.root,self.record,h,'design',self.rev,self.owner,'codex',expected_policy=eog.policy(self.root)['policy_sha256']))
        self.assertIn('deny',eog.dumps(eog.pretool(self.root,self.record,h,'completion',self.rev,self.owner,'codex',expected_policy=eog.policy(self.root)['policy_sha256'])))
    def test_pretool_stale_policy_denied(self):
        h=eog.digest(eog.dumps(self.record).encode())
        r=eog.pretool(self.root,self.record,h,'design',self.rev,self.owner,'codex',expected_policy='0'*64)
        self.assertIn('deny',eog.dumps(r))
    def test_pretool_validator_unavailable_still_denies(self):
        h=eog.digest(eog.dumps(self.record).encode())
        with patch('eog.stage_check',side_effect=ImportError('fixture')):
            r=eog.pretool(self.root,self.record,h,'design',self.rev,self.owner,'codex',expected_policy=eog.policy(self.root)['policy_sha256'])
            self.assertIn('deny',eog.dumps(r))
    def test_no_progress_rule_does_not_stop_informative_feedback(self):
        self.assertIn('stop when more information cannot reasonably change the next useful decision', ' '.join(CORE.split()).lower())
    def test_pretool_does_not_depend_on_workflow_prompt_file(self):
        import contextlib, io
        argv=['eog','--root',str(self.root),'pretool',str(self.root/'missing.json'),
              '--record-sha256','0'*64,'--policy-sha256','0'*64,'--owner',self.owner,
              '--revision',self.rev,'--host','codex']
        out=io.StringIO()
        with patch('sys.argv',argv), patch('eog.workflows',side_effect=OSError('missing workflow')), contextlib.redirect_stdout(out):
            self.assertEqual(eog.main(),0)
        self.assertIn('deny',out.getvalue())
    def test_pretool_missing_file_fails_closed(self):
        r=self.native('pretool',str(self.root/'missing.json'),'--record-sha256','0'*64,'--policy-sha256',eog.policy(self.root)['policy_sha256'],'--owner',self.owner,'--revision',self.rev,'--host','codex')
        self.assertEqual(r.returncode,0);self.assertIn('deny',r.stdout)
    def packet(self):return eog.handoff(self.root,self.record,self.owner,self.rev,'fixture://authority',['stop on denied authority'])
    def test_handoff_roundtrip(self):
        self.assertTrue(eog.verify_handoff(self.root,self.packet(),self.owner,self.rev)['consistent'])
    def test_handoff_tamper(self):
        p=self.packet();p['authority_ref']='changed'
        with self.assertRaises(ValueError):eog.verify_handoff(self.root,p,self.owner,self.rev)
    def test_handoff_wrong_recipient_scope(self):
        with self.assertRaises(ValueError):eog.verify_handoff(self.root,self.packet(),'different task',self.rev)
    def test_handoff_stale_policy(self):
        p=self.packet();(self.root/'AGENTS.md').write_text(CORE+'\nChanged\n',encoding='utf-8')
        with self.assertRaises(ValueError):eog.verify_handoff(self.root,p,self.owner,self.rev)
    def test_handoff_requires_stops(self):
        with self.assertRaises(ValueError):eog.handoff(self.root,self.record,self.owner,self.rev,'fixture',[])
    def test_native_debt_preserves_legacy(self):
        self.repo();p=self.root/'code.py';p.write_text('# ponytail: global lock, per-account if load rises\n# eog: ceiling: serial; trigger: contention; upgrade: partition\nx="// ponytail: not a comment"\n')
        self.git('add','.');before=p.read_bytes();r=eog.source_debt(self.root)
        self.assertEqual(r['count'],2);self.assertEqual(r['unresolved_trigger_count'],1);self.assertEqual(p.read_bytes(),before)
    def test_native_debt_ignores_untracked_and_vendor(self):
        self.repo();(self.root/'untracked.py').write_text('# eog: no\n');(self.root/'vendor').mkdir();(self.root/'vendor/a.py').write_text('# eog: third party\n');self.git('add','vendor')
        self.assertEqual(eog.source_debt(self.root)['count'],0)
    def test_real_git_impact(self):
        self.repo();(self.root/'a.txt').write_text('one\n');a=self.commit();(self.root/'a.txt').write_text('two\nthree\n');b=self.commit()
        r=eog.impact(self.root,a,b);self.assertEqual((r['added'],r['removed']),(2,1));self.assertIsNone(r['savings_claim'])
    def test_impact_ref_injection_rejected(self):
        with self.assertRaises(ValueError):eog.revision_sha(self.root,'--all')
    def test_catalog_transport_failure_no_fallback(self):
        with patch('urllib.request.build_opener') as m:
            m.return_value.open.side_effect=OSError('unavailable')
            with self.assertRaises(OSError):eog.catalog()
    def test_catalog_contract_keeps_source_digest(self):
        cm=types.SimpleNamespace(__enter__=None)
        with patch('urllib.request.build_opener') as m:
            m.return_value.open.return_value.__enter__.return_value.read.return_value=b'{"loops":[]}'
            r=eog.catalog();self.assertEqual(r['sha256'],eog.digest(b'{"loops":[]}'));self.assertTrue(r['untrusted_reference_data'])
    def test_catalog_external_redirect_rejected(self):
        with self.assertRaises(ValueError):eog.SameOriginRedirect().redirect_request(None,None,302,'',{},'http://127.0.0.1/secrets')
    def test_loop_schema_and_finite_boundary(self):
        self.assertEqual(eog.check_loop(self.loop),[])
        self.loop['boundary']={'kind':'user_limit','condition':'two passes'}
        self.assertTrue(eog.check_loop(self.loop))
    def test_save_preserves_exact_legacy_bytes(self):
        p=self.root/'LOOPS.md';old=b'# Existing\r\nlegacy loop instructions  \r\n\r\n';p.write_bytes(old)
        r=eog.save_loop(self.root,'LOOPS.md',self.loop,eog.digest(old))
        self.assertTrue(p.read_bytes().startswith(old));self.assertFalse(r['published']);self.assertEqual(eog.saved_loops(p.read_text())[0],self.loop)
    def test_save_duplicate_and_stale(self):
        r=eog.save_loop(self.root,'LOOPS.md',self.loop,'absent');before=(self.root/'LOOPS.md').read_bytes()
        with self.assertRaises(ValueError):eog.save_loop(self.root,'LOOPS.md',self.loop,r['sha256'])
        with self.assertRaises(ValueError):eog.save_loop(self.root,'LOOPS.md',self.loop,'absent')
        self.assertEqual(before,(self.root/'LOOPS.md').read_bytes())
    def test_save_confined_and_symlink(self):
        with self.assertRaises(ValueError):eog.save_loop(self.root,'../escape.md',self.loop,'absent')
        if os.name=='nt': self.skipTest('unprivileged Windows symlink creation is unavailable on this runner')
        (self.root/'link').symlink_to(self.root/'elsewhere')
        with self.assertRaises(ValueError):eog.save_loop(self.root,'link',self.loop,'absent')
    def test_cooperative_lock_is_fail_closed_and_cleaned(self):
        p=self.root/'LOOPS.md'
        with eog.write_lock(p):
            with self.assertRaises(FileExistsError):eog.save_loop(self.root,'LOOPS.md',self.loop,'absent')
        self.assertFalse((self.root/'.LOOPS.md.eog-write-lock').exists())
    def test_native_install_merge_idempotent_remove(self):
        if os.name=='nt': self.skipTest('native Windows hook install intentionally unclaimed; project-rule delivery is supported')
        for host,rel in eog.CONFIG_PATHS.items():
            with self.subTest(host=host):
                p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True)
                foreign={'x':1,'hooks':{'ForeignEvent':[{'foreign':'preserve'}]}};p.write_text(json.dumps(foreign))
                initial=eog.file_state(p);preview=eog.install(self.root,host,None,False)
                self.assertFalse(preview['applied']);self.assertEqual(eog.file_state(p),initial)
                result=eog.install(self.root,host,initial,True);mid=p.read_bytes()
                again=eog.install(self.root,host,result['sha256'],True);self.assertEqual(mid,p.read_bytes())
                eog.uninstall(self.root,host,again['sha256']);rest=eog.read_json(p)
                self.assertEqual(rest['x'],1);self.assertEqual(rest['hooks']['ForeignEvent'],foreign['hooks']['ForeignEvent'])
    def test_install_requires_expected_and_preserves_stale(self):
        if os.name=='nt': self.skipTest('native Windows hook install intentionally unclaimed; project-rule delivery is supported')
        with self.assertRaises(ValueError):eog.install(self.root,'cursor',None,True)
        r=eog.install(self.root,'cursor','absent',True);p=self.root/eog.CONFIG_PATHS['cursor'];p.write_text('{"user":true}')
        with self.assertRaises(ValueError):eog.install(self.root,'cursor',r['sha256'],True)
        self.assertEqual(eog.read_json(p),{'user':True})
    def test_generated_rule_current_and_uninstall_preserves_user(self):
        p=self.root/'CLAUDE.md';before='My original rules.\n';p.write_text(before)
        r=eog.install(self.root,'claude-rule',eog.file_state(p),True)
        self.assertTrue(eog.doctor(self.root,'claude-rule')['adapter']['configured_and_current'])
        eog.uninstall(self.root,'claude-rule',r['sha256']);self.assertIn(before,p.read_text())
    def test_generated_rule_foreign_edit_refuses_uninstall(self):
        eog.install(self.root,'claude-rule','absent',True);p=self.root/'CLAUDE.md';p.write_text(p.read_text().replace('EOG 2.0','EOG custom'))
        with self.assertRaises(ValueError):eog.uninstall(self.root,'claude-rule',eog.file_state(p))
    def test_cursor_rule_cannot_silently_disable(self):
        p=self.root/'.cursor/rules/eog.mdc';p.parent.mkdir(parents=True);p.write_text('---\nalwaysApply: false\n---\nuser\n')
        with self.assertRaises(ValueError):eog.install(self.root,'cursor-rule',eog.file_state(p),True)
    def test_doctor_never_certifies_native_or_model(self):
        r=eog.doctor(self.root,None);self.assertFalse(r['native_loading_verified']);self.assertFalse(r['model_compliance_verified'])
    def receipt(self):
        return {'definition':self.loop,'definition_sha256':eog.digest(eog.dumps(self.loop).encode()),'scope':'fixture','work_owner':'fixture-owner','subject_revision':'fixture-v1','steps':[],'outcome':'blocked','residual':'fixture only'}
    def test_receipt_blocked_not_success(self):
        r=self.receipt();self.assertEqual(eog.check_receipt(r),[]);r['outcome']='success';self.assertTrue(eog.check_receipt(r))
    def test_receipt_digest_and_revision(self):
        r=self.receipt();r['definition_sha256']='0'*64;self.assertTrue(eog.check_receipt(r))
        r=self.receipt();r['outcome']='success';r['acceptance']={'result':'passed','locator':'fixture://accept','observation':'fixture','subject_revision':'old'}
        self.assertTrue(eog.check_receipt(r))
    def test_receipt_latest_failure_beats_success(self):
        r=self.receipt();r['outcome']='success';obs={'result':'passed','locator':'fixture://accept','observation':'fixture','subject_revision':'fixture-v1'};r['acceptance']=obs
        r['steps']=[{'sequence':1,'observed_at':'2026-09-16T00:00:00Z','baseline':'fixture','choice':'fixture','action':'fixture','changed':True,'verification':dict(obs,result='failed'),'next_learning':'fix'}]
        self.assertTrue(eog.check_receipt(r));r['outcome']='clean_noop';self.assertTrue(any('mutation' in x for x in eog.check_receipt(r)))
    def test_manifest_covers_whole_method_families(self):
        m=eog.read_json(HERE/'capabilities.json');ids=[x['id'] for x in m['capabilities']]
        self.assertEqual(len(ids),len(set(ids)))
        for name in ['ponytail.mcp','ponytail.hermes','ponytail.pi','ponytail.opencode','ponytail.debt','loopy.publish','loopy.save','loopy.debrief','uog.wheel-search','uog.gap']:
            self.assertIn(name,ids)
    def test_empty_replacement_receipt_never_retires(self):
        r=eog.replacement_check(self.root,{})
        self.assertFalse(r['receipt_consistent']);self.assertFalse(r['replacement_authorized'])
    def test_invalid_host_inventory_no_false_acceptance(self):
        r=eog.replacement_check(self.root,{'hosts':[4]});self.assertFalse(r['receipt_consistent'])
    def test_structural_host_evidence_not_native(self):
        r=eog.replacement_check(self.root,{'hosts':[{'id':'fixture','kind':'unit_test','loading':'passed','workflow':'passed','legacy_absent_trial':'passed','locator':'fixture://'}]})
        self.assertTrue(any('host replacement' in x for x in r['errors']))
    def test_cli_manifest_and_doctor(self):
        for args in [('manifest',),('doctor',),('prompt','--workflow','debt')]:
            r=self.native(*args);self.assertEqual(r.returncode,0,r.stderr)
    def test_hermes_native_contract_respects_gateway(self):
        spec=importlib.util.spec_from_file_location('eog_hermes',HERE/'adapters/hermes.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=self.root
        event=types.SimpleNamespace(text='/eog review sample',source='fixture')
        deny=types.SimpleNamespace(_check_slash_access=lambda *_:'denied')
        allow=types.SimpleNamespace(_check_slash_access=lambda *_:None)
        self.assertIsNone(m.rewrite_gateway(event,deny));self.assertIsNone(m.rewrite_gateway(event,None))
        self.assertEqual(m.rewrite_gateway(event,allow)['action'],'rewrite')
        self.assertIn('Existing solutions are first-class candidates',m.before_llm()['context'])
    def test_hermes_queues_on_existing_host_only(self):
        spec=importlib.util.spec_from_file_location('eog_hermes_registration',HERE/'adapters/hermes.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=self.root
        registered={}
        ctx=types.SimpleNamespace(register_skill=lambda name,path:registered.update(skill=(name,path)),register_hook=lambda name,fn:registered.update({name:fn}),register_command=lambda name,fn,**kw:registered.update(command=fn),inject_message=lambda _:True)
        m.register(ctx);self.assertEqual(registered['skill'][0],'eog');self.assertIn('Queued',registered['command']('review'))

    def test_v2_depth_compatibility_is_task_scoped(self):
        for depth in eog.DEPTHS:
            text=eog.instructions(self.root,'plan',depth=depth)
            self.assertIn('depth='+depth,text)
        self.assertIn('skip optional optimization',eog.instructions(self.root,'plan',depth='off'))
        self.assertIn('authority/integrity guards remain',eog.instructions(self.root,'plan',depth='off'))

    def test_v2_manifest_separates_capability_and_evidence(self):
        m=eog.read_json(HERE/'capabilities.json')
        self.assertEqual(m['absorption_status'],'capability_complete')
        self.assertEqual(m['ordinary_mental_model'],['Experience','Choice','Minimality','Feedback','Integrity'])
        self.assertNotIn('policy_change',{x['disposition'] for x in m['capabilities']})
        for cid in ['ponytail.optional-modes','loopy.compare','loopy.repair','uog.no-ceremony','uog.decision-uncertainty']:
            row=next(x for x in m['capabilities'] if x['id']==cid)
            self.assertIn(row['capability_state'],m['capability_state_model'])
            self.assertIn(row['evidence_state'],m['evidence_state_model'])

    def test_v2_repair_is_canonical_and_legacy_alias_preserved(self):
        self.assertIn('repair',eog.workflows())
        self.assertNotIn('loop-repair',eog.workflows())
        self.assertIn('Repair material loop defects',eog.instructions(self.root,'loop-repair'))

if __name__=='__main__':unittest.main()
