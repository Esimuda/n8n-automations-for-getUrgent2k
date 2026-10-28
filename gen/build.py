import json, uuid, os, sys
BASE="appFGiMYmxwrcLgcv"
T={"Contributors":"tblsswkiEY1lsRMBJ","Gigs":"tblSAZtBJD7DuruFS","Projects":"tbl169BWKS5M54Rfc","Applications":"tbl1l8GgdTUDtaDa7","Submissions":"tbl9ZIdFLu40HQfCt","Payments":"tblJEb1wA2PaCAs6V","Incidents":"tblKRs1e85t7XI9bw","Nodes":"tblvp0C0F6NdQvcdm","Bugs":"tblvYK2lpXgT1zYPK","Email Outbox":"tblGleD2vdsbQ6bw4"}
CRED=json.loads(os.environ.get("AT_CRED","null"))
def rl(v): return {"__rl":True,"mode":"id","value":v}
class W:
    def __init__(s,name,note=""): s.name=name; s.nodes=[]; s.conn={}; s.x=0; s.note=note
    def add(s,name,typ,ver,params,y=0,creds=None):
        n={"id":str(uuid.uuid4()),"name":name,"type":typ,"typeVersion":ver,"position":[len(s.nodes)*220,y],"parameters":params}
        if creds: n["credentials"]=creds
        s.nodes.append(n); return name
    def at(s,name,op,table,y=0,**kw):
        p={"operation":op,"base":rl(BASE),"table":rl(T[table])}
        if op in("create","update"):
            p["columns"]={"mappingMode":"defineBelow","value":kw.get("cols",{}),"matchingColumns":["id"] if op=="update" else [],"schema":[]}
            p["options"]={"typecast":True}
        if op=="search":
            p["filterByFormula"]=kw.get("formula",""); p["options"]={}
            if kw.get("always"): pass
        if op=="get": p["id"]=kw["rid"]; p["options"]={}
        n=s.add(name,"n8n-nodes-base.airtable",2.1,p,y,{"airtableTokenApi":CRED} if CRED else None)
        s.nodes[-1]["alwaysOutputData"]=bool(kw.get("always"))
        return n
    def trig(s,name,table,field="Last Modified"):
        p={"pollTimes":{"item":[{"mode":"everyMinute"}]},"authentication":"airtableTokenApi","baseId":rl(BASE),"tableId":rl(T[table]),"triggerField":field,"additionalFields":{}}
        return s.add(name,"n8n-nodes-base.airtableTrigger",1,p,0,{"airtableTokenApi":CRED} if CRED else None)
    def sched(s,name,rule):
        return s.add(name,"n8n-nodes-base.scheduleTrigger",1.2,{"rule":{"interval":[rule]}})
    def code(s,name,js,y=0,mode="runOnceForAllItems"):
        return s.add(name,"n8n-nodes-base.code",2,{"mode":mode,"jsCode":js},y)
    def tg(s,name,text,y=0):
        # Email-to-owner notification (Telegram dropped per user): Set node with to/subject/text
        subj="GetUrgent2K: "+("Notification" if name=="Email Message" else name.replace("Email ",""))+" — "+s.name
        s.add(name,"n8n-nodes-base.set",3.4,{"mode":"manual","assignments":{"assignments":[
            {"id":str(uuid.uuid4()),"name":"to","type":"string","value":"babalolabowale01@gmail.com"},
            {"id":str(uuid.uuid4()),"name":"subject","type":"string","value":subj},
            {"id":str(uuid.uuid4()),"name":"text","type":"string","value":text}]},"options":{}},y)
        ob=s.at(name+" → Outbox","create","Email Outbox",y+120,cols={"To":"={{$json.to}}","Subject":"={{$json.subject}}","Body":"={{$json.text}}","Workflow":s.name,"Status":"Queued"})
        s.c(name,ob); return name
    def ifn(s,name,left,op,right,typ="string",y=0):
        o={"string":{"type":"string","operation":op},"boolean":{"type":"boolean","operation":op,"singleValue":True},"number":{"type":"number","operation":op}}[typ]
        if op in("empty","notEmpty"): o=dict(o,singleValue=True)
        c={"id":str(uuid.uuid4()),"leftValue":left,"rightValue":right,"operator":o}
        return s.add(name,"n8n-nodes-base.if",2.2,{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"loose","version":2},"conditions":[c],"combinator":"and"},"looseTypeValidation":True,"options":{}},y)
    def switch(s,name,expr,keys,y=0):
        rules=[{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"loose","version":2},"conditions":[{"id":str(uuid.uuid4()),"leftValue":expr,"rightValue":k,"operator":{"type":"string","operation":"equals"}}],"combinator":"and"},"renameOutput":True,"outputKey":k} for k in keys]
        return s.add(name,"n8n-nodes-base.switch",3.2,{"rules":{"values":rules},"options":{}},y)
    def hook(s,name,path):
        n=s.add(name,"n8n-nodes-base.webhook",2,{"httpMethod":"POST","path":path,"responseMode":"onReceived","options":{}})
        s.nodes[-1]["webhookId"]=str(uuid.uuid5(uuid.NAMESPACE_URL,path)); return n
    def c(s,a,b,out=0):
        m=s.conn.setdefault(a,{"main":[]})["main"]
        while len(m)<=out: m.append([])
        m[out].append({"node":b,"type":"main","index":0})
    def chain(s,*ns):
        for a,b in zip(ns,ns[1:]): s.c(a,b)
    def json(s):
        d={"name":s.name,"nodes":s.nodes,"connections":s.conn,"settings":{"executionOrder":"v1"}}
        if s.note: d["nodes"].append({"id":str(uuid.uuid4()),"name":"Note","type":"n8n-nodes-base.stickyNote","typeVersion":1,"position":[0,-300],"parameters":{"content":s.note,"width":500,"height":160}})
        return d
