// Message Queue System for Offline Support

interface QueuedMessage {
  id: string;
  conversationId: string;
  content: string;
  timestamp: number;
  token: string;
  retryCount: number;
  status: 'pending' | 'sending' | 'failed' | 'sent';
}

class MessageQueue {
  private dbName = 'hokmMessageQueue';
  private dbVersion = 1;
  private db: IDBDatabase | null = null;

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
        
        if (!db.objectStoreNames.contains('messages')) {
          const store = db.createObjectStore('messages', { keyPath: 'id' });
          store.createIndex('status', 'status', { unique: false });
          store.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  async addMessage(
    conversationId: string,
    content: string,
    token: string
  ): Promise<string> {
    if (!this.db) await this.init();

    const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const queuedMessage: QueuedMessage = {
      id: messageId,
      conversationId,
      content,
      timestamp: Date.now(),
      token,
      retryCount: 0,
      status: 'pending'
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['messages'], 'readwrite');
      const store = transaction.objectStore('messages');
      
      const request = store.add(queuedMessage);
      request.onsuccess = () => {
        console.log('📝 Message queued for offline sending:', messageId);
        resolve(messageId);
      };
      request.onerror = () => reject(request.error);
    });
  }

  async getPendingMessages(): Promise<QueuedMessage[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['messages'], 'readonly');
      const store = transaction.objectStore('messages');
      const index = store.index('status');
      
      const request = index.getAll('pending');
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async updateMessageStatus(
    messageId: string, 
    status: QueuedMessage['status'],
    incrementRetry = false
  ): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['messages'], 'readwrite');
      const store = transaction.objectStore('messages');
      
      const getRequest = store.get(messageId);
      getRequest.onsuccess = () => {
        const message = getRequest.result;
        if (message) {
          message.status = status;
          if (incrementRetry) {
            message.retryCount += 1;
          }
          
          const updateRequest = store.put(message);
          updateRequest.onsuccess = () => resolve();
          updateRequest.onerror = () => reject(updateRequest.error);
        } else {
          reject(new Error('Message not found'));
        }
      };
      getRequest.onerror = () => reject(getRequest.error);
    });
  }

  async removeMessage(messageId: string): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['messages'], 'readwrite');
      const store = transaction.objectStore('messages');
      
      const request = store.delete(messageId);
      request.onsuccess = () => {
        console.log('✅ Message removed from queue:', messageId);
        resolve();
      };
      request.onerror = () => reject(request.error);
    });
  }

  async processQueue(): Promise<void> {
    try {
      const pendingMessages = await this.getPendingMessages();
      console.log(`📤 Processing ${pendingMessages.length} queued messages`);

      for (const message of pendingMessages) {
        try {
          await this.updateMessageStatus(message.id, 'sending');
          
          const response = await fetch('/api/chat/send', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${message.token}`
            },
            body: JSON.stringify({
              conversation_id: message.conversationId,
              message: message.content
            })
          });

          if (response.ok) {
            await this.removeMessage(message.id);
            console.log('✅ Queued message sent successfully:', message.id);
            
            // Dispatch event to update UI
            window.dispatchEvent(new CustomEvent('queued-message-sent', {
              detail: { messageId: message.id, response: await response.json() }
            }));
          } else {
            throw new Error(`HTTP ${response.status}`);
          }
        } catch (error) {
          console.error('❌ Failed to send queued message:', error);
          
          if (message.retryCount < 3) {
            await this.updateMessageStatus(message.id, 'pending', true);
          } else {
            await this.updateMessageStatus(message.id, 'failed');
            
            // Dispatch event for failed message
            window.dispatchEvent(new CustomEvent('queued-message-failed', {
              detail: { messageId: message.id, error }
            }));
          }
        }
      }
    } catch (error) {
      console.error('❌ Error processing message queue:', error);
    }
  }

  async getQueueStatus(): Promise<{ pending: number; failed: number }> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['messages'], 'readonly');
      const store = transaction.objectStore('messages');
      
      const pendingRequest = store.index('status').count('pending');
      const failedRequest = store.index('status').count('failed');
      
      let pending = 0;
      let failed = 0;
      let completed = 0;

      pendingRequest.onsuccess = () => {
        pending = pendingRequest.result;
        completed++;
        if (completed === 2) resolve({ pending, failed });
      };

      failedRequest.onsuccess = () => {
        failed = failedRequest.result;
        completed++;
        if (completed === 2) resolve({ pending, failed });
      };

      pendingRequest.onerror = failedRequest.onerror = () => reject(new Error('Failed to get queue status'));
    });
  }
}

// Export singleton instance
export const messageQueue = new MessageQueue();

// Auto-process queue when connection is restored
window.addEventListener('connection-restored', () => {
  console.log('🔄 Connection restored, processing message queue...');
  messageQueue.processQueue();
});

// Initialize queue on load
messageQueue.init().catch(console.error);