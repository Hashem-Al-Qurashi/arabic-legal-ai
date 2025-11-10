import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo, { NetInfoState } from '@react-native-community/netinfo';
import { chatAPI } from './api';
import { generateUUID } from '@/utils/uuid';
import { StorageQuotaManager } from '@/utils/storageQuota';
import { retryWithBackoff } from '@/utils/retry';
import type { QueuedMessage, NetworkStatus, Message, Conversation } from '@/types';

const QUEUE_KEY = 'offline_message_queue';
const CACHE_KEY_PREFIX = 'cached_conversation_';
const MESSAGES_CACHE_KEY_PREFIX = 'cached_messages_';
const NETWORK_STATUS_KEY = 'last_network_status';

export class OfflineService {
  private messageQueue: QueuedMessage[] = [];
  private networkStatus: NetworkStatus = { isConnected: true };
  private syncInProgress = false;
  private syncLock = false; // Prevent race conditions
  private listeners: Set<(status: NetworkStatus) => void> = new Set();
  private unsubscribeNetInfo: (() => void) | null = null;
  private storageManager: StorageQuotaManager;
  private syncRetryTimeout: NodeJS.Timeout | null = null;

  constructor(storageLimit?: number) {
    this.storageManager = new StorageQuotaManager(storageLimit);
    this.initialize();
  }

  /**
   * Initialize offline service
   */
  private async initialize() {
    try {
      // Clean up old data first
      await this.storageManager.cleanupOldItems();

      // Load queue from storage
      await this.loadQueue();

      // Setup network monitoring
      this.unsubscribeNetInfo = NetInfo.addEventListener(this.handleNetworkChange);

      // Get initial network state
      const state = await NetInfo.fetch();
      this.handleNetworkChange(state);
    } catch (error) {
      console.error('Failed to initialize offline service:', error);
    }
  }

  /**
   * Handle network state changes
   */
  private handleNetworkChange = async (state: NetInfoState) => {
    const prevStatus = this.networkStatus;

    this.networkStatus = {
      isConnected: state.isConnected ?? false,
      type: state.type as any,
      isInternetReachable: state.isInternetReachable ?? undefined,
    };

    // Save network status
    await AsyncStorage.setItem(NETWORK_STATUS_KEY, JSON.stringify(this.networkStatus));

    // Notify listeners
    this.listeners.forEach(listener => listener(this.networkStatus));

    // If we just came back online, sync messages with delay to avoid race conditions
    if (!prevStatus.isConnected && this.networkStatus.isConnected) {
      console.log('Network restored, syncing offline messages...');

      // Clear any existing retry timeout
      if (this.syncRetryTimeout) {
        clearTimeout(this.syncRetryTimeout);
      }

      // Delay sync to ensure network is stable
      this.syncRetryTimeout = setTimeout(() => {
        this.syncMessages();
      }, 2000);
    }
  };

  /**
   * Subscribe to network status changes
   */
  subscribeToNetworkStatus(listener: (status: NetworkStatus) => void) {
    this.listeners.add(listener);
    // Immediately call with current status
    listener(this.networkStatus);

    // Return unsubscribe function
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * Get current network status
   */
  getNetworkStatus(): NetworkStatus {
    return this.networkStatus;
  }

  /**
   * Check if currently online
   */
  isOnline(): boolean {
    return this.networkStatus.isConnected && (this.networkStatus.isInternetReachable !== false);
  }

  /**
   * Load queue from AsyncStorage
   */
  private async loadQueue() {
    try {
      const queueData = await AsyncStorage.getItem(QUEUE_KEY);
      if (queueData) {
        this.messageQueue = JSON.parse(queueData);
      }
    } catch (error) {
      console.error('Failed to load offline queue:', error);
      this.messageQueue = [];
    }
  }

  /**
   * Save queue to AsyncStorage with quota check
   */
  private async saveQueue() {
    try {
      const queueData = JSON.stringify(this.messageQueue);
      const sizeInBytes = queueData.length * 2; // UTF-16 encoding

      // Check storage quota
      if (!(await this.storageManager.hasSpace(sizeInBytes))) {
        // Try to free space
        await this.storageManager.freeSpace(sizeInBytes);

        // Check again
        if (!(await this.storageManager.hasSpace(sizeInBytes))) {
          throw new Error('Storage quota exceeded for message queue');
        }
      }

      await this.storageManager.setItem(QUEUE_KEY, queueData, 'high');
    } catch (error) {
      console.error('Failed to save offline queue:', error);

      // If storage is full, remove oldest messages
      if (this.messageQueue.length > 10) {
        this.messageQueue = this.messageQueue.slice(-10); // Keep only last 10 messages
        try {
          await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(this.messageQueue));
        } catch (retryError) {
          console.error('Failed to save reduced queue:', retryError);
        }
      }
    }
  }

