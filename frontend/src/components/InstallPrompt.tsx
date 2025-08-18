import React, { useState, useEffect } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
}

export const InstallPrompt: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showInstall, setShowInstall] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if app is already installed
    const checkInstalled = () => {
      // Check if running in standalone mode
      if (window.matchMedia('(display-mode: standalone)').matches) {
        setIsInstalled(true);
        return;
      }
      
      // Check if running as installed PWA
      if ((window.navigator as any).standalone === true) {
        setIsInstalled(true);
        return;
      }
    };

    checkInstalled();

    // Listen for install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShowInstall(true);
    };

    // Listen for app installed
    const handleAppInstalled = () => {
      console.log('✅ PWA was installed');
      setShowInstall(false);
      setDeferredPrompt(null);
      setIsInstalled(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    console.log(`User response to install prompt: ${outcome}`);

    if (outcome === 'accepted') {
      setShowInstall(false);
      setDeferredPrompt(null);
    }
  };

  const handleDismiss = () => {
    setShowInstall(false);
    // Store dismissal in localStorage to avoid showing again soon
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  };

  // Don't show if already installed or recently dismissed
  if (isInstalled || !showInstall || !deferredPrompt) {
    return null;
  }

  // Check if recently dismissed (within 24 hours)
  const dismissedTime = localStorage.getItem('pwa-install-dismissed');
  if (dismissedTime && Date.now() - parseInt(dismissedTime) < 24 * 60 * 60 * 1000) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: '#006C35',
        color: 'white',
        padding: '16px 24px',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0, 108, 53, 0.3)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        maxWidth: '90vw',
        direction: 'rtl' as const,
        textAlign: 'right' as const,
      }}
    >
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: '600', marginBottom: '4px' }}>
          📱 تثبيت التطبيق
        </div>
        <div style={{ fontSize: '14px', opacity: 0.9 }}>
          احصل على تجربة أفضل مع التطبيق
        </div>
      </div>
      
      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={handleInstallClick}
          style={{
            backgroundColor: 'white',
            color: '#006C35',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '8px',
            fontWeight: '600',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          تثبيت
        </button>
        
        <button
          onClick={handleDismiss}
          style={{
            backgroundColor: 'transparent',
            color: 'white',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            padding: '8px 12px',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          لاحقاً
        </button>
      </div>
    </div>
  );
};