WF=[]
SUBID=os.environ.get("SUB_ID","")
def incident_call(w,name,y=0):
    return w.add(name,"n8n-nodes-base.executeWorkflow",1.2,{"workflowId":{"__rl":True,"mode":"id","value":SUBID or "SET_AFTER_IMPORT"},"workflowInputs":{"mappingMode":"defineBelow","value":{"source":"={{$json.source}}","description":"={{$json.description}}","severity":"={{$json.severity}}"},"matchingColumns":[],"schema":[{"id":k,"displayName":k,"type":"string","display":True,"required":False,"defaultMatch":False,"canBeUsedToMatch":True} for k in ("source","description","severity")]},"options":{"waitForSubWorkflow":False}},y)

# ---------- P1
w=W("Project 1 - Contributor Onboarding","Tally 'Contributor Onboarding' -> webhook /contributor-onboarding")
w.chain(w.hook("Webhook","contributor-onboarding"),
 w.code("Normalize Tally",open(os.path.dirname(__file__)+"/tally.js").read()+"""
const d=flat($input.first().json.body||$input.first().json);
return [{json:{Name:d['Name']||d['Full Name']||'',Phone:d['Phone']||'',Email:d['Email']||'',City:d['City']||'',Skills:d['Skills']||'',Availability:d['Availability']||'','Experience Level':d['Experience Level']||'','Payment Info Provided':!!d['Payment Info Provided'],Status:'Active','Verification Status':'Pending','Date Registered':new Date().toISOString().slice(0,10),'Last Active Date':new Date().toISOString().slice(0,10)}}];"""),
 w.at("Airtable Create","create","Contributors",cols={k:"={{$json['%s']}}"%k for k in ["Name","Phone","Email","City","Skills","Availability","Experience Level","Payment Info Provided","Status","Verification Status","Date Registered","Last Active Date"]}),
 w.tg("Email Message","=Welcome to GetUrgent2K, {{($json.fields||$json).Name}}! Your profile ({{($json.fields||$json).City}}) is registered. Complete your profile to unlock gigs."))
# Airtable-form path (no tunnel needed): new Contributors rows without Date Registered (webhook rows already have it)
w.chain(w.trig("Airtable Trigger (form)","Contributors","Created"),
 w.ifn("From Form?","={{($json.fields||$json)['Date Registered']||''}}","empty","",y=400),
 w.at("Stamp Contributor","update","Contributors",400,cols={"id":"={{$json.id}}","Date Registered":"={{$now.toISODate()}}","Last Active Date":"={{$now.toISODate()}}","Status":"Active","Verification Status":"Pending"}),
 w.tg("Email Message (form)","=Welcome to GetUrgent2K, {{($json.fields||$json).Name}}! Your profile ({{($json.fields||$json).City}}) is registered via the onboarding form. Complete your profile to unlock gigs.",400))
WF.append(w)
w=W("Project 1 - Profile Completeness")
w.chain(w.sched("Schedule Trigger",{"field":"hours","hoursInterval":24}),w.at("Airtable Search","search","Contributors"),
 w.code("Score Completeness","""const F=['Name','Phone','Email','City','Skills','Availability','Experience Level','Payment Info Provided'];
return items.map(i=>{const f=(i.json.fields||i.json);const have=F.filter(k=>{const v=f[k];return Array.isArray(v)?v.length>0:!!v}).length;const score=Math.round(have/F.length*100);const missing=F.filter(k=>{const v=f[k];return !(Array.isArray(v)?v.length:v)});return {json:{id:i.json.id,name:f.Name,score,missing:missing.join(', ')}}});"""),
 w.at("Airtable Update","update","Contributors",cols={"id":"={{$json.id}}","Profile Completeness":"={{$json.score}}"}))
