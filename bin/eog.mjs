#!/usr/bin/env node
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {pythonCommand} from '../python_command.mjs';
try {
  const {command,args}=pythonCommand();
  const run=spawnSync(command,[...args,fileURLToPath(new URL('../eog.py',import.meta.url)),...process.argv.slice(2)],
    {stdio:'inherit',windowsHide:true});
  if(run.error) throw run.error;
  process.exit(run.status ?? 2);
} catch(e) {console.error('EOG blocked: '+e.message);process.exit(2);}