  /**
   * Queue a message for sending when online
   */
  async queueMessage(
    content: string,
    conversationId?: string,
    attachments?: any[]
  ): Promise<QueuedMessage> {
    // Check queue size limit
    if (this.messageQueue.length >= 50) {
      throw new Error('Message queue is full. Please wait for messages to sync.');
    }

    const message: QueuedMessage = {
      id: generateUUID(),
      content,
      conversationId,
      attachments,
      timestamp: new Date().toISOString(),
      retryCount: 0,
      maxRetries: 3,
      status: 'pending',
    };

    this.messageQueue.push(message);
    await this.saveQueue();

    // Try to send immediately if online (don't await to prevent blocking)
    if (this.isOnline()) {
      this.syncMessages().catch(err => {
        console.error('Failed to sync message immediately:', err);
      });
    }

    return message;
  }

  /**
   * Sync all queued messages with proper locking and retry logic
   */
  async syncMessages(): Promise<void> {
    // Prevent race conditions with lock
    if (this.syncLock || !this.isOnline() || this.messageQueue.length === 0) {
      return;
    }

    try {
      this.syncLock = true;
      this.syncInProgress = true;

      console.log(`Syncing ${this.messageQueue.length} offline messages...`);

      const pendingMessages = this.messageQueue.filter(m => m.status === 'pending');
      const successfulIds: string[] = [];
      const failedMessages: QueuedMessage[] = [];

      // Process messages with proper error handling
      for (const message of pendingMessages) {
        try {
          // Update status to sending
          message.status = 'sending';
          await this.saveQueue();

          // Send the message with retry logic
          const response = await retryWithBackoff(
            () => chatAPI.sendMessage(
              message.content,
              message.conversationId
            ),
            {
              maxRetries: 2,
              initialDelay: 1000,
              shouldRetry: (error) => {
                // Don't retry on client errors
                if (error?.status >= 400 && error?.status < 500) {
                  return false;
                }
                return true;
              },
            }
          );

          if (response.success) {
            successfulIds.push(message.id);
            console.log(`Successfully synced message ${message.id}`);
          } else {
            throw new Error(response.error || 'Failed to send message');
          }
        } catch (error) {
          console.error(`Failed to sync message ${message.id}:`, error);

          // Update retry count
          message.retryCount++;
          message.status = 'pending';
          message.error = error instanceof Error ? error.message : 'Unknown error';

          // Mark as failed if max retries exceeded
          if (message.retryCount >= message.maxRetries) {
            message.status = 'failed';
            console.error(`Message ${message.id} failed after ${message.maxRetries} retries`);
          } else {
            failedMessages.push(message);
          }
        }
      }

      // Remove successful messages from queue
      if (successfulIds.length > 0) {
        this.messageQueue = this.messageQueue.filter(m => !successfulIds.includes(m.id));
      }

      // Schedule retry for failed messages
      if (failedMessages.length > 0 && this.isOnline()) {
        if (this.syncRetryTimeout) {
          clearTimeout(this.syncRetryTimeout);
        }

        // Exponential backoff for retry
        const retryDelay = Math.min(
          5000 * Math.pow(2, failedMessages[0].retryCount),
          60000 // Max 1 minute
        );

        this.syncRetryTimeout = setTimeout(() => {
          this.syncMessages();
        }, retryDelay);
      }

      await this.saveQueue();
    } catch (error) {
      console.error('Sync messages error:', error);
    } finally {
      this.syncInProgress = false;
      this.syncLock = false;
    }
  }

  /**
   * Get all queued messages
   */
  getQueuedMessages(): QueuedMessage[] {
    return [...this.messageQueue];
  }

  /**
   * Check if sync is in progress
   */
  isSyncing(): boolean {
    return this.syncInProgress;
  }