w.c("Score Completeness",w.ifn("Below 80%","={{$json.score}}","lt",80,"number",200))
w.c("Below 80%",w.tg("Email Message","=Hi {{$json.name}}, your profile is {{$json.score}}% complete. Missing: {{$json.missing}}",200))
WF.append(w)
w=W("Project 1 - Inactivity Segmentation")
w.chain(w.sched("Schedule Trigger",{"field":"days","triggerAtHour":9}),
 w.at("Airtable Search","search","Contributors",formula="IS_BEFORE({Last Active Date}, DATEADD(TODAY(), -30, 'days'))"),
 w.code("Classify","""return items.map(i=>{const f=(i.json.fields||i.json);const d=(Date.now()-new Date(f['Last Active Date']))/864e5;return {json:{id:i.json.id,name:f.Name,days:Math.round(d),segment:d>=60?'Inactive':'At Risk'}}});"""),
 w.at("Airtable Update","update","Contributors",cols={"id":"={{$json.id}}","Segment":"={{$json.segment}}"}),
 w.code("Build Digest","const l=$('Classify').all().map(i=>`${i.json.name}: ${i.json.segment} (${i.json.days}d)`);return [{json:{digest:l.join('\\n')||'No inactive contributors'}}];"),
 w.tg("Email Message","=Inactivity digest:\n{{$json.digest}}"))
WF.append(w)
# ---------- P2
w=W("Project 2 - Gig Checklist")
w.chain(w.trig("Airtable Trigger","Gigs"),w.ifn("Is Draft","={{($json.fields||$json).Status}}","equals","Draft"),
 w.code("Checklist","""return items.map(it=>{const f=(it.json.fields||it.json);const missing=[];
if(!f['Compensation'])missing.push('Compensation');if(!f['City'])missing.push('City');
if(!f['Screening Questions'])missing.push('Screening Questions');if(!f['Evidence Requirements'])missing.push('Evidence Requirements');
if(!f['Deadline'])missing.push('Deadline');return {json:{id:it.json.id,title:f.Title,ready:missing.length===0,missing:missing.join(', ')}}});"""),
 w.ifn("Ready?","={{$json.ready}}","true",True,"boolean"))
w.c("Ready?",w.at("Set Ready","update","Gigs",cols={"id":"={{$json.id}}","Status":"Ready"}),0)
w.c("Ready?",w.tg("Email Message","=Gig {{$json.title}} ({{$json.id}}) is missing: {{$json.missing}}",200),1)
WF.append(w)
w=W("Project 2 - Gig Publishing")
w.chain(w.trig("Airtable Trigger","Gigs"),w.ifn("Is Published","={{($json.fields||$json).Status}}","equals","Published"),
 w.at("Find Contributors","search","Contributors",formula="=AND({City}='{{($json.fields||$json).City}}', FIND('{{($json.fields||$json).Type}}', ARRAYJOIN({Skills})))",always=True),
 w.code("Summarize","const n=$input.all().filter(i=>i.json.id).length;const g=($('Is Published').first().json.fields||$('Is Published').first().json);return [{json:{text:`Gig ${g.Title} published — ${n} eligible contributors found.`}}];"),
 w.tg("Email Message","={{$json.text}}"))
WF.append(w)
w=W("Project 2 - Fill Monitoring")
w.chain(w.sched("Schedule Trigger",{"field":"hours","hoursInterval":4}),w.at("Airtable Search","search","Gigs",formula="OR({Status}='Published', {Status}='Filling')"),
 w.code("Flag","""return items.map(item=>{const rate=Math.round((item.json.fields||item.json)['Fill Rate']||0);let flag='Green';if(rate<40)flag='Red';else if(rate<80)flag='Yellow';return {json:{id:item.json.id,title:(item.json.fields||item.json).Title,rate,flag}}});"""),
 w.ifn("Is Red","={{$json.flag}}","equals","Red"),w.tg("Email Message","=⚠️ {{$json.title}} is at {{$json.rate}}% fill — needs intervention."))
WF.append(w)
w=W("Project 2 - Deadline Alerts")
w.chain(w.sched("Schedule Trigger",{"field":"days","triggerAtHour":8}),w.at("Airtable Search","search","Gigs",formula="AND(IS_BEFORE({Deadline}, DATEADD(TODAY(), 3, 'days')), {Status}!='Closed')"),
 w.code("Level","""return items.map(item=>{const f=(item.json.fields||item.json);const fr=f['Fill Rate']||0;const h=(new Date(f['Deadline'])-new Date())/36e5;let level='ok';
if(h<=0)level='passed';else if(h<=24&&fr<80)level='escalate';else if(h<=72&&fr<60)level='warn';
return {json:{id:item.json.id,title:f.Title,level,fill:Math.round(fr),source:'Failed Workflow',severity:'P2',description:`Gig "${f.Title}" deadline passed at ${Math.round(fr)}% fill (gig ${item.json.id}).`}}});"""),
 w.switch("Route Level","={{$json.level}}",["warn","escalate","passed"]))
