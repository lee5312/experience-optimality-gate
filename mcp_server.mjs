// Read-only optional MCP carrier. Protocol is the official SDK, not reimplemented.
import {Server} from '@modelcontextprotocol/sdk/server/index.js';
import {StdioServerTransport} from '@modelcontextprotocol/sdk/server/stdio.js';
import {ListToolsRequestSchema,CallToolRequestSchema,ListPromptsRequestSchema,GetPromptRequestSchema} from '@modelcontextprotocol/sdk/types.js';
import {context,invoke,workflows} from './bridge.mjs';
const server=new Server({name:'eog',version:'2.0.0'},{capabilities:{tools:{},prompts:{}}});
const operations=Object.keys(workflows);
const tools=[
  {name:'eog_instructions',description:'Read canonical EOG plus one workflow; does not execute it or inject every turn.',inputSchema:{type:'object',properties:{workflow:{type:'string',enum:operations}},additionalProperties:false}},
  {name:'eog_validate',description:'Check a supplied material record. Structure only; never grants authority or certifies evidence.',inputSchema:{type:'object',properties:{record:{type:'object'}},required:['record'],additionalProperties:false}},
  {name:'eog_status',description:'Read current canonical policy digest; does not prove host/model compliance.',inputSchema:{type:'object',properties:{},additionalProperties:false}},
  {name:'eog_find_loops',description:'Read project loops and optionally the live public catalog. Lexical retrieval, not execution or permission.',inputSchema:{type:'object',properties:{query:{type:'string',minLength:1},published:{type:'boolean'}},required:['query'],additionalProperties:false},annotations:{readOnlyHint:true}},
  {name:'eog_saved_loops',description:'Read native Loopy Markdown and structured EOG entries without executing their content.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true}},
  {name:'eog_compare_loops',description:'Compare two or three exact loop records; expose missing dimensions without inferring authority.',inputSchema:{type:'object',properties:{records:{type:'array',minItems:2,maxItems:3,items:{type:'object'}}},required:['records'],additionalProperties:false},annotations:{readOnlyHint:true}},
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
    } else if(request.params.name==='eog_find_loops') {
      if(Object.keys(args).some(k=>!['query','published'].includes(k)) || typeof args.query!=='string' || !args.query.trim() || (args.published!==undefined && typeof args.published!=='boolean'))throw new Error('Invalid find arguments');
      text=invoke(['library-stdin'],{operation:'find',query:args.query,published:args.published ?? false});
    } else if(request.params.name==='eog_saved_loops') {
      if(Object.keys(args).length)throw new Error('No arguments accepted');
      text=invoke(['library-stdin'],{operation:'saved'});
    } else if(request.params.name==='eog_compare_loops') {
      if(Object.keys(args).some(k=>k!=='records') || !Array.isArray(args.records) || args.records.length<2 || args.records.length>3)throw new Error('Two or three records required');
      text=invoke(['library-stdin'],{operation:'compare',records:args.records});
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