  /**
   * Remove a message from the queue
   */
  async removeFromQueue(messageId: string): Promise<void> {
    this.messageQueue = this.messageQueue.filter(m => m.id !== messageId);
    await this.saveQueue();
  }

  /**
   * Clear all queued messages
   */
  async clearQueue(): Promise<void> {
    this.messageQueue = [];
    await this.saveQueue();
  }

  /**
   * Cache a conversation for offline access with quota management
   */
  async cacheConversation(conversation: Conversation): Promise<void> {
    try {
      const key = `${CACHE_KEY_PREFIX}${conversation.id}`;
      const data = JSON.stringify({
        conversation,
        cachedAt: new Date().toISOString(),
      });

      await this.storageManager.setItem(key, data, 'medium');
    } catch (error) {
      console.error('Failed to cache conversation:', error);
      // Don't throw - caching is optional
    }
  }

  /**
   * Cache messages for offline access with size limit
   */
  async cacheMessages(conversationId: string, messages: Message[]): Promise<void> {
    try {
      // Limit cached messages to last 100 to prevent storage issues
      const messagesToCache = messages.slice(-100);

      const key = `${MESSAGES_CACHE_KEY_PREFIX}${conversationId}`;
      const data = JSON.stringify({
        messages: messagesToCache,
        cachedAt: new Date().toISOString(),
      });

      await this.storageManager.setItem(key, data, 'medium');
    } catch (error) {
      console.error('Failed to cache messages:', error);
      // Don't throw - caching is optional
    }
  }

  /**
   * Get cached conversation
   */
  async getCachedConversation(conversationId: string): Promise<Conversation | null> {
    try {
      const key = `${CACHE_KEY_PREFIX}${conversationId}`;
      const data = await AsyncStorage.getItem(key);

      if (data) {
        const parsed = JSON.parse(data);
        return parsed.conversation;
      }
    } catch (error) {
      console.error('Failed to get cached conversation:', error);
    }

    return null;
  }

  /**
   * Get cached messages
   */
  async getCachedMessages(conversationId: string): Promise<Message[]> {
    try {
      const key = `${MESSAGES_CACHE_KEY_PREFIX}${conversationId}`;
      const data = await AsyncStorage.getItem(key);

      if (data) {
        const parsed = JSON.parse(data);
        return parsed.messages || [];
      }
    } catch (error) {
      console.error('Failed to get cached messages:', error);
    }

    return [];
  }

  /**
   * Get all cached conversations
   */
  async getAllCachedConversations(): Promise<Conversation[]> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const conversationKeys = keys.filter(k => k.startsWith(CACHE_KEY_PREFIX));

      const conversations: Conversation[] = [];

      for (const key of conversationKeys) {
        const data = await AsyncStorage.getItem(key);
        if (data) {
          const parsed = JSON.parse(data);
          conversations.push(parsed.conversation);
        }
      }

      return conversations.sort((a, b) =>
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      );
    } catch (error) {
      console.error('Failed to get cached conversations:', error);
      return [];
    }
  }

  /**
   * Clear all cached data
   */
  async clearCache(): Promise<void> {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter(k =>
        k.startsWith(CACHE_KEY_PREFIX) || k.startsWith(MESSAGES_CACHE_KEY_PREFIX)
      );

      if (cacheKeys.length > 0) {
        await AsyncStorage.multiRemove(cacheKeys);
      }
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  }

  /**
   * Get storage statistics
   */
  async getStorageStats() {
    return await this.storageManager.getStats();
  }

  /**
   * Cleanup and unsubscribe
   */
  cleanup() {
    // Clear any pending timeouts
    if (this.syncRetryTimeout) {
      clearTimeout(this.syncRetryTimeout);
      this.syncRetryTimeout = null;
    }

    // Unsubscribe from network monitoring
    if (this.unsubscribeNetInfo) {
      this.unsubscribeNetInfo();
      this.unsubscribeNetInfo = null;
    }

    // Clear listeners
    this.listeners.clear();

    // Reset state
    this.syncInProgress = false;
    this.syncLock = false;
  }
}

// Create a factory function instead of singleton
export function createOfflineService(storageLimit?: number): OfflineService {
  return new OfflineService(storageLimit);
}

// Default instance for backward compatibility
export const offlineService = createOfflineService();
