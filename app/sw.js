// Firn: app-schil en kaart offline beschikbaar. Elke versie krijgt een eigen cache, zodat app en teksten bij elkaar horen.
const V='firn-shell-__V__',ST='firn-static-1';
const SHELL=['./','index.html','manifest.webmanifest','icon-192.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).catch(()=>{}).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x.startsWith('firn')&&x!==V&&x!==ST).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
  const stat=/\/(relief|media)\//.test(u.pathname);
  if(stat){e.respondWith(caches.open(ST).then(c=>c.match(e.request).then(r=>r||fetch(e.request).then(n=>{if(n.ok)c.put(e.request,n.clone());return n}))));return}
  e.respondWith(fetch(e.request).then(n=>{if(n.ok){const c=n.clone();caches.open(V).then(x=>x.put(e.request,c))}return n}).catch(()=>caches.match(e.request).then(r=>r||caches.match(e.request,{ignoreSearch:true}))))});
