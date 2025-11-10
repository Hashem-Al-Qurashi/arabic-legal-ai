import { useState, useEffect, useCallback, useRef } from 'react';
import { offlineService, OfflineService } from '@/services/offlineService';
import type { NetworkStatus, QueuedMessage } from '@/types';

export function useOffline(customService?: OfflineService) {
  const [isOnline, setIsOnline] = useState(true);
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isConnected: true,
  });
  const [queuedMessages, setQueuedMessages] = useState<QueuedMessage[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);

  // Use provided service or default
  const service = useRef(customService || offlineService);

  // Track if component is mounted to prevent state updates after unmount
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;

    // Subscribe to network status changes
    const unsubscribe = service.current.subscribeToNetworkStatus((status) => {
      if (isMounted.current) {
        setNetworkStatus(status);
        setIsOnline(status.isConnected && status.isInternetReachable !== false);
      }
    });

    // Get initial state
    if (isMounted.current) {
      setIsOnline(service.current.isOnline());
      setNetworkStatus(service.current.getNetworkStatus());
      setQueuedMessages(service.current.getQueuedMessages());
    }

    return () => {
      isMounted.current = false;
      unsubscribe();
    };
  }, []);

  // Queue a message
  const queueMessage = useCallback(async (
    content: string,
    conversationId?: string,
    attachments?: any[]
  ) => {
    const queued = await service.current.queueMessage(content, conversationId, attachments);
    if (isMounted.current) {
      setQueuedMessages(service.current.getQueuedMessages());
    }
    return queued;
  }, []);

  // Sync messages manually
  const syncMessages = useCallback(async () => {
    if (isSyncing || !isOnline) {return;}

    if (isMounted.current) {
      setIsSyncing(true);
    }

    try {
      await service.current.syncMessages();
      if (isMounted.current) {
        setQueuedMessages(service.current.getQueuedMessages());
      }
    } finally {
      if (isMounted.current) {
        setIsSyncing(false);
      }
    }
  }, [isOnline, isSyncing]);

  // Remove message from queue
  const removeFromQueue = useCallback(async (messageId: string) => {
    await service.current.removeFromQueue(messageId);
    if (isMounted.current) {
      setQueuedMessages(service.current.getQueuedMessages());
    }
  }, []);

  // Clear queue
  const clearQueue = useCallback(async () => {
    await service.current.clearQueue();
    if (isMounted.current) {
      setQueuedMessages([]);
    }
  }, []);

  return {
    isOnline,
    networkStatus,
    queuedMessages,
    isSyncing,
    queueMessage,
    syncMessages,
    removeFromQueue,
    clearQueue,
  };
}
