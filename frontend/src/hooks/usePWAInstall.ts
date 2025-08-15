import { useState, useEffect } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface PWAInstallState {
  isInstallable: boolean;
  isInstalled: boolean;
  showInstallPrompt: boolean;
  promptInstall: () => Promise<void>;
  dismissPrompt: () => void;
}

export const usePWAInstall = (): PWAInstallState => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);

  useEffect(() => {
    // Check if app is already installed
    const checkIfInstalled = () => {
      // Method 1: Check display mode
      const isDisplayModeStandalone = window.matchMedia('(display-mode: standalone)').matches;
      
      // Method 2: Check if running in PWA context
      const isInWebAppiOS = (window.navigator as any).standalone === true;
      
      // Method 3: Check if installed via Chrome
      const isInWebAppChrome = window.matchMedia('(display-mode: standalone)').matches;

      setIsInstalled(isDisplayModeStandalone || isInWebAppiOS || isInWebAppChrome);
    };

    checkIfInstalled();

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      console.log('📱 PWA: Install prompt available');
      e.preventDefault();
      
      const installEvent = e as BeforeInstallPromptEvent;
      setDeferredPrompt(installEvent);
      setIsInstallable(true);
      
      // Show custom install prompt after a delay (don't be too pushy)
      setTimeout(() => {
        if (!isInstalled && !localStorage.getItem('pwa-install-dismissed')) {
          setShowInstallPrompt(true);
        }
      }, 5000); // Show after 5 seconds
    };

    // Listen for app installed event
    const handleAppInstalled = () => {
      console.log('✅ PWA: App has been installed');
      setIsInstalled(true);
      setIsInstallable(false);
      setShowInstallPrompt(false);
      setDeferredPrompt(null);
      
      // Remove dismissed flag since app is now installed
      localStorage.removeItem('pwa-install-dismissed');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, [isInstalled]);

  const promptInstall = async (): Promise<void> => {
    if (!deferredPrompt) {
      console.warn('PWA: No install prompt available');
      return;
    }

    try {
      // Show the install prompt
      await deferredPrompt.prompt();
      
      // Wait for user choice
      const { outcome } = await deferredPrompt.userChoice;
      
      console.log(`PWA: Install prompt ${outcome}`);
      
      if (outcome === 'accepted') {
        console.log('✅ PWA: User accepted the install prompt');
      } else {
        console.log('❌ PWA: User dismissed the install prompt');
        localStorage.setItem('pwa-install-dismissed', 'true');
      }
      
      // Hide our custom prompt
      setShowInstallPrompt(false);
      setDeferredPrompt(null);
      setIsInstallable(false);
    } catch (error) {
      console.error('PWA: Error during install prompt:', error);
    }
  };

  const dismissPrompt = (): void => {
    console.log('PWA: Custom install prompt dismissed');
    setShowInstallPrompt(false);
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  return {
    isInstallable,
    isInstalled,
    showInstallPrompt,
    promptInstall,
    dismissPrompt
  };
};