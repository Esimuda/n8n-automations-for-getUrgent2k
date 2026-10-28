const fs=require('fs');const W=f=>JSON.parse(fs.readFileSync('workflows/'+f));
function run(wf,node,items,refs={}){const n=W(wf).nodes.find(x=>x.name===node);
 const $=k=>({first:()=>refs[k][0],all:()=>refs[k],item:refs[k][0]});const $input={first:()=>items[0],all:()=>items};
 return new Function('items','$input','$','$json',n.parameters.jsCode)(items,$input,$,items[0]&&items[0].json);}
const r={};
r.checklist=run('Project_2___Gig_Checklist.json','Checklist',[{json:{id:'rec1',fields:{Title:'A',City:'Lagos'}}},{json:{id:'rec2',fields:{Title:'B',City:'Kano',Compensation:5000,'Screening Questions':'q','Evidence Requirements':'e',Deadline:'2026-11-05'}}}]).map(i=>i.json);
r.fill=run('Project_2___Fill_Monitoring.json','Flag',[{json:{id:'g',fields:{Title:'X','Fill Rate':25}}},{json:{id:'h',fields:{Title:'Y','Fill Rate':90}}}]).map(i=>i.json.flag);
r.deadline=run('Project_2___Deadline_Alerts.json','Level',[{json:{id:'g',fields:{Title:'X','Fill Rate':20,Deadline:'2026-10-27'}}},{json:{id:'h',fields:{Title:'Y','Fill Rate':50,Deadline:'2026-10-30'}}}]).map(i=>i.json.level);
const tallyBody={body:{data:{fields:[{label:'Gig ID',value:'recGIG'},{label:'Contributor ID',value:'recC'},{label:'Evidence upload',value:[{url:'https://x/y.jpg'}]},{label:'Notes',value:'ok'}]}}};
const norm=run('Project_4___Submission_QA.json','Normalize Tally',[{json:tallyBody}]);r.norm=norm[0].json;
r.qa=run('Project_4___Submission_QA.json','QA Checks',[{json:{fields:{Deadline:'2026-11-30',Compensation:8000,Title:'G'}}}],{'Normalize Tally':norm,'Airtable Create':[{json:{id:'recSUB'}}]})[0].json.status;
r.recon=run('Project_5___Reconciliation.json','Reconcile',[],{'Passed Submissions':[{json:{id:1,fields:{Gig:['g1'],Contributor:['c1']}}},{json:{id:2,fields:{Gig:['g2'],Contributor:['c2']}}}],'All Payments':[{json:{id:3,fields:{Gig:['g1'],Contributor:['c1']}}},{json:{id:4,fields:{Gig:['g1'],Contributor:['c1']}}}]})[0].json.text;
r.scope=run('Project_3___Intake_Scoping.json','Scoping Draft (template)',[{json:{id:'p',fields:{'Sample Size Requested':40,Location:'Lagos',Method:'Interview'}}}])[0].json.draft;
r.pm=run('Project_6___Postmortem_Generator.json','Postmortem Draft (template)',[{json:{id:'i',fields:{Source:'Failed Payment',Severity:'P1',Description:'Payout API down','Resolution Notes':'Retried batch'}}}])[0].json.draft.slice(0,120);
const m=run('Project_7___Weekly_Node_Report.json','Metrics',[{json:{id:'n',fields:{City:'Kano',Registrations:60,'Verified Contributors':24,'Tasks Dispatched':30,'Tasks Completed':17,Cost:120000,Revenue:150000,'Prior Week Activation %':62}}}]);r.node=m[0].json;
const merged=[{json:{section:'Open P1-P2 Incidents',Severity:'P1',Description:'Down'}},{json:{section:'Node Numbers',City:'Lagos','Tasks Completed':5,'Tasks Dispatched':6}},{json:{section:'New Bugs',_empty:true}}];
const fm=run('Project_8___Daily_Ops_Brief.json','Format Data',merged);r.brief=run('Project_8___Daily_Ops_Brief.json','Brief Draft (template)',fm)[0].json.text;
r.weekly=run('Project_8___Weekly_Operating_Review.json','Brief Draft (template)',run('Project_8___Weekly_Operating_Review.json','Format Data',merged))[0].json.text.slice(0,200);
console.log(JSON.stringify(r,null,1));