t=w.tg("Email Message","=⏰ {{$json.level.toUpperCase()}}: {{$json.title}} at {{$json.fill}}% fill",200)
w.c("Route Level",t,0);w.c("Route Level",t,1);w.c("Route Level",incident_call(w,"Create Incident (P6 sub-workflow)",400),2)
WF.append(w)
w=W("Project 2 - Low Fill Sweep")
w.chain(w.sched("Schedule Trigger",{"field":"days","triggerAtHour":8}),w.at("Airtable Search","search","Gigs",formula="AND({Qualified}<10, IS_BEFORE({Deadline}, DATEADD(TODAY(), 5, 'days')), {Status}!='Closed')",always=True),
 w.code("Digest","const t=$input.all().filter(i=>i.json.id).map(i=>(i.json.fields||i.json).Title);return [{json:{text:t.length?`Low-fill gigs (${t.length}): ${t.join(', ')}`:'No low-fill gigs today ✅'}}];"),
 w.tg("Email Message","={{$json.text}}"))
WF.append(w)
# ---------- P4 + P5A
w=W("Project 4 - Submission QA","Webhook /submit-evidence. Body: gigId (rec...), contributorId (rec...), evidence (url), notes. Pass branch = Project 5 Workflow A (Payment Calculation).")
w.chain(w.hook("Webhook","submit-evidence"),
 w.code("Normalize Tally",open(os.path.dirname(__file__)+"/tally.js").read()+"""
const d=flat($input.first().json.body||$input.first().json);
const ev=d['Evidence']||d['Evidence upload']||d.evidence;const evUrl=Array.isArray(ev)?(ev[0]&&ev[0].url):ev;
return [{json:{gigId:(d['Gig ID']||d.gigId||'').trim(),contributorId:(d['Contributor ID']||d.contributorId||'').trim(),evidence:evUrl||'',notes:d['Notes']||d.notes||''}}];"""),
 w.at("Airtable Create","create","Submissions",cols={"Gig":"={{[$json.gigId]}}","Contributor":"={{[$json.contributorId]}}","Evidence":"={{$json.evidence?[{url:$json.evidence}]:[]}}","Notes":"={{$json.notes}}","Submission Date":"={{$now.toISODate()}}","QA Status":"Pending"}),
 w.code("Webhook Prep","const n=$('Normalize Tally').first().json;return [{json:{...n,id:$input.first().json.id}}];"),
 w.code("QA Input","return $input.all();"),
 w.at("Get Gig","get","Gigs",rid="={{$('QA Input').first().json.gigId}}"),
 w.code("QA Checks","""const n=$('QA Input').first().json;const raw=$input.first().json;const gig=raw.fields||raw;
const checks={hasEvidence:!!n.evidence,withinDeadline:!gig['Deadline']||new Date().toISOString().slice(0,10)<=gig['Deadline']};
let status='Pass';if(!checks.hasEvidence)status='Major Issue';else if(!checks.withinDeadline)status='Suspicious';else if(!n.notes)status='Minor Issue';
return [{json:{id:n.id,status,checks,gigId:n.gigId,contributorId:n.contributorId,compensation:gig['Compensation']||0,gigTitle:gig.Title,city:gig.City,type:gig.Type}}];"""),
 w.at("Update QA Status","update","Submissions",cols={"id":"={{$json.id}}","QA Status":"={{$json.status}}"}),
 w.code("Restore QA","return [{json:$('QA Checks').first().json}];"),
 w.switch("Route QA","={{$json.status}}",["Pass","Minor Issue","Major Issue","Suspicious"]))
w.c("Route QA",w.at("Create Payment (P5 A)","create","Payments",200,cols={"Gig":"={{[$json.gigId]}}","Contributor":"={{[$json.contributorId]}}","Base Amount":"={{$json.compensation}}","Bonus":"0","Deductions":"0","Status":"Pending","Date Queued":"={{$now.toISODate()}}"}),0)
w.c("Route QA",w.tg("Email Correction","=Submission {{$json.id}} for {{$json.gigTitle}} needs a small correction (add notes/details).",400),1)
w.c("Route QA",w.tg("Email Rejection","=Submission {{$json.id}} rejected — no evidence. Finding replacement.",600),2)
w.c("Email Rejection",w.at("Find Replacement","search","Contributors",600,formula="=AND({City}='{{$('Restore QA').first().json.city}}', FIND('{{$('Restore QA').first().json.type}}', ARRAYJOIN({Skills})))"))
w.c("Route QA",w.tg("Email Suspicious","=🚩 Suspicious submission {{$json.id}} ({{$json.gigTitle}}) — submitted after deadline. Investigate.",800),3)
# Airtable-form path: new Submissions with empty/Pending QA Status
w.chain(w.trig("Airtable Trigger (form)","Submissions","Created"),
 w.ifn("Needs QA?","={{['','Pending'].includes(($json.fields||$json)['QA Status']||'')}}","true",True,"boolean",y=1000),
 w.code("Form Prep","""const it=$input.first().json;const f=it.fields||it;const ev=f.Evidence;
return [{json:{id:it.id,gigId:(f.Gig||[])[0]||'',contributorId:(f.Contributor||[])[0]||'',evidence:Array.isArray(ev)?((ev[0]&&ev[0].url)||''):(ev||''),notes:f.Notes||''}}];""",1000),
 "QA Input")
