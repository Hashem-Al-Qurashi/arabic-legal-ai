// Service Worker for cache management
const CACHE_NAME = 'islamic-legal-ai-v1.0.0';
const urlsToCache = [
  '/',
  '/assets/index-933add3c.js',
  '/assets/index-ae9bc01c.css',
  '/vite.svg'
];

self.addEventListener('install', function(event) {
  // Skip waiting to activate immediately
  self.skipWaiting();
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('activate', function(event) {
  // Take control of all clients immediately
  event.waitUntil(self.clients.claim());
  
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          // Delete old caches
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', function(event) {
  // For HTML requests, always go to network first (cache-busting)
  if (event.request.destination === 'document') {
    event.respondWith(
      fetch(event.request)
        .catch(function() {
          return caches.match(event.request);
        })
    );
    return;
  }
  
  // For other resources, use cache first strategy
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

// Handle message from main thread to clear cache
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then(function(cacheNames) {
        return Promise.all(
          cacheNames.map(function(cacheName) {
            return caches.delete(cacheName);
          })
        );
      }).then(function() {
        // Reload all clients
        return self.clients.matchAll().then(function(clients) {
          clients.forEach(client => client.postMessage({type: 'CACHE_CLEARED'}));
        });
      })
    );
  }
});