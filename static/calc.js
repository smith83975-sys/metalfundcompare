(function(){
 var F=window.FUNDS||[], picks=document.getElementById('picks'), out=document.getElementById('out');
 var pre=new URLSearchParams(location.search).get('f'), defs=[pre||'GLD','GLDM','IAU'];
 function opt(sel){return '<option value="">— custom fee —</option>'+F.map(function(f){return '<option value="'+f.t+'"'+(f.t===sel?' selected':'')+'>'+f.t+' — '+f.n+' ('+f.fee+'%'+(f.s==='unverified'?'†':'')+')</option>'}).join('')}
 for(var i=0;i<3;i++){picks.insertAdjacentHTML('beforeend','<label>Fund '+(i+1)+'<select class="pf">'+opt(defs[i])+'</select><input class="cf" type="number" step="0.01" placeholder="custom fee %"></label>')}
 function fee(i){var s=document.querySelectorAll('.pf')[i].value,c=document.querySelectorAll('.cf')[i].value; if(s){var f=F.find(function(x){return x.t===s});return {n:f.t+(f.s==='unverified'?'†':''),fee:f.fee}} if(c!=='')return {n:'Custom '+c+'%',fee:parseFloat(c)}; return null}
 function money(v){return '$'+Math.round(v).toLocaleString()}
 function run(){var a=+document.getElementById('amt').value||0,y=+document.getElementById('yrs').value||0,g=(+document.getElementById('gr').value||0)/100;
  var base=a*Math.pow(1+g,y), h='<table class="res"><tr><th>Fund</th><th>Fee</th><th>Value after '+y+' yrs</th><th>Fees cost you</th></tr>';
  for(var i=0;i<3;i++){var f=fee(i); if(!f)continue; var v=a*Math.pow((1+g)*(1-f.fee/100),y); h+='<tr><td>'+f.n+'</td><td>'+f.fee.toFixed(2)+'%</td><td>'+money(v)+'</td><td><b>'+money(base-v)+'</b></td></tr>'}
  out.innerHTML=h+'</table><p class="small muted">Without any fee: '+money(base)+'.</p>'}
 document.querySelector('.calc').addEventListener('input',run); document.querySelector('.calc').addEventListener('change',run); run();
})();
