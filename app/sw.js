// Firn: app-schil en kaart offline beschikbaar. Netwerk eerst voor pagina's, cache eerst voor tegels en foto's.
const V='firn-v1',SHELL=['./','index.html','lang-nl.js','lang-en.js','lang-de.js','lang-fr.js','images.js','kaart/','kaart/index.html','kaart/leaflet.js','kaart/leaflet.css','kaart/map-data.js','manifest.webmanifest','icon-192.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==location.origin)return;
  const stat=/\/(relief|media)\//.test(u.pathname);
  e.respondWith(stat?caches.match(e.request).then(r=>r||fetch(e.request).then(n=>{const c=n.clone();caches.open(V).then(x=>x.put(e.request,c));return n}))
    :fetch(e.request).then(n=>{const c=n.clone();caches.open(V).then(x=>x.put(e.request,c));return n}).catch(()=>caches.match(e.request,{ignoreSearch:true})))});
