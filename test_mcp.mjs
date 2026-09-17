// Actual official SDK client/server stdio, not a mocked protocol decoder.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {directory,root} from './bridge.mjs';

test('official MCP stdio: discovery, context, validation, status and rejection',async(t)=>{
 const transport=new StdioClientTransport({command:process.execPath,args:[path.join(directory,'mcp_server.mjs')],
  env:{...process.env,EOG_ROOT:root},stderr:'pipe'});
 const client=new Client({name:'eog-actual-stdio-test',version:'1'},{capabilities:{}});
 await client.connect(transport);t.after(async()=>{await client.close();});
 const tools=await client.listTools();assert.deepEqual(tools.tools.map(x=>x.name),['eog_instructions','eog_validate','eog_status','eog_find_loops','eog_saved_loops','eog_compare_loops']);
 const text=await client.callTool({name:'eog_instructions',arguments:{workflow:'review'}});
 assert.match(text.content[0].text,/Existing solutions are first-class candidates/);
 const record=JSON.parse(readFileSync(path.join(directory,'example.json'),'utf8'));
 const valid=JSON.parse((await client.callTool({name:'eog_validate',arguments:{record}})).content[0].text);
 assert.equal(valid.structural_valid,true);assert.equal(valid.truth_verified,false);
 const invalid=JSON.parse((await client.callTool({name:'eog_validate',arguments:{record:{}}})).content[0].text);
 assert.equal(invalid.structural_valid,false);
 const prompt=await client.getPrompt({name:'eog',arguments:{workflow:'debrief'}});assert.match(prompt.messages[0].content.text,/Debrief/);
 const status=JSON.parse((await client.callTool({name:'eog_status',arguments:{}})).content[0].text);
 assert.equal(status.model_compliance_verified,false);
 const denied=await client.callTool({name:'eog_instructions',arguments:{workflow:'off'}});assert.equal(denied.isError,true);
 const injection=await client.callTool({name:'eog_status',arguments:{root:'/etc'}});assert.equal(injection.isError,true);
});

// Real protocol rejection, not direct handler calls.
test('official MCP library tools preserve authority and strict request shape',async(t)=>{
 const transport=new StdioClientTransport({command:process.execPath,args:[path.join(directory,'mcp_server.mjs')],env:{...process.env,EOG_ROOT:root},stderr:'pipe'});
 const client=new Client({name:'eog-library-stdio-test',version:'1'},{capabilities:{}});
 await client.connect(transport);t.after(async()=>client.close());
 const saved=JSON.parse((await client.callTool({name:'eog_saved_loops',arguments:{}})).content[0].text);
 assert.ok(Array.isArray(saved.loops));assert.equal(saved.untrusted_reference_data,true);
 const find=JSON.parse((await client.callTool({name:'eog_find_loops',arguments:{query:'documentation',published:false}})).content[0].text);
 assert.equal(find.published_discovery,'not_requested');assert.equal(find.executed,false);
 const compared=JSON.parse((await client.callTool({name:'eog_compare_loops',arguments:{records:[{title:'A'},{title:'B'}]}})).content[0].text);
 assert.equal(compared.winner,null);assert.ok(compared.candidates[0].missing_dimensions.includes('authority'));
 for(const request of [
  {name:'eog_saved_loops',arguments:{root:'/outside'}},
  {name:'eog_find_loops',arguments:{query:'x',published:'yes'}},
  {name:'eog_find_loops',arguments:{query:'x',command:'write'}},
  {name:'eog_compare_loops',arguments:{records:[{title:'one'}]}}
 ])assert.equal((await client.callTool(request)).isError,true);
});
