// Native Pi callbacks; persistent modes are intentionally replaced by always-on EOG.
import {appendContext,commandPrompt,invoke} from '../bridge.mjs';
export default function eogExtension(pi) {
  pi.on('before_agent_start',async(event)=>({systemPrompt:appendContext(event?.systemPrompt)}));
  pi.on('session_start',async(_event,ctx)=>{
    const state=JSON.parse(invoke(['doctor']));
    ctx?.ui?.setStatus?.('eog','EOG '+state.policy_sha256.slice(0,12)+' (source loaded; compliance unverified)');
  });
  pi.registerCommand('eog',{
    description:'EOG review/audit/debt and bounded loop operations',
    handler:async(args,ctx)=>{
      const message=commandPrompt(args);
      if(ctx?.isIdle?.()===false)pi.sendUserMessage(message,{deliverAs:'followUp'});
      else pi.sendUserMessage(message);
    },
  });
}
