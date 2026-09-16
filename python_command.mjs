// Discover installed Python without shell expansion, downloads or profile edits.
import {spawnSync} from 'node:child_process';
let cached;
export function pythonCommand() {
  if (cached) return cached;
  const explicit=process.env.EOG_PYTHON;
  const candidates=explicit?[[explicit,[]]]:process.platform==='win32'?
    [['py',['-3']],['python3',[]],['python',[]]]:[['python3',[]],['python',[]]];
  for (const [command,args] of candidates) {
    const r=spawnSync(command,[...args,'-c','import sys; print("EOG_PYTHON_OK" if sys.version_info >= (3,11) else "OLD")'],
      {encoding:'utf8',timeout:4000,windowsHide:true,stdio:['ignore','pipe','pipe']});
    if (r.status===0 && r.stdout.trim()==='EOG_PYTHON_OK') return cached={command,args};
  }
  throw new Error(explicit?'EOG_PYTHON must name a working Python 3.11+ executable.':'Python 3.11+ not found. Install Python or set EOG_PYTHON; no installation was attempted.');
}