WF.append(w)
# ---------- P5
w=W("Project 5 - Payment SLA Monitor")
w.chain(w.sched("Schedule Trigger",{"field":"days","triggerAtHour":8}),w.at("Airtable Search","search","Payments",formula="AND({Status}='Pending', IS_BEFORE({SLA Deadline}, TODAY()))"),
 w.code("Digest","const r=$input.all().map(i=>`#${(i.json.fields||i.json)['Payment ID']} ₦${(i.json.fields||i.json)['Total Amount']} (due ${(i.json.fields||i.json)['SLA Deadline']})`);return [{json:{text:`💸 ${r.length} overdue payments:\\n`+r.join('\\n'),source:'Failed Payment',severity:'P2',description:`${r.length} payments past 3-day SLA: `+r.join('; ')}}];"),
 w.tg("Email Message","={{$json.text}}"))
w.c("Digest",incident_call(w,"Create Incident (P6 sub-workflow)",200))
WF.append(w)
w=W("Project 5 - Reconciliation")
w.chain(w.sched("Schedule Trigger",{"field":"days","triggerAtHour":7}),w.at("Passed Submissions","search","Submissions",formula="{QA Status}='Pass'",always=True),
 w.at("All Payments","search","Payments",always=True),
 w.code("Reconcile","""const key=f=>`${(f.Gig||[])[0]}|${(f.Contributor||[])[0]}`;
const subs=$('Passed Submissions').all().filter(i=>i.json.id).map(i=>key((i.json.fields||i.json)));
const pays=$('All Payments').all().filter(i=>i.json.id).map(i=>key((i.json.fields||i.json)));
const cnt={};pays.forEach(k=>cnt[k]=(cnt[k]||0)+1);
const noPay=subs.filter(k=>!pays.includes(k)),noPass=[...new Set(pays.filter(k=>!subs.includes(k)))],dups=Object.keys(cnt).filter(k=>cnt[k]>1);
return [{json:{noPay,noPass,dups,text:`🧾 Reconciliation: ${subs.length} passed / ${pays.length} payments\\nPass w/o payment: ${noPay.length}\\nPayment w/o pass: ${noPass.length}\\nDuplicates: ${dups.length}`}}];"""),
 w.tg("Email Message","={{$json.text}}"))
WF.append(w)
# ---------- P6
w=W("Project 6 - Incident Intake (Sub-workflow)")
w.chain(w.add("Execute Workflow Trigger","n8n-nodes-base.executeWorkflowTrigger",1.1,{"workflowInputs":{"values":[{"name":"source"},{"name":"description"},{"name":"severity"}]}}),
 w.code("Default Severity","return items.map(i=>({json:{...i.json,severity:i.json.severity||'P3',source:i.json.source||'Failed Workflow'}}));"),
 w.at("Airtable Create","create","Incidents",cols={"Source":"={{$json.source}}","Severity":"={{$json.severity}}","Description":"={{$json.description}}","Status":"Open","Created Date":"={{$now.toISO()}}"}),
 w.switch("Route Severity","={{($json.fields||$json).Severity}}",["P1","P2","P3"]))
t=w.tg("Email Message","=🚨 {{($json.fields||$json).Severity}} incident ({{($json.fields||$json).Source}}): {{($json.fields||$json).Description}}",200)
w.c("Route Severity",t,0);w.c("Route Severity",t,1)
WF.append(w)
w=W("Project 6 - Incident Webhook Intake","Optional: Tally 'Support / Incident' form -> /incident-intake, forwards to sub-workflow.")
w.chain(w.hook("Webhook","incident-intake"),w.code("Normalize",open(os.path.dirname(__file__)+"/tally.js").read()+"\nconst d=flat($input.first().json.body||$input.first().json);return [{json:{source:d.Source||d.source||'Support Form',severity:d.Severity||d.severity||'',description:d.Description||d.description||''}}];"),incident_call(w,"Create Incident (P6 sub-workflow)"))
WF.append(w)
w=W("Project 6 - SLA Escalation")
w.chain(w.sched("Schedule Trigger",{"field":"minutes","minutesInterval":30}),w.at("Airtable Search","search","Incidents",formula="AND({Status}!='Resolved', IS_BEFORE({SLA Deadline}, NOW()))"),
 w.tg("Email Message","=⛔ SLA BREACH: {{($json.fields||$json).Severity}} {{($json.fields||$json).Source}} — {{($json.fields||$json).Description}} (owner: {{($json.fields||$json).Owner || 'unassigned'}})"))
