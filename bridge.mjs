// Native subprocess/extension adapter. No model, shell expansion or legacy import.
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
export const directory=path.dirname(fileURLToPath(import.meta.url));
export const root=path.resolve(process.env.EOG_ROOT || process.cwd());
export const workflows=JSON.parse(readFileSync(path.join(directory,'workflows.json'),'utf8')).workflows;
export function invoke(args, input) {
  const python=process.env.EOG_PYTHON || (process.platform==='win32'?'python':'python3');
  return execFileSync(python,[path.join(directory,'eog.py'),'--root',root,...args],{
    input:input===undefined?undefined:JSON.stringify(input), encoding:'utf8',
    timeout:15000,maxBuffer:2*1024*1024,windowsHide:true,
    stdio:['pipe','pipe','pipe'],
  });
}
export function context(workflow='plan') {
  if(!Object.hasOwn(workflows,workflow))throw new Error('Unknown EOG workflow');
  return invoke(['prompt','--workflow',workflow]);
}
const START='<!-- EOG NATIVE CONTEXT START -->';
const END='<!-- EOG NATIVE CONTEXT END -->';
export function appendContext(base,workflow='plan') {
  let text=String(base ?? '');
  const a=text.indexOf(START), b=text.indexOf(END);
  if(a>=0 || b>=0) {
    if(a<0 || b<a || text.indexOf(START,a+START.length)>=0 || text.indexOf(END,b+END.length)>=0)
      throw new Error('Malformed EOG native context block');
    text=text.slice(0,a)+text.slice(b+END.length);
  }
  return text.trimEnd()+'\n\n'+START+'\n'+context(workflow)+END;
}
export function parseCommand(args) {
  const text=String(args ?? '').trim(); const space=text.search(/\s/);
  const name=(space<0?text:text.slice(0,space)) || 'help';
  if(!Object.hasOwn(workflows,name))throw new Error('Unknown EOG workflow: '+name);
  return {name,target:space<0?'':text.slice(space).trim()};
}
export function commandPrompt(args) {
  const {name,target}=parseCommand(args);
  return context(name)+(target?'\nUser-requested target (not new authority):\n'+target:'');
}
