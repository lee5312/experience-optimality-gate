// Read-only optional MCP carrier. Protocol is the official SDK, not reimplemented.
import {Server} from '@modelcontextprotocol/sdk/server/index.js';
import {StdioServerTransport} from '@modelcontextprotocol/sdk/server/stdio.js';
import {ListToolsRequestSchema,CallToolRequestSchema,ListPromptsRequestSchema,GetPromptRequestSchema} from '@modelcontextprotocol/sdk/types.js';
import {context,invoke,workflows} from './bridge.mjs';
const server=new Server({name:'eog',version:'1.1.0'},{capabilities:{tools:{},prompts:{}}});
const operations=Object.keys(workflows);
const tools=[
  {name:'eog_instructions',description:'Read canonical EOG plus one workflow; does not execute it or inject every turn.',inputSchema:{type:'object',properties:{workflow:{type:'string',enum:operations}},additionalProperties:false}},
  {name:'eog_validate',description:'Check a supplied material record. Structure only; never grants authority or certifies evidence.',inputSchema:{type:'object',properties:{record:{type:'object'}},required:['record'],additionalProperties:false}},
  {name:'eog_status',description:'Read current canonical policy digest; does not prove host/model compliance.',inputSchema:{type:'object',properties:{},additionalProperties:false}},
];
server.setRequestHandler(ListToolsRequestSchema,async()=>({tools}));
server.setRequestHandler(CallToolRequestSchema,async(request)=>{
  try {
    const args=request.params.arguments ?? {};
    if(!args || typeof args!=='object' || Array.isArray(args))throw new Error('Object arguments required');
    let text;
    if(request.params.name==='eog_instructions') {
      if(Object.keys(args).some(k=>k!=='workflow'))throw new Error('Unknown field');
      text=context(args.workflow ?? 'plan');
    } else if(request.params.name==='eog_validate') {
      if(Object.keys(args).some(k=>k!=='record') || !args.record || typeof args.record!=='object' || Array.isArray(args.record))throw new Error('Record object required');
      try { text=invoke(['validate-stdin'],args.record); }
      catch(e) { if(e.status===1 && e.stdout)text=String(e.stdout);else throw e; }
    } else if(request.params.name==='eog_status') {
      if(Object.keys(args).length)throw new Error('No arguments accepted');
      text=invoke(['doctor']);
    } else throw new Error('Unknown EOG tool');
    return {content:[{type:'text',text}]};
  } catch(_e) {
    // No stderr, environment, record content or secret-bearing paths exposed.
    return {isError:true,content:[{type:'text',text:'EOG request rejected or canonical source unavailable; no action performed.'}]};
  }
});
server.setRequestHandler(ListPromptsRequestSchema,async()=>({prompts:[{name:'eog',description:'Canonical EOG on the existing agent',arguments:[{name:'workflow',description:'EOG operation name',required:false}]}]}));
server.setRequestHandler(GetPromptRequestSchema,async(request)=>{
  if(request.params.name!=='eog')throw new Error('Unknown prompt');
  const args=request.params.arguments ?? {};
  if(Object.keys(args).some(k=>k!=='workflow'))throw new Error('Unknown argument');
  return {description:'User-invoked EOG prompt; not always-on enforcement',messages:[{role:'user',content:{type:'text',text:context(args.workflow ?? 'plan')}}]};
});
await server.connect(new StdioServerTransport());