WF.append(w)
w=W("Project 6 - Postmortem Generator (template draft, swap for LLM later)","Code node generates a template postmortem instead of calling Anthropic. Swap 'Postmortem Draft' for HTTP Request to an LLM when a key exists.")
w.chain(w.trig("Airtable Trigger","Incidents"),w.ifn("Is Resolved","={{($json.fields||$json).Status}}","equals","Resolved"),
 w.ifn("No Postmortem Yet","={{($json.fields||$json).Postmortem}}","empty","","string"),
 w.code("Postmortem Draft (template)","""return items.map(i=>{const f=(i.json.fields||i.json);const sevImpact={P1:'Critical — core flow blocked for contributors/clients.',P2:'Significant — degraded operations, workaround needed.',P3:'Minor — limited impact.'}[f.Severity]||'Unassessed.';
const t=`POSTMORTEM (template draft — swap for LLM later)
What happened: ${f.Description||'n/a'} (source: ${f.Source||'n/a'}, severity ${f.Severity||'n/a'}, opened ${f['Created Date']||'n/a'}).
Root cause: Initial assessment points to ${ {'Failed Payment':'the payment pipeline/SLA queue','Failed Workflow':'an automation or gig-ops process gap','Bug':'a product defect','QA Failure':'submission quality controls','Complaint':'a contributor/client experience gap','Support Form':'a support-reported issue'}[f.Source]||'an unconfirmed cause'}; confirm with owner ${f.Owner||'(unassigned)'}.
Impact: ${sevImpact}
Resolution: ${f['Resolution Notes']||'See resolution notes.'}
Prevention: Add a monitor/alert for this failure mode, document the fix in the runbook, and review in the Weekly Operating Review.`;
return {json:{id:i.json.id,draft:t}}});"""),
 w.at("Airtable Update","update","Incidents",cols={"id":"={{$json.id}}","Postmortem":"={{$json.draft}}"}))
WF.append(w)
# ---------- P3
w=W("Project 3 - Intake Scoping (template draft, swap for LLM later)","Webhook /client-intake. Scoping is a Code-node template instead of Anthropic.")
w.chain(w.hook("Webhook","client-intake"),
 w.code("Normalize Tally",open(os.path.dirname(__file__)+"/tally.js").read()+"""
const d=flat($input.first().json.body||$input.first().json);const num=v=>Number(String(v||0).replace(/[^0-9.]/g,''))||0;
return [{json:{'Client Name':d['Client Name']||'','Research Objective':d['Research Objective']||'',Location:d['Location']||'','Sample Size Requested':num(d['Sample Size Requested']),'Target Audience':d['Target Audience']||'',Method:d['Method']||'',Deadline:d['Deadline']||null,'Compensation Budget':num(d['Compensation Budget']),'Evidence Requirements':d['Evidence Requirements']||''}}];"""),
 w.at("Airtable Create","create","Projects",cols=dict({k:"={{$json['%s']}}"%k for k in ["Client Name","Research Objective","Location","Sample Size Requested","Target Audience","Method","Deadline","Compensation Budget","Evidence Requirements"]},Status="Intake")),
 w.code("Scoping Draft (template)","""const f=($input.first().json.fields||$input.first().json);const n=f['Sample Size Requested']||0;const target=Math.ceil(n*1.25);
const ev={'Mystery Shopping':'receipt photo, storefront photo, timed visit notes','Interview':'audio recording + consent, transcript notes','Market Observation':'geotagged photos, price/shelf log','Retailer Verification':'storefront photo with GPS, owner contact, shelf photo','UGC':'original video/photo, usage rights consent'}[f.Method]||'photo evidence + notes';
const days=Math.max(3,Math.ceil(target/10)+2);const risk=n>100?'high':n>40?'medium':'low';
const why={high:'large sample relative to one-city contributor pool',medium:'moderate sample; may need cross-city recruiting',low:'small sample, well within node capacity'}[risk];
return [{json:{id:$input.first().json.id,draft:`[Template draft — swap for LLM later] Recruit ${target} (${n} + 25% buffer) in ${f.Location||'TBD'} via ${f.Method||'TBD'}. Evidence: ${ev}. Est. duration: ${days} days. Risk: ${risk} — ${why}.`}}];"""),
 w.at("Airtable Update","update","Projects",cols={"id":"={{$json.id}}","Scoping Draft":"={{$json.draft}}","Status":"Scoped"}),
 w.tg("Email Message","=New project scoped, please review in Airtable: {{($json.fields||$json)['Client Name']}} ({{$json.id}})"))
w.chain(w.trig("Airtable Trigger (form)","Projects","Created"),
 w.ifn("Not Scoped Yet?","={{($json.fields||$json)['Scoping Draft']||''}}","empty","",y=400),
 "Scoping Draft (template)")
WF.append(w)
w=W("Project 3 - Approval Conversion")
w.chain(w.trig("Airtable Trigger","Projects"),w.ifn("Is Approved","={{($json.fields||$json).Status}}","equals","Approved"),
 w.at("Create Gig","create","Gigs",cols={"Title":"={{($json.fields||$json)['Client Name']}} - {{($json.fields||$json).Method}}","City":"={{($json.fields||$json).Location}}","Type":"={{($json.fields||$json).Method}}","Compensation":"={{($json.fields||$json)['Compensation Budget']}}","Required Participants":"={{($json.fields||$json)['Sample Size Requested']}}","Evidence Requirements":"={{($json.fields||$json)['Evidence Requirements']}}","Deadline":"={{($json.fields||$json).Deadline}}","Status":"Draft"}),
 w.at("Mark Converted","update","Projects",cols={"id":"={{$('Is Approved').item.json.id}}","Status":"Converted"}))
