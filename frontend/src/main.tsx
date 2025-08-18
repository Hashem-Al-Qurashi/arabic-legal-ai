import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './App.css'

// 🚫 DISABLE SERVICE WORKERS - Clean up any existing registrations
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(registrations => {
    registrations.forEach(registration => {
      console.log('🚫 Unregistering service worker:', registration.scope);
      registration.unregister();
    });
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)