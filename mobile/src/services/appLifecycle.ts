import { AppState, AppStateStatus, NativeEventSubscription } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { offlineService } from './offlineService';
import { storageQuota } from '@/utils/storageQuota';

const APP_STATE_KEY = 'app_last_state';
const LAST_ACTIVE_KEY = 'app_last_active_time';
const SESSION_KEY = 'app_session_data';

export interface AppSession {
  startTime: string;
  lastActiveTime: string;
  backgroundTime?: string;
  foregroundCount: number;
}

export class AppLifecycleService {
  private currentState: AppStateStatus = 'active';
  private listeners: Set<(state: AppStateStatus) => void> = new Set();
  private session: AppSession;
  private backgroundTimer?: ReturnType<typeof setTimeout>; // Fix Timer type for React Native
  private appStateSubscription?: NativeEventSubscription; // Proper type for subscription

  constructor() {
    this.session = {
      startTime: new Date().toISOString(),
      lastActiveTime: new Date().toISOString(),
      foregroundCount: 0,
    };
    this.initialize();
  }

  /**
   * Initialize lifecycle monitoring
   */
  private async initialize() {
    try {
      // Load previous session if exists
      await this.loadSession();

      // Subscribe to app state changes
      this.appStateSubscription = AppState.addEventListener(
        'change',
        this.handleAppStateChange
      );

      // Get initial state
      this.currentState = AppState.currentState || 'active';

      // Save initial state
      await this.saveAppState(this.currentState);
    } catch (error) {
      console.error('Failed to initialize app lifecycle:', error);
    }
  }

  /**
   * Handle app state changes
   */
  private handleAppStateChange = async (nextAppState: AppStateStatus) => {
    const prevState = this.currentState;

    console.log(`App state change: ${prevState} → ${nextAppState}`);

    // Handle transitions
    if (prevState === 'active' && nextAppState.match(/inactive|background/)) {
      // App is going to background
      await this.handleAppBackground();
    } else if (prevState.match(/inactive|background/) && nextAppState === 'active') {
      // App is coming to foreground
      await this.handleAppForeground();
    }

    this.currentState = nextAppState;

    // Notify listeners
    this.listeners.forEach(listener => listener(nextAppState));

    // Save state
    await this.saveAppState(nextAppState);
  };

  /**
   * Handle app going to background
   */
  private async handleAppBackground() {
    console.log('App entering background');

    // Update session
    this.session.backgroundTime = new Date().toISOString();
    await this.saveSession();

    // Save current timestamp
    await AsyncStorage.setItem(LAST_ACTIVE_KEY, new Date().toISOString());

    // Sync offline messages before going to background
    await offlineService.syncMessages();

    // Set a timer to clear sensitive data if app stays in background too long
    // Use proper setTimeout for React Native
    this.backgroundTimer = setTimeout(() => {
      // Don't use async in setTimeout to avoid memory leaks
      this.clearSensitiveData().catch(error => {
        console.error('Failed to clear sensitive data:', error);
      });
    }, 5 * 60 * 1000); // 5 minutes
  }

  /**
   * Handle app coming to foreground
   */
  private async handleAppForeground() {
    console.log('App entering foreground');

    // Clear background timer
    if (this.backgroundTimer) {
      clearTimeout(this.backgroundTimer);
      this.backgroundTimer = undefined;
    }

    // Update session
    this.session.lastActiveTime = new Date().toISOString();
    this.session.foregroundCount++;
    delete this.session.backgroundTime;
    await this.saveSession();

    // Check how long app was in background
    const lastActiveStr = await AsyncStorage.getItem(LAST_ACTIVE_KEY);
    if (lastActiveStr) {
      const lastActive = new Date(lastActiveStr);
      const now = new Date();
      const timeDiff = now.getTime() - lastActive.getTime();
      const minutesInBackground = Math.floor(timeDiff / 60000);

      console.log(`App was in background for ${minutesInBackground} minutes`);

      // If app was in background for more than 30 minutes, refresh data
      if (minutesInBackground > 30) {
        await this.refreshAppData();
      }
    }

    // Sync any offline messages
    await offlineService.syncMessages();
  }

