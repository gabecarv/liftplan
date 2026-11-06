const C='liftplan-v8';const FILES=['./','./index.html','./manifest.json','./icon.svg','./icon-180.png','./icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const nav=e.request.mode==='navigate'||e.request.url.endsWith('/index.html')||e.request.url.endsWith('/');const req=nav?new Request(e.request.url,{cache:'no-store'}):e.request;e.respondWith(fetch(req).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r;}).catch(()=>caches.match(e.request)));});
