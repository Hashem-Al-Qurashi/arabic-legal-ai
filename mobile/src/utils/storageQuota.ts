/**
 * Storage quota management utility
 * Manages AsyncStorage usage and prevents quota exceeded errors
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

export interface StorageQuota {
  used: number;
  limit: number;
  available: number;
  percentage: number;
}

export interface StorageItem {
  key: string;
  size: number;
  timestamp: number;
  priority: 'low' | 'medium' | 'high';
}

/**
 * Storage quota manager
 */
export class StorageQuotaManager {
  private static readonly DEFAULT_QUOTA = 50 * 1024 * 1024; // 50MB default
  private static readonly MIN_FREE_SPACE = 5 * 1024 * 1024; // Keep 5MB free
  private static readonly QUOTA_CHECK_INTERVAL = 60000; // Check every minute

  private quotaLimit: number;
  private lastQuotaCheck: number = 0;
  private cachedQuota: StorageQuota | null = null;

  constructor(quotaLimit: number = StorageQuotaManager.DEFAULT_QUOTA) {
    this.quotaLimit = quotaLimit;
  }

  /**
   * Get current storage quota usage
   */
  async getQuota(): Promise<StorageQuota> {
    const now = Date.now();

    // Return cached quota if recent
    if (this.cachedQuota && now - this.lastQuotaCheck < StorageQuotaManager.QUOTA_CHECK_INTERVAL) {
      return this.cachedQuota;
    }

    try {
      const keys = await AsyncStorage.getAllKeys();
      let totalSize = 0;

      // Calculate total size of all stored items
      for (const key of keys) {
        const value = await AsyncStorage.getItem(key);
        if (value) {
          // Approximate size in bytes (UTF-16 encoding)
          totalSize += key.length * 2 + value.length * 2;
        }
      }

      const quota: StorageQuota = {
        used: totalSize,
        limit: this.quotaLimit,
        available: Math.max(0, this.quotaLimit - totalSize),
        percentage: (totalSize / this.quotaLimit) * 100,
      };

      this.cachedQuota = quota;
      this.lastQuotaCheck = now;

      return quota;
    } catch (error) {
      console.error('Failed to get storage quota:', error);

      // Return a safe default
      return {
        used: 0,
        limit: this.quotaLimit,
        available: this.quotaLimit,
        percentage: 0,
      };
    }
  }

  /**
   * Check if there's enough space for new data
   */
  async hasSpace(sizeInBytes: number): Promise<boolean> {
    const quota = await this.getQuota();
    return quota.available >= sizeInBytes + StorageQuotaManager.MIN_FREE_SPACE;
  }

  /**
   * Store data with quota check
   */
  async setItem(key: string, value: string, priority: 'low' | 'medium' | 'high' = 'medium'): Promise<void> {
    const sizeInBytes = (key.length + value.length) * 2;

    // Check if we have space
    if (!(await this.hasSpace(sizeInBytes))) {
      // Try to free up space
      await this.freeSpace(sizeInBytes);

      // Check again
      if (!(await this.hasSpace(sizeInBytes))) {
        throw new Error('Storage quota exceeded');
      }
    }

    // Store the item
    await AsyncStorage.setItem(key, value);

    // Store metadata
    const metadata: StorageItem = {
      key,
      size: sizeInBytes,
      timestamp: Date.now(),
      priority,
    };

    await this.saveMetadata(key, metadata);
  }

  /**
   * Free up storage space by removing old/low-priority items
   */
  async freeSpace(requiredBytes: number): Promise<void> {
    try {
      const items = await this.getAllItems();

      // Sort by priority and timestamp (low priority and old items first)
      items.sort((a, b) => {
        if (a.priority !== b.priority) {
          const priorityOrder = { low: 0, medium: 1, high: 2 };
          return priorityOrder[a.priority] - priorityOrder[b.priority];
        }
        return a.timestamp - b.timestamp;
      });

      let freedBytes = 0;
      const keysToRemove: string[] = [];

      // Remove items until we have enough space
      for (const item of items) {
        // Skip high-priority recent items
        if (item.priority === 'high' && Date.now() - item.timestamp < 86400000) {
          continue;
        }

        keysToRemove.push(item.key);
        freedBytes += item.size;

        if (freedBytes >= requiredBytes) {
          break;
        }
      }

      // Remove selected items
      if (keysToRemove.length > 0) {
        await AsyncStorage.multiRemove(keysToRemove);

        // Remove metadata
        const metadataKeys = keysToRemove.map(k => `__metadata_${k}`);
        await AsyncStorage.multiRemove(metadataKeys);

        console.log(`Freed ${freedBytes} bytes by removing ${keysToRemove.length} items`);
      }
    } catch (error) {
      console.error('Failed to free storage space:', error);
    }
  }

  /**
   * Get all stored items with metadata
   */
  private async getAllItems(): Promise<StorageItem[]> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const metadataKeys = keys.filter(k => k.startsWith('__metadata_'));

      const items: StorageItem[] = [];

      for (const metaKey of metadataKeys) {
        const metadata = await AsyncStorage.getItem(metaKey);
        if (metadata) {
          try {
            const item = JSON.parse(metadata) as StorageItem;
            items.push(item);
          } catch {
            // Invalid metadata, skip
          }
        }
      }

      return items;
    } catch (error) {
      console.error('Failed to get all items:', error);
      return [];
    }
  }

  /**
   * Save item metadata
   */
  private async saveMetadata(key: string, metadata: StorageItem): Promise<void> {
    const metaKey = `__metadata_${key}`;
    await AsyncStorage.setItem(metaKey, JSON.stringify(metadata));
  }

  /**
   * Clean up old items based on age
   */
  async cleanupOldItems(maxAgeMs: number = 7 * 24 * 60 * 60 * 1000): Promise<void> {
    try {
      const items = await this.getAllItems();
      const now = Date.now();
      const keysToRemove: string[] = [];

      for (const item of items) {
        if (now - item.timestamp > maxAgeMs && item.priority !== 'high') {
          keysToRemove.push(item.key);
        }
      }

      if (keysToRemove.length > 0) {
        await AsyncStorage.multiRemove(keysToRemove);

        // Remove metadata
        const metadataKeys = keysToRemove.map(k => `__metadata_${k}`);
        await AsyncStorage.multiRemove(metadataKeys);

        console.log(`Cleaned up ${keysToRemove.length} old items`);
      }
    } catch (error) {
      console.error('Failed to cleanup old items:', error);
    }
  }

  /**
   * Get storage statistics
   */
  async getStats(): Promise<{
    quota: StorageQuota;
    itemCount: number;
    oldestItem: number | null;
    largestItem: { key: string; size: number } | null;
  }> {
    const quota = await this.getQuota();
    const items = await this.getAllItems();

    let oldestTimestamp: number | null = null;
    let largestItem: { key: string; size: number } | null = null;

    for (const item of items) {
      if (!oldestTimestamp || item.timestamp < oldestTimestamp) {
        oldestTimestamp = item.timestamp;
      }

      if (!largestItem || item.size > largestItem.size) {
        largestItem = { key: item.key, size: item.size };
      }
    }

    return {
      quota,
      itemCount: items.length,
      oldestItem: oldestTimestamp,
      largestItem,
    };
  }

  /**
   * Clear all storage (use with caution)
   */
  async clearAll(): Promise<void> {
    try {
      await AsyncStorage.clear();
      this.cachedQuota = null;
      console.log('All storage cleared');
    } catch (error) {
      console.error('Failed to clear storage:', error);
      throw error;
    }
  }
}

// Create a singleton instance for app-wide use
export const storageQuota = new StorageQuotaManager();
