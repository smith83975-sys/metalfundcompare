(function(){
 document.querySelectorAll('form.signup').forEach(function(f){
  f.addEventListener('submit',function(e){
   if(!window.fetch||!window.FormData) return;          // no JS support -> normal POST
   e.preventDefault();
   var msg=f.querySelector('.signup-msg'), btn=f.querySelector('button');
   btn.disabled=true; msg.textContent='Sending…'; msg.className='signup-msg';
   fetch(f.action,{method:'POST',body:new FormData(f),headers:{'Accept':'application/json'}})
    .then(function(r){return r.json().catch(function(){return {};}).then(function(j){return {ok:r.ok,j:j};});})
    .then(function(res){
      if(res.j.status==='quarantined' && res.j.url){        // Kit's spam check: send the visitor to Kit's verification page
        msg.textContent='One quick check… redirecting to our newsletter provider.'; msg.className='signup-msg ok';
        window.location.href=res.j.url; return;
      }
      if(res.ok && (!res.j.status || res.j.status==='success')){
        msg.textContent='Check your inbox to confirm your subscription.'; msg.className='signup-msg ok'; f.reset();
      } else {
        msg.textContent=(res.j.errors&&res.j.errors.messages&&res.j.errors.messages.join(' '))||'Something went wrong. Please try again.'; msg.className='signup-msg err';
      }
      btn.disabled=false;
    })
    .catch(function(){ f.submit(); });                    // network/CORS failure -> fall back to normal POST
  });
 });
})();
