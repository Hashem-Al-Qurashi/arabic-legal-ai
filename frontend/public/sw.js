// حكم PWA Service Worker
// Progressive Web App Service Worker for Hokm AI Legal Assistant

const CACHE_NAME = 'hokm-ai-v1';
const RUNTIME_CACHE = 'hokm-runtime-v1';

// Critical app shell resources to cache
const APP_SHELL = [
  '/',
  '/index.html',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  // Add other critical resources
];

// Install event - cache app shell
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Service Worker: Caching app shell');
        return cache.addAll(APP_SHELL);
      })
      .then(() => {
        console.log('✅ Service Worker: App shell cached successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Service Worker: Failed to cache app shell:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE) {
              console.log('🗑️ Service Worker: Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker: Activated successfully');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Handle different types of requests
  if (url.pathname.startsWith('/api/')) {
    // API requests - network first, cache for offline
    event.respondWith(networkFirstStrategy(request));
  } else if (APP_SHELL.includes(url.pathname) || url.pathname === '/') {
    // App shell - cache first
    event.respondWith(cacheFirstStrategy(request));
  } else {
    // Other resources - stale while revalidate
    event.respondWith(staleWhileRevalidateStrategy(request));
  }
});

// Cache First Strategy (for app shell)
async function cacheFirstStrategy(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.error('Cache first strategy failed:', error);
    // Return offline fallback page if available
    return caches.match('/index.html');
  }
}

// Network First Strategy (for API calls)
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful API responses
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('Network failed, trying cache:', error);
    
    // Try to serve from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for API calls
    return new Response(
      JSON.stringify({
        error: 'لا يوجد اتصال بالإنترنت',
        offline: true,
        message: 'يرجى التحقق من اتصالك بالإنترنت والمحاولة مرة أخرى'
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        }
      }
    );
  }
}

// Stale While Revalidate Strategy (for other resources)
async function staleWhileRevalidateStrategy(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Fetch from network in background
  const networkResponsePromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    })
    .catch(() => cachedResponse);
  
  // Return cached version immediately, or wait for network
  return cachedResponse || networkResponsePromise;
}

// Background sync for queued messages
self.addEventListener('sync', (event) => {
  console.log('🔄 Service Worker: Background sync triggered');
  
  if (event.tag === 'send-queued-messages') {
    event.waitUntil(sendQueuedMessages());
  }
});

// Send queued messages when connection is restored
async function sendQueuedMessages() {
  try {
    console.log('📤 Service Worker: Sending queued messages...');
    
    // Get queued messages from IndexedDB
    const queuedMessages = await getQueuedMessages();
    
    for (const message of queuedMessages) {
      try {
        const response = await fetch('/api/chat/send', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${message.token}`
          },
          body: JSON.stringify(message.data)
        });
        
        if (response.ok) {
          // Remove from queue
          await removeFromQueue(message.id);
          console.log('✅ Service Worker: Message sent successfully');
        }
      } catch (error) {
        console.error('❌ Service Worker: Failed to send queued message:', error);
      }
    }
  } catch (error) {
    console.error('❌ Service Worker: Background sync failed:', error);
  }
}

// Placeholder functions for IndexedDB operations
async function getQueuedMessages() {
  // Implementation will be added with message queuing
  return [];
}

async function removeFromQueue(messageId) {
  // Implementation will be added with message queuing
  console.log('Removing message from queue:', messageId);
}

// Push notification handling
self.addEventListener('push', (event) => {
  console.log('📬 Service Worker: Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'رسالة جديدة من حكم',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    dir: 'rtl',
    lang: 'ar',
    vibrate: [200, 100, 200],
    actions: [
      {
        action: 'open',
        title: 'فتح التطبيق'
      },
      {
        action: 'close',
        title: 'إغلاق'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('حكم - المساعد القانوني', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Service Worker: Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

console.log('🎉 Service Worker: Loaded successfully - حكم PWA Ready!');