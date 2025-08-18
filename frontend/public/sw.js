// PWA Service Worker - Network First (No Offline Mode)
const CACHE_NAME = 'hokm-legal-ai-v2.0.0';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Install - cache only essential static assets
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Installing...');
  self.skipWaiting();
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('💾 Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .catch(err => console.log('❌ Service Worker: Cache failed', err))
  );
});

// Activate - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker: Activating...');
  event.waitUntil(self.clients.claim());
  
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️ Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      )
    )
  );
});

// Fetch - Network First Strategy (NO OFFLINE FALLBACK)
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) return;
  
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Network request successful - return response
        console.log('🌐 Service Worker: Network response for:', event.request.url);
        return response;
      })
      .catch(error => {
        // Network failed - only serve cached static assets
        console.log('⚠️ Service Worker: Network failed for:', event.request.url);
        
        if (event.request.destination === 'document') {
          return caches.match('/');
        }
        
        // For other resources, try cache but don't create offline experience
        return caches.match(event.request);
      })
  );
});

// Handle cache management messages
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    console.log('🧹 Service Worker: Clearing all caches');
    event.waitUntil(
      caches.keys().then(cacheNames =>
        Promise.all(
          cacheNames.map(cacheName => caches.delete(cacheName))
        )
      ).then(() => {
        return self.clients.matchAll().then(clients => {
          clients.forEach(client => 
            client.postMessage({type: 'CACHE_CLEARED'})
          );
        });
      })
    );
  }
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});