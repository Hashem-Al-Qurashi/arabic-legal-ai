import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './App.css'

// 🔄 CACHE MANAGEMENT - Register service worker for proper cache control
if ('serviceWorker' in navigator) {
  // First unregister any existing service workers
  navigator.serviceWorker.getRegistrations().then(registrations => {
    registrations.forEach(registration => {
      console.log('🚫 Unregistering old service worker:', registration.scope);
      registration.unregister();
    });
  });
  
  // Register new service worker after cleanup
  setTimeout(() => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('✅ Service Worker registered:', registration.scope);
        
        // Listen for updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New content available, reload
                window.location.reload();
              }
            });
          }
        });
      })
      .catch(error => {
        console.log('❌ Service Worker registration failed:', error);
      });
  }, 1000);
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)