// Flatten Tally payload {data:{fields:[{label,value,options}]}} or plain JSON
function flat(b){ if(b&&b.data&&Array.isArray(b.data.fields)){const o={};for(const f of b.data.fields){let v=f.value;if(Array.isArray(v)&&f.options){v=v.map(id=>(f.options.find(x=>x.id===id)||{}).text||id);if(f.type==='DROPDOWN'||f.type==='MULTIPLE_CHOICE')v=v[0];}o[f.label]=v;}return o;} return b||{}; }
