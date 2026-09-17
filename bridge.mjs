// Native subprocess/extension adapter. No model, shell expansion or legacy import.
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import {pythonCommand} from './python_command.mjs';
export const directory=path.dirname(fileURLToPath(import.meta.url));
export const root=path.resolve(process.env.EOG_ROOT || process.cwd());
const manifest=JSON.parse(readFileSync(path.join(directory,'workflows.json'),'utf8'));
export const workflows=manifest.workflows;
const aliases=manifest.aliases || {};
const resolve=name=>aliases[String(name).replace(/^\//,'')] || String(name).replace(/^\//,'');
export function invoke(args, input) {
  const {command:python,args:prefix}=pythonCommand();
  return execFileSync(python,[...prefix,path.join(directory,'eog.py'),'--root',root,...args],{
    input:input===undefined?undefined:JSON.stringify(input), encoding:'utf8',
    timeout:30000,maxBuffer:2*1024*1024,windowsHide:true,
    stdio:['pipe','pipe','pipe'],
  });
}
export function context(workflow='plan') {
  workflow=resolve(workflow);
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
  return text.trimEnd()+'\n\n'+START+'\n'+invoke(['refresh'])+END;
}
export function parseCommand(args) {
  const text=String(args ?? '').trim(); const space=text.search(/\s/);
  const name=resolve((space<0?text:text.slice(0,space)) || 'help');
  if(!Object.hasOwn(workflows,name))throw new Error('Unknown EOG workflow: '+name);
  return {name,target:space<0?'':text.slice(space).trim()};
}
export function commandPrompt(args) {
  const {name,target}=parseCommand(args);
  return context(name)+(target?'\nUser-requested target (not new authority):\n'+target:'');
}
