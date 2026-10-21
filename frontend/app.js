'use strict';
const base=(window.API_BASE_URL||'http://localhost:8000').replace(/\/$/,'');
const $=id=>document.getElementById(id);let records=[],summary=null,conversationId=null;
const fmt=n=>typeof n==='number'?n.toLocaleString('en-US',{maximumFractionDigits:2}):'—';
function notice(s){$('alert').textContent=s;}
async function request(path, options = {}) {
  const response = await fetch(base + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}
function error(e){notice('Error: '+e.message)}
function switchTab(name){document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.tab===name));document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.id===name));notice('');if(name==='history')loadHistory();if(name==='data')loadData();if(name==='overview')loadSummary();}
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>switchTab(t.dataset.tab));
$('theme').onclick=()=>{document.body.classList.toggle('dark');if(summary)renderGraph();};
function renderGraph(){const canvas=$('graph'),ctx=canvas.getContext('2d'),ratio=window.devicePixelRatio||1,rect=canvas.getBoundingClientRect();canvas.width=Math.max(400,rect.width)*ratio;canvas.height=230*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);const w=canvas.width/ratio,h=230;ctx.clearRect(0,0,w,h);const points=records.filter(r=>r.memo==='revenue').sort((a,b)=>a.date.localeCompare(b.date));if(!points.length){ctx.fillStyle='#777';ctx.fillText('No revenue data yet',20,25);return;}const recent=points.slice(-16),max=Math.max(...recent.map(p=>+p.value),1),min=Math.min(...recent.map(p=>+p.value),0),x=i=>40+i*(w-65)/Math.max(1,recent.length-1),y=v=>h-35-(v-min)/Math.max(1,max-min)*(h-70);ctx.strokeStyle='#a4b6a8';ctx.beginPath();ctx.moveTo(40,15);ctx.lineTo(40,h-35);ctx.lineTo(w-15,h-35);ctx.stroke();ctx.strokeStyle='#0b9764';ctx.lineWidth=3;ctx.beginPath();recent.forEach((p,i)=>i?ctx.lineTo(x(i),y(+p.value)):ctx.moveTo(x(i),y(+p.value)));ctx.stroke();ctx.fillStyle=getComputedStyle(document.body).getPropertyValue('--text');recent.forEach((p,i)=>{if(i%3===0||i===recent.length-1)ctx.fillText(p.fiscal_year+' '+p.fiscal_quarter,x(i)-8,h-13)});}
async function loadSummary(){try{[summary,records]=await Promise.all([request('/api/data/summary'),request('/api/data')]);const m=summary.latest_metrics||{};$('kpis').replaceChildren();for(const [label,val] of [['Revenue',m.revenue],['Operating Income',m.operating_income],['Net Income',m.net_income],['Total Assets',m.total_assets]]){const node=document.createElement('div');node.className='kpi';const l=document.createElement('small'),v=document.createElement('strong');l.textContent=label;v.textContent='$'+fmt(val);node.append(l,v);$('kpis').append(node)}$('range').textContent=`Period: ${summary.period||'No data'} · ${summary.count} records · Latest: ${summary.latest_quarter||'—'} · USD millions`;renderGraph()}catch(e){error(e)}}
$('refresh').onclick=loadSummary;$('export').onclick=()=>{const blob=new Blob([JSON.stringify({summary,records},null,2)],{type:'application/json'}),u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download='starbucks_financial_export.json';a.click();URL.revokeObjectURL(u)};
function bubble(role,content){const div=document.createElement('div');div.className='message '+role;div.textContent=content;$('messages').append(div);$('messages').scrollTop=$('messages').scrollHeight}
$('chat-form').onsubmit=async e=>{e.preventDefault();const txt=$('question').value.trim();if(!txt)return;$('ask').disabled=true;$('loading').hidden=false;bubble('user',txt);$('question').value='';try{const result=await request('/api/chat',{method:'POST',body:JSON.stringify({message:txt,conversation_id:conversationId})});conversationId=result.conversation_id;bubble('assistant',result.answer)}catch(err){error(err);bubble('assistant','Unable to complete the request. Please try again.')}finally{$('ask').disabled=false;$('loading').hidden=true}};
$('new-chat').onclick=()=>{conversationId=null;$('messages').replaceChildren();notice('Started a new conversation')};
function fillForm(r){$('record-id').value=r.id;$('date').value=r.date;$('value').value=r.value;$('memo').value=r.memo;$('year').value=r.fiscal_year;$('quarter').value=r.fiscal_quarter;switchTab('data');window.scrollTo(0,0)};
function clearForm(){$('data-form').reset();$('record-id').value=''}$('reset').onclick=clearForm;
function renderData(){const filter=$('filter').value.toLowerCase();$('records').replaceChildren();records.filter(r=>`${r.date} ${r.memo} ${r.fiscal_year} ${r.fiscal_quarter}`.toLowerCase().includes(filter)).forEach(r=>{const tr=document.createElement('tr');for(const value of [r.date,`${r.fiscal_year} ${r.fiscal_quarter}`,r.memo,fmt(Number(r.value))]){let td=document.createElement('td');td.textContent=value;tr.append(td)}let actions=document.createElement('td'),edit=document.createElement('button'),del=document.createElement('button');edit.textContent='Edit';edit.className='ghost';edit.onclick=()=>fillForm(r);del.textContent='Delete';del.onclick=async()=>{if(!confirm('Delete this financial record?'))return;try{await request('/api/data/'+encodeURIComponent(r.id),{method:'DELETE'});await loadData();notice('Record deleted')}catch(e){error(e)}};actions.append(edit,del);tr.append(actions);$('records').append(tr)})}
$('filter').oninput=renderData;async function loadData(){try{records=await request('/api/data');renderData()}catch(e){error(e)}};
$('data-form').onsubmit=async e=>{e.preventDefault();const id=$('record-id').value,payload={date:$('date').value,value:Number($('value').value),memo:$('memo').value,fiscal_year:Number($('year').value),fiscal_quarter:$('quarter').value,unit:'USD millions',source_document:'manual',method:'manual'};try{await request(id?'/api/data/'+encodeURIComponent(id):'/api/data',{method:id?'PUT':'POST',body:JSON.stringify(payload)});clearForm();await loadData();notice('Record saved successfully')}catch(e){error(e)}};
async function loadHistory(){try{const conversations=await request('/api/conversations');$('conversations').replaceChildren();if(!conversations.length){$('conversations').textContent='No conversations saved yet.';return}conversations.forEach(c=>{const div=document.createElement('div');div.className='conversation';let title=document.createElement('span');title.textContent=c.title||'Untitled';const buttons=document.createElement('div'),open=document.createElement('button'),del=document.createElement('button');open.textContent='Load';open.onclick=async()=>{try{const full=await request('/api/conversations/'+encodeURIComponent(c.id));conversationId=c.id;$('messages').replaceChildren();(full.messages||[]).forEach(m=>{if(['user','assistant'].includes(m.role))bubble(m.role,m.content)});switchTab('chat')}catch(e){error(e)}};del.textContent='Delete';del.className='ghost';del.onclick=async()=>{if(!confirm('Delete saved conversation?'))return;try{await request('/api/conversations/'+encodeURIComponent(c.id),{method:'DELETE'});if(conversationId===c.id)conversationId=null;await loadHistory()}catch(e){error(e)}};buttons.append(open,del);div.append(title,buttons);$('conversations').append(div)})}catch(e){error(e)}}$('history-refresh').onclick=loadHistory;
loadSummary();