  /**
   * Save app state to storage
   */
  private async saveAppState(state: AppStateStatus) {
    try {
      await AsyncStorage.setItem(APP_STATE_KEY, state);
    } catch (error) {
      console.error('Failed to save app state:', error);
    }
  }

  /**
   * Save session data
   */
  private async saveSession() {
    try {
      await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(this.session));
    } catch (error) {
      console.error('Failed to save session:', error);
    }
  }

  /**
   * Load session data
   */
  private async loadSession() {
    try {
      const sessionStr = await AsyncStorage.getItem(SESSION_KEY);
      if (sessionStr) {
        this.session = JSON.parse(sessionStr);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  }

  /**
   * Clear sensitive data (called when app is in background too long)
   */
  private async clearSensitiveData() {
    try {
      console.log('App in background for extended period, clearing sensitive data');

      // Clear any sensitive cached data
      const keysToKeep = [
        APP_STATE_KEY,
        LAST_ACTIVE_KEY,
        SESSION_KEY,
        'guestSessionId',
        'offline_message_queue',
        '__metadata_', // Keep storage metadata
      ];

      const allKeys = await AsyncStorage.getAllKeys();
      const keysToRemove = allKeys.filter(key => {
        // Keep important keys and metadata
        return !keysToKeep.some(keepKey => key.includes(keepKey));
      });

      if (keysToRemove.length > 0) {
        // Remove in batches to avoid memory issues
        const batchSize = 10;
        for (let i = 0; i < keysToRemove.length; i += batchSize) {
          const batch = keysToRemove.slice(i, i + batchSize);
          await AsyncStorage.multiRemove(batch);
        }
        console.log(`Cleared ${keysToRemove.length} sensitive data items`);
      }
    } catch (error) {
      console.error('Failed to clear sensitive data:', error);
    }
  }

  /**
   * Refresh app data after being in background
   */
  private async refreshAppData() {
    console.log('Refreshing app data after extended background period');

    // This would typically:
    // - Re-authenticate if needed
    // - Refresh conversations
    // - Check for new messages
    // - Update user profile

    // For now, just sync offline messages
    await offlineService.syncMessages();
  }

  /**
   * Subscribe to app state changes
   */
  subscribe(listener: (state: AppStateStatus) => void) {
    this.listeners.add(listener);

    // Immediately call with current state
    listener(this.currentState);

    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * Get current app state
   */
  getCurrentState(): AppStateStatus {
    return this.currentState;
  }

  /**
   * Get session information
   */
  getSession(): AppSession {
    return { ...this.session };
  }

  /**
   * Check if app is active
   */
  isActive(): boolean {
    return this.currentState === 'active';
  }

  /**
   * Check if app is in background
   */
  isBackground(): boolean {
    return this.currentState === 'background';
  }

  /**
   * Manually trigger background tasks
   */
  async performBackgroundTasks() {
    console.log('Performing background tasks');

    try {
      // Sync offline messages with timeout
      const syncPromise = offlineService.syncMessages();
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Sync timeout')), 30000)
      );

      await Promise.race([syncPromise, timeoutPromise]).catch(error => {
        console.error('Background sync failed:', error);
      });

      // Use storage quota manager for cleanup
      await storageQuota.cleanupOldItems(7 * 24 * 60 * 60 * 1000); // 7 days

      // Get storage stats
      const stats = await storageQuota.getStats();
      console.log('Storage stats:', stats);

      if (stats.quota.percentage > 80) {
        console.warn('Storage usage is high:', stats.quota.percentage + '%');
      }
    } catch (error) {
      console.error('Background tasks error:', error);
    }
  }

  /**
   * Cleanup and unsubscribe
   */
  cleanup() {
    // Remove app state subscription
    if (this.appStateSubscription) {
      this.appStateSubscription.remove();
      this.appStateSubscription = undefined;
    }

    // Clear background timer
    if (this.backgroundTimer) {
      clearTimeout(this.backgroundTimer);
      this.backgroundTimer = undefined;
    }

    // Clear all listeners
    this.listeners.clear();

    // Save final session state
    this.saveSession().catch(error => {
      console.error('Failed to save final session:', error);
    });
  }
}

// Create factory function instead of singleton
export function createAppLifecycleService(): AppLifecycleService {
  return new AppLifecycleService();
}

// Default instance for backward compatibility
export const appLifecycle = createAppLifecycleService();
