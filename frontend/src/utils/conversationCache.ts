// Conversation History Caching System

import type { Message, Conversation } from '../types';

interface CachedConversation extends Conversation {
  cached_at: number;
  last_accessed: number;
}

interface CachedMessage extends Message {
  conversation_id: string;
  cached_at: number;
}

class ConversationCache {
  private dbName = 'hokmConversationCache';
  private dbVersion = 1;
  private db: IDBDatabase | null = null;
  private readonly CACHE_DURATION = 7 * 24 * 60 * 60 * 1000; // 7 days
  private readonly MAX_CONVERSATIONS = 50; // Limit cache size

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // Conversations store
        if (!db.objectStoreNames.contains('conversations')) {
          const conversationStore = db.createObjectStore('conversations', { keyPath: 'id' });
          conversationStore.createIndex('last_accessed', 'last_accessed', { unique: false });
          conversationStore.createIndex('cached_at', 'cached_at', { unique: false });
        }

        // Messages store
        if (!db.objectStoreNames.contains('messages')) {
          const messageStore = db.createObjectStore('messages', { keyPath: 'id' });
          messageStore.createIndex('conversation_id', 'conversation_id', { unique: false });
          messageStore.createIndex('cached_at', 'cached_at', { unique: false });
        }
      };
    });
  }

  // Cache conversations
  async cacheConversations(conversations: Conversation[]): Promise<void> {
    if (!this.db) await this.init();

    const transaction = this.db!.transaction(['conversations'], 'readwrite');
    const store = transaction.objectStore('conversations');
    const now = Date.now();

    for (const conversation of conversations) {
      const cachedConversation: CachedConversation = {
        ...conversation,
        cached_at: now,
        last_accessed: now
      };

      try {
        await new Promise<void>((resolve, reject) => {
          const request = store.put(cachedConversation);
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        });
      } catch (error) {
        console.error('Failed to cache conversation:', conversation.id, error);
      }
    }

    console.log(`📦 Cached ${conversations.length} conversations`);
    await this.cleanupOldConversations();
  }

  // Get cached conversations
  async getCachedConversations(): Promise<Conversation[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['conversations'], 'readwrite');
      const store = transaction.objectStore('conversations');
      const index = store.index('last_accessed');
      
      // Get all conversations ordered by last accessed (most recent first)
      const request = index.openCursor(null, 'prev');
      const conversations: Conversation[] = [];

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        if (cursor) {
          const cachedConversation = cursor.value as CachedConversation;
          
          // Check if not expired
          if (Date.now() - cachedConversation.cached_at < this.CACHE_DURATION) {
            // Update last accessed time
            cachedConversation.last_accessed = Date.now();
            cursor.update(cachedConversation);
            
            // Remove cache metadata before returning
            const { cached_at, last_accessed, ...conversation } = cachedConversation;
            conversations.push(conversation);
          } else {
            // Delete expired conversation
            cursor.delete();
          }
          
          cursor.continue();
        } else {
          resolve(conversations);
        }
      };

      request.onerror = () => reject(request.error);
    });
  }

  // Cache messages for a conversation
  async cacheMessages(conversationId: string, messages: Message[]): Promise<void> {
    if (!this.db) await this.init();

    const transaction = this.db!.transaction(['messages'], 'readwrite');
    const store = transaction.objectStore('messages');
    const now = Date.now();

    // First, delete existing messages for this conversation
    await this.clearConversationMessages(conversationId);

    for (const message of messages) {
      const cachedMessage: CachedMessage = {
        ...message,
        conversation_id: conversationId,
        cached_at: now
      };

      try {
        await new Promise<void>((resolve, reject) => {
          const request = store.add(cachedMessage);
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        });
      } catch (error) {
        console.error('Failed to cache message:', message.id, error);
      }
    }

    console.log(`📦 Cached ${messages.length} messages for conversation ${conversationId}`);
  }

  // Get cached messages for a conversation
  async getCachedMessages(conversationId: string): Promise<Message[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['messages'], 'readonly');
      const store = transaction.objectStore('messages');
      const index = store.index('conversation_id');
      
      const request = index.getAll(conversationId);
      request.onsuccess = () => {
        const cachedMessages = request.result as CachedMessage[];
        
        // Filter out expired messages and remove cache metadata
        const messages: Message[] = cachedMessages
          .filter(msg => Date.now() - msg.cached_at < this.CACHE_DURATION)
          .map(({ conversation_id, cached_at, ...message }) => message)
          .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

        resolve(messages);
      };
      request.onerror = () => reject(request.error);
    });
  }

  // Clear messages for a specific conversation
  private async clearConversationMessages(conversationId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['messages'], 'readwrite');
      const store = transaction.objectStore('messages');
      const index = store.index('conversation_id');
      
      const request = index.openCursor(IDBKeyRange.only(conversationId));
      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        if (cursor) {
          cursor.delete();
          cursor.continue();
        } else {
          resolve();
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  // Cleanup old conversations (keep only most recent ones)
  private async cleanupOldConversations(): Promise<void> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['conversations'], 'readwrite');
      const store = transaction.objectStore('conversations');
      const index = store.index('last_accessed');
      
      const request = index.openCursor(null, 'prev');
      let count = 0;

      request.onsuccess = (event) => {
        const cursor = (event.target as IDBRequest).result;
        if (cursor) {
          count++;
          if (count > this.MAX_CONVERSATIONS) {
            // Delete old conversations
            cursor.delete();
          }
          cursor.continue();
        } else {
          resolve();
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  // Get cache statistics
  async getCacheStats(): Promise<{ conversations: number; messages: number; size: string }> {
    if (!this.db) await this.init();

    const conversationCount = await this.getStoreCount('conversations');
    const messageCount = await this.getStoreCount('messages');

    // Estimate cache size (rough calculation)
    const estimatedSize = ((conversationCount * 1000) + (messageCount * 500)) / 1024; // KB

    return {
      conversations: conversationCount,
      messages: messageCount,
      size: estimatedSize > 1024 ? `${(estimatedSize / 1024).toFixed(1)} MB` : `${estimatedSize.toFixed(1)} KB`
    };
  }

  private async getStoreCount(storeName: string): Promise<number> {
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      
      const request = store.count();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  // Clear all cache
  async clearCache(): Promise<void> {
    if (!this.db) await this.init();

    const transaction = this.db!.transaction(['conversations', 'messages'], 'readwrite');
    
    await Promise.all([
      new Promise<void>((resolve, reject) => {
        const request = transaction.objectStore('conversations').clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      }),
      new Promise<void>((resolve, reject) => {
        const request = transaction.objectStore('messages').clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      })
    ]);

    console.log('🗑️ Conversation cache cleared');
  }
}

// Export singleton instance
export const conversationCache = new ConversationCache();

// Initialize cache on load
conversationCache.init().catch(console.error);