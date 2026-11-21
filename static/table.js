(function(){
 var tb=document.querySelector('#funds tbody'); if(!tb) return;
 var rows=[].slice.call(tb.rows), q=document.getElementById('q'), fm=document.getElementById('f-metal'), ft=document.getElementById('f-type'), fx=document.getElementById('f-tax'), fu=document.getElementById('f-us'), cnt=document.getElementById('count');
 var params=new URLSearchParams(location.search); if(params.get('metal')) fm.value=params.get('metal'); if(params.get('type')) ft.value=params.get('type');
 function apply(){var s=q.value.trim().toLowerCase(),n=0;
  rows.forEach(function(r){var d=r.dataset,ok=(!s||(d.t+' '+d.n).toLowerCase().indexOf(s)>-1)&&(!fm.value||d.m===fm.value)&&(!ft.value||d.ty===ft.value)&&(!fx.value||d.tax.indexOf(fx.value)===0&&(fx.value!=='ric'||d.tax==='ric'))&&(!fu.checked||d.us==='1');
   r.style.display=ok?'':'none'; if(ok)n++;});
  cnt.textContent=n+' funds';}
 [q,fm,ft,fx,fu].forEach(function(e){e.addEventListener('input',apply);e.addEventListener('change',apply)});
 var num={fee:1,aum:1,pd:1};
 document.querySelectorAll('#funds thead th').forEach(function(th){th.addEventListener('click',function(){
  var k=th.dataset.k, asc=!th.classList.contains('asc');
  document.querySelectorAll('#funds thead th').forEach(function(x){x.classList.remove('asc','desc')}); th.classList.add(asc?'asc':'desc');
  rows.sort(function(a,b){var x=a.dataset[k],y=b.dataset[k];
   if(num[k]){ if(x===''&&y==='')return 0; if(x==='')return 1; if(y==='')return -1; return (parseFloat(x)-parseFloat(y))*(asc?1:-1);}
   return x.localeCompare(y)*(asc?1:-1);});
  rows.forEach(function(r){tb.appendChild(r)});});});
 apply();
})();