WF.append(w)
# ---------- P7
w=W("Project 7 - Weekly Node Report","Workflow A (report) + Workflow B (underperformance alert) chained after the Code node, per guide 7.3.")
w.chain(w.sched("Schedule Trigger",{"field":"weeks","triggerAtDay":[5],"triggerAtHour":17}),
 w.at("Airtable Search","search","Nodes",formula="IS_AFTER({Week Of}, DATEADD(TODAY(), -7, 'days'))"),
 w.code("Metrics","""return items.map(item=>{const f=(item.json.fields||item.json);
const activation=f['Registrations']?Math.round((f['Verified Contributors']/f['Registrations'])*100):0;
const completion=f['Tasks Dispatched']?Math.round((f['Tasks Completed']/f['Tasks Dispatched'])*100):0;
const productivity=f['Cost']?Number((f['Tasks Completed']/f['Cost']*1000).toFixed(2)):0;
return {json:{id:item.json.id,city:f.City,activation,completion,productivity,margin:(f.Revenue||0)-(f.Cost||0),priorActivation:f['Prior Week Activation %']??null,priorCompletion:f['Prior Week Completion %']??null}}});"""),
 w.code("Build Report","const l=$input.all().map(i=>`${i.json.city}: activation ${i.json.activation}%, completion ${i.json.completion}%, tasks/₦1k ${i.json.productivity}, margin ₦${i.json.margin}`);return [{json:{text:'📊 Weekly Node Report\\n'+l.join('\\n')}}];"),
 w.tg("Email Message","={{$json.text}}"))
w.c("Metrics",w.ifn("Activation Drop >15","={{$json.priorActivation !== null && $json.activation < $json.priorActivation - 15}}","true",True,"boolean",250))
w.c("Activation Drop >15",w.tg("Email Underperformance","=📉 Underperformance: {{$json.city}} activation {{$json.activation}}% vs prior {{$json.priorActivation}}%",250),0)
w.c("Metrics",w.at("Update Prior Week","update","Nodes",450,cols={"id":"={{$json.id}}","Prior Week Activation %":"={{$json.activation}}","Prior Week Completion %":"={{$json.completion}}"}))
WF.append(w)
# ---------- P8
def brief(name,weekly):
    w=W(name,"Six Airtable searches -> Merge(append) -> Code formats -> Code template brief (swap for LLM later).")
    w.sched("Schedule Trigger",{"field":"weeks","triggerAtDay":[5],"triggerAtHour":17} if weekly else {"field":"days","triggerAtHour":8})
    S=[("At-Risk Gigs","Gigs","AND({Fill Rate}<40, OR({Status}='Published',{Status}='Filling'))" if not weekly else ""),
       ("Overdue Payments","Payments","AND({Status}='Pending', IS_BEFORE({SLA Deadline}, TODAY()))" if not weekly else ""),
       ("Open P1-P2 Incidents","Incidents","AND({Status}!='Resolved', OR({Severity}='P1',{Severity}='P2'))" if not weekly else ""),
       ("New Bugs","Bugs","IS_AFTER({Reported Date}, DATEADD(TODAY(), -%d, 'days'))"%(7 if weekly else 1) if not weekly else ""),
       ("Inactive Contributors","Contributors","OR({Segment}='At Risk',{Segment}='Inactive')" if not weekly else ""),
       ("Node Numbers","Nodes","IS_AFTER({Week Of}, DATEADD(TODAY(), -7, 'days'))")]
    m=w.add("Merge","n8n-nodes-base.merge",3.1,{"numberInputs":6},300)
    for idx,(n,t,f) in enumerate(S):
        w.at(n,"search",t,idx*120,formula=f,always=True); w.c("Schedule Trigger",n)
        w.code("Tag "+n,"return $input.all().filter(i=>i.json.id).map(i=>({json:{section:%s,...(i.json.fields||i.json),_id:i.json.id}})).concat($input.all().filter(i=>i.json.id).length?[]:[{json:{section:%s,_empty:true}}]);"%(json.dumps(n),json.dumps(n)),idx*120)
        w.c(n,"Tag "+n); w.conn.setdefault("Tag "+n,{"main":[[]]})["main"][0].append({"node":"Merge","type":"main","index":idx})
    js_fmt="""const by={};for(const i of $input.all()){const s=i.json.section;by[s]=by[s]||[];if(!i.json._empty)by[s].push(i.json)}
return [{json:{by,counts:Object.fromEntries(Object.entries(by).map(([k,v])=>[k,v.length]))}}];"""
    w.chain("Merge",w.code("Format Data",js_fmt,300))
    if not weekly:
        js="""const {by,counts}=$json;const crit=[],att=[],ok=[];
(by['Open P1-P2 Incidents']||[]).forEach(x=>crit.push(`${x.Severity} incident: ${x.Description}`));
(by['Overdue Payments']||[]).forEach(x=>crit.push(`Overdue payment #${x['Payment ID']} ₦${x['Total Amount']}`));
(by['At-Risk Gigs']||[]).forEach(x=>att.push(`Low fill: ${x.Title} (${Math.round(x['Fill Rate']||0)}%)`));
(by['New Bugs']||[]).forEach(x=>att.push(`New bug (${x.Severity}): ${x.Feature}`));
if(counts['Inactive Contributors'])att.push(`${counts['Inactive Contributors']} contributors at risk/inactive`);
(by['Node Numbers']||[]).forEach(x=>ok.push(`${x.City}: ${x['Tasks Completed']}/${x['Tasks Dispatched']} tasks`));
const s=a=>a.length?a.map(x=>'• '+x).join('\\n'):'• None';
return [{json:{text:`☀️ Daily Ops Brief (template draft — swap for LLM later)\\n\\n🔴 Critical\\n${s(crit)}\\n\\n🟡 Attention\\n${s(att)}\\n\\n🟢 Healthy\\n${s(ok)}`}}];"""
    else:
        js="""const {by,counts}=$json;const n=by['Node Numbers']||[];const sum=k=>n.reduce((a,x)=>a+(x[k]||0),0);
const sec=(t,l)=>`*${t}*\\n`+l.map(x=>'• '+x).join('\\n');
const g=by['At-Risk Gigs']||[];const p=by['Overdue Payments']||[];const inc=by['Open P1-P2 Incidents']||[];const b=by['New Bugs']||[];const c=by['Inactive Contributors']||[];
const text=['📅 Weekly Operating Review (template draft — swap for LLM later)',
sec('Growth',[`Registrations: ${sum('Registrations')}`,`Verified: ${sum('Verified Contributors')}`,`Contributors on file: ${c.length}`,`At risk/inactive: ${c.filter(x=>['At Risk','Inactive'].includes(x.Segment)).length}`]),
sec('Marketplace',[`Gigs: ${g.length}`,`Open/filling: ${g.filter(x=>['Published','Filling'].includes(x.Status)).length}`,`Avg fill: ${g.length?Math.round(g.reduce((a,x)=>a+(x['Fill Rate']||0),0)/g.length):0}%`]),
sec('Financial',[`Payments: ${p.length}`,`Pending: ${p.filter(x=>x.Status==='Pending').length}`,`Paid ₦${p.filter(x=>x.Status==='Paid').reduce((a,x)=>a+(x['Total Amount']||0),0)}`,`Node revenue ₦${sum('Revenue')} / cost ₦${sum('Cost')}`]),
sec('Product',[`Bugs: ${b.length}`,`Open: ${b.filter(x=>x.Status!=='Fixed').length}`,`Critical/High: ${b.filter(x=>['Critical','High'].includes(x.Severity)).length}`]),
sec('Network/Nodes',n.map(x=>`${x.City}: ${x['Tasks Completed']}/${x['Tasks Dispatched']} tasks, ${x['Businesses Onboarded']} businesses`)),
sec('Operations',[`Incidents: ${inc.length}`,`Unresolved: ${inc.filter(x=>x.Status!=='Resolved').length}`])].join('\\n\\n');
return [{json:{text}}];"""
    w.chain("Format Data",w.code("Brief Draft (template)",js,300),w.tg("Email Message","={{$json.text}}",300))
    return w
