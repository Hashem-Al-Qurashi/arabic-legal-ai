// =====================================================================
// 🧭 CONVERSATION ROUTING HOOK - EXTRACTED FROM 4550-LINE APP.TSX
// =====================================================================

import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { ConversationRouteParams, UseConversationRoutingReturn } from '../types';
import { isValidConversationIdFormat, sanitizeConversationId } from '../utils/security';

/**
 * Senior-level custom hook for managing conversation URL routing
 * Handles bidirectional URL ↔ State synchronization with error boundaries
 * 
 * @param selectedConversation - Currently selected conversation ID
 * @param conversations - Array of available conversations
 * @param loadConversationMessages - Function to load messages for a conversation
 * @param user - Current user object
 * @param loadingConversations - Whether conversations are currently loading
 * @param loadConversations - Function to load conversations
 * @returns Hook interface with navigation methods
 */
export const useConversationRouting = (
  selectedConversation: string | null,
  conversations: any[],
  loadConversationMessages: (conversationId: string) => Promise<void>,
  user: any,
  loadingConversations: boolean,
  loadConversations: () => Promise<void>
): UseConversationRoutingReturn => {
  const { conversationId } = useParams<ConversationRouteParams>();
  const navigate = useNavigate();

  // Comprehensive conversation ID validation
  const isValidConversationId = (conversationId: string): boolean => {
    // First check format and security
    if (!isValidConversationIdFormat(conversationId)) return false;
    
    // Then check if it exists in user's conversations
    const sanitized = sanitizeConversationId(conversationId);
    return conversations.some(conv => conv.id === sanitized);
  };

  // Senior-level navigation methods with parameter validation and error handling
  const navigateToConversation = (conversationId: string) => {
    try {
      if (!conversationId) {
        console.warn('🚨 Empty conversation ID provided');
        navigate('/');
        return;
      }
      
      // Validate format first for security
      if (!isValidConversationIdFormat(conversationId)) {
        console.warn('🚨 Invalid conversation ID format:', conversationId);
        navigate('/', { replace: true });
        return;
      }
      
      const sanitizedId = sanitizeConversationId(conversationId);
      
      if (isValidConversationId(sanitizedId)) {
        console.log('🎯 Navigating to conversation:', sanitizedId);
        navigate(`/c/${sanitizedId}`);
      } else {
        console.warn('🚨 Conversation not found:', sanitizedId);
        navigate('/', { replace: true });
      }
    } catch (error) {
      console.error('🚨 Navigation error:', error);
      navigate('/', { replace: true });
    }
  };

  const navigateToHome = () => {
    try {
      console.log('🏠 Navigating to home');
      navigate('/');
    } catch (error) {
      console.error('🚨 Home navigation error:', error);
      window.location.href = '/'; // Fallback
    }
  };

  // URL → State synchronization with race condition protection
  useEffect(() => {
    if (!conversationId) return;
    
    try {
      // Validate conversation ID format first for security
      if (!isValidConversationIdFormat(conversationId)) {
        console.warn('🚨 Invalid conversation ID format in URL:', conversationId);
        navigate('/', { replace: true });
        return;
      }
      
      const sanitizedId = sanitizeConversationId(conversationId);
      
      if (sanitizedId !== selectedConversation) {
        // 🔧 FIX RACE CONDITION: Check if we have user AND if conversations are loading
        if (!user) {
          console.log('⏳ Waiting for user authentication...');
          return;
        }
        
        if (conversations.length === 0 && !loadingConversations) {
          // Conversations not loaded and not loading - trigger load
          console.log('🔄 Triggering conversation load for URL navigation');
          loadConversations();
          return;
        }
        
        if (conversations.length === 0 && loadingConversations) {
          // Still loading conversations - wait
          console.log('⏳ Waiting for conversations to load...');
          return;
        }
        
        // Conversations are loaded - validate and navigate
        if (isValidConversationId(sanitizedId)) {
          console.log('🔄 Loading conversation from URL:', sanitizedId);
          loadConversationMessages(sanitizedId).catch((error) => {
            console.error('🚨 Failed to load conversation:', error);
            navigate('/', { replace: true });
          });
        } else {
          console.warn('🚨 Conversation not found in URL, redirecting to home');
          navigate('/', { replace: true });
        }
      }
    } catch (error) {
      console.error('🚨 URL synchronization error:', error);
      navigate('/', { replace: true });
    }
  }, [conversationId, conversations, selectedConversation, user, loadingConversations, loadConversations, loadConversationMessages, navigate]);

  return {
    conversationId: conversationId || null,
    navigateToConversation,
    navigateToHome,
    isValidConversationId
  };
};