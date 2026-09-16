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
 const tools=await client.listTools();assert.deepEqual(tools.tools.map(x=>x.name),['eog_instructions','eog_validate','eog_status']);
 const text=await client.callTool({name:'eog_instructions',arguments:{workflow:'review'}});
 assert.match(text.content[0].text,/Mandatory existing-wheel search/);
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