WF.append(brief("Project 8 - Daily Ops Brief (template draft, swap for LLM later)",False))
WF.append(brief("Project 8 - Weekly Operating Review (template draft, swap for LLM later)",True))
w=W("Project 8 - Bug Report Intake","Tally 'Bug Report' -> /bug-report")
w.chain(w.hook("Webhook","bug-report"),w.code("Normalize Tally",open(os.path.dirname(__file__)+"/tally.js").read()+"\nconst d=flat($input.first().json.body||$input.first().json);return [{json:{Feature:d.Feature||d.feature||'',Severity:d.Severity||d.severity||'Low'}}];"),
 w.at("Airtable Create","create","Bugs",cols={"Feature":"={{$json.Feature}}","Severity":"={{$json.Severity}}","Status":"Open","Reported Date":"={{$now.toISODate()}}"}),
 w.tg("Email Message","=🐞 New bug reported ({{($json.fields||$json).Severity}}): {{($json.fields||$json).Feature}}"))
w.chain(w.trig("Airtable Trigger (form)","Bugs","Created"),
 w.ifn("From Form?","={{($json.fields||$json).Status||''}}","empty","",y=400),
 w.at("Stamp Bug","update","Bugs",400,cols={"id":"={{$json.id}}","Status":"Open","Reported Date":"={{$now.toISODate()}}","Severity":"={{($json.fields||$json).Severity||'Low'}}"}),
 w.tg("Email Message (form)","=🐞 New bug reported via form ({{($json.fields||$json).Severity}}): {{($json.fields||$json).Feature}}",400))
WF.append(w)
out=sys.argv[1]
for w in WF:
    fn="".join(ch if ch.isalnum() else "_" for ch in w.name.split(" (")[0]).strip("_")
    json.dump(w.json(),open(f"{out}/{fn}.json","w"),indent=1,ensure_ascii=False)
print(len(WF))
