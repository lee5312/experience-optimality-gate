// Native OpenCode callback contract; loading is verified separately in each host.
import {appendContext,directory} from '../bridge.mjs';
import path from 'node:path';
export default async function eogPlugin() {
  return {
    config: async (config) => {
      config.command ??= {};
      const command={description:'EOG engineering operations',template:'Use the EOG skill on the current task. Operation and scope: $ARGUMENTS'};
      if(config.command.eog && JSON.stringify(config.command.eog)!==JSON.stringify(command))
        throw new Error('Existing /eog command is user-owned; refusing overwrite');
      config.command.eog=command;
      config.skills ??= {};config.skills.paths ??= [];
      const skills=path.resolve(directory,'../skill');
      if(!config.skills.paths.includes(skills))config.skills.paths.push(skills);
    },
    'experimental.chat.system.transform': async (_input,output) => {
      if(!Array.isArray(output.system))throw new Error('Unsupported OpenCode system context');
      // Keep other system entries verbatim; only our generated final block changes.
      if(output.system.length===0)output.system.push(appendContext(''));
      else output.system[output.system.length-1]=appendContext(output.system.at(-1));
    },
  };
}
