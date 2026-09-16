import test from 'node:test';
import assert from 'node:assert/strict';
import {appendContext,commandPrompt,parseCommand,context} from './bridge.mjs';
import openCode from './adapters/opencode.mjs';
import piExtension from './adapters/pi.mjs';

test('shared context reads canonical source without legacy dependencies',()=>{
 const text=context('review');assert.match(text,/Mandatory existing-wheel search/);assert.match(text,/Requested EOG operation/);
});
test('native context stays one block while preserving foreign text',()=>{
 const once=appendContext('Foreign instructions.');const twice=appendContext(once);
 assert.equal((twice.match(/EOG NATIVE CONTEXT START/g)||[]).length,1);assert.match(twice,/Foreign instructions/);
});
test('unknown operation is rejected, not executable shell arguments',()=>{
 assert.throws(()=>parseCommand('; rm -rf /'));assert.throws(()=>context('off'));
 assert.equal(parseCommand('review a file').target,'a file');
});
test('OpenCode registration preserves other commands and skills',async()=>{
 const plugin=await openCode();const cfg={command:{other:{template:'keep'}},skills:{paths:['foreign']}};
 await plugin.config(cfg);await plugin.config(cfg);assert.equal(cfg.command.other.template,'keep');assert.equal(cfg.skills.paths.length,2);
 const out={system:['base']};await plugin['experimental.chat.system.transform']({},out);await plugin['experimental.chat.system.transform']({},out);
 assert.equal((out.system[0].match(/EOG NATIVE CONTEXT START/g)||[]).length,1);
});
test('OpenCode refuses foreign eog command overwrite',async()=>{
 const p=await openCode();await assert.rejects(()=>p.config({command:{eog:{template:'mine'}}}));
});
test('Pi fresh turn injects and active command uses followUp',async()=>{
 const callbacks={},commands={},sent=[];
 const pi={on:(k,f)=>callbacks[k]=f,registerCommand:(k,v)=>commands[k]=v,sendUserMessage:(...a)=>sent.push(a)};
 piExtension(pi);const turn=await callbacks.before_agent_start({systemPrompt:'Base'});
 assert.match(turn.systemPrompt,/Base/);assert.match(turn.systemPrompt,/EOG/);
 await commands.eog.handler('review native',{isIdle:()=>false});assert.deepEqual(sent[0][1],{deliverAs:'followUp'});
 assert.match(sent[0][0],/native/);
});
test('Pi absent base is not literal undefined and idle runs on same host',async()=>{
 const cb={},cmd={},sent=[];piExtension({on:(k,f)=>cb[k]=f,registerCommand:(k,v)=>cmd[k]=v,sendUserMessage:(...a)=>sent.push(a)});
 assert.doesNotMatch((await cb.before_agent_start(null)).systemPrompt,/^undefined/);
 await cmd.eog.handler('help',{isIdle:()=>true});assert.equal(sent[0].length,1);
});
test('Pi status says source loaded, not compliance verified',async()=>{
 const cb={},statuses=[];piExtension({on:(k,f)=>cb[k]=f,registerCommand:()=>{},sendUserMessage:()=>{}});
 await cb.session_start({}, {ui:{setStatus:(...a)=>statuses.push(a)}});assert.match(statuses[0][1],/compliance unverified/);
});
