/**
 * MSW Server for API Mocking
 *
 * This provides REAL API mocking that allows testing:
 * - HTTP requests and responses
 * - Loading states
 * - Error conditions
 * - Data transformations
 * - Network delays
 */

import { setupServer } from 'msw/node';
import { http, HttpResponse, delay } from 'msw';

// Types for our API responses
interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
}

interface User {
  id: string;
  name: string;
  full_name: string;
  email: string;
  avatar?: string;
  subscription_tier: string;
  is_active: boolean;
  is_verified: boolean;
  questions_used_current_cycle: number;
  cycle_reset_time: string | null;
}

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: string;
  conversationId: string;
}

interface Conversation {
  id: string;
  title: string;
  lastMessage?: string;
  lastMessageAt: string;
  messages: Message[];
}

// Mock data
const mockUsers: Record<string, User & { password: string; full_name: string; subscription_tier: string; is_active: boolean; is_verified: boolean; questions_used_current_cycle: number; cycle_reset_time: string | null }> = {
  'test@example.com': {
    id: '1',
    name: 'Test User',
    full_name: 'Test User',
    email: 'test@example.com',
    password: 'password123',
    avatar: 'https://example.com/avatar.jpg',
    subscription_tier: 'free',
    is_active: true,
    is_verified: true,
    questions_used_current_cycle: 5,
    cycle_reset_time: null,
  },
};

const mockConversations: Record<string, Conversation> = {
  '1': {
    id: '1',
    title: 'Legal Question about Contracts',
    lastMessage: 'Thank you for the detailed explanation.',
    lastMessageAt: '2024-01-15T10:30:00Z',
    messages: [
      {
        id: '1',
        content: 'I have a question about contract law.',
        isUser: true,
        timestamp: '2024-01-15T10:00:00Z',
        conversationId: '1',
      },
      {
        id: '2',
        content: 'I\'d be happy to help you with contract law. What specific aspect would you like to discuss?',
        isUser: false,
        timestamp: '2024-01-15T10:01:00Z',
        conversationId: '1',
      },
    ],
  },
};

// Current session state
let currentUser: User | null = null;
let sessionToken: string | null = null;

// Request handlers
export const handlers = [
  // Authentication endpoints - match all possible base URLs with wildcard patterns
  http.post('*/api/auth/login', async ({ request }) => {
    console.log('MSW: Login request intercepted!', request.url);
    await delay(300); // Simulate network delay

    const { email, password } = await request.json() as LoginRequest;
    console.log('MSW: Login attempt', { email, password });

    const user = mockUsers[email];
    if (!user || user.password !== password) {
      return HttpResponse.json(
        { message: 'Invalid credentials' },
        { status: 401 }
      );
    }

    // Set current session state
    currentUser = {
      id: user.id,
      name: user.name,
      email: user.email,
      avatar: user.avatar,
      full_name: user.full_name,
      subscription_tier: user.subscription_tier,
      is_active: user.is_active,
      is_verified: user.is_verified,
      questions_used_current_cycle: user.questions_used_current_cycle,
      cycle_reset_time: user.cycle_reset_time,
    };
    sessionToken = `token_${user.id}_${Date.now()}`;

    // Match the exact API response format that api.ts expects
    return HttpResponse.json({
      access_token: sessionToken,
      refresh_token: `refresh_${sessionToken}`,
      expires_in: 3600,
      token_type: 'Bearer',
      // Include user data directly in response (not nested in data)
      id: currentUser.id,
      full_name: currentUser.full_name,
      email: currentUser.email,
      avatar: currentUser.avatar,
      subscription_tier: currentUser.subscription_tier,
      is_active: currentUser.is_active,
      is_verified: currentUser.is_verified,
      questions_used_current_cycle: currentUser.questions_used_current_cycle,
      cycle_reset_time: currentUser.cycle_reset_time,
    });
  }),

  http.post('*/api/auth/register', async ({ request }) => {
    await delay(500); // Simulate network delay

    const { full_name, email, password } = await request.json() as RegisterRequest;

    if (mockUsers[email]) {
      return HttpResponse.json(
        { message: 'Email already exists' },
        { status: 409 }
      );
    }

    const newUser = {
      id: String(Object.keys(mockUsers).length + 1),
      name: full_name,
      full_name,
      email,
      password,
      avatar: undefined,
      subscription_tier: 'free',
      is_active: true,
      is_verified: false,
      questions_used_current_cycle: 0,
      cycle_reset_time: null,
    };

    mockUsers[email] = newUser;
    currentUser = {
      id: newUser.id,
      name: newUser.name,
      full_name: newUser.full_name,
      email: newUser.email,
      subscription_tier: newUser.subscription_tier,
      is_active: newUser.is_active,
      is_verified: newUser.is_verified,
      questions_used_current_cycle: newUser.questions_used_current_cycle,
      cycle_reset_time: newUser.cycle_reset_time,
    };
    sessionToken = `token_${newUser.id}_${Date.now()}`;

    // Return just the user data for registration
    return HttpResponse.json({
      id: currentUser.id,
      full_name: currentUser.full_name,
      email: currentUser.email,
      subscription_tier: currentUser.subscription_tier,
      is_active: currentUser.is_active,
      is_verified: currentUser.is_verified,
      questions_used_current_cycle: currentUser.questions_used_current_cycle,
      cycle_reset_time: currentUser.cycle_reset_time,
    });
  }),

  http.post('*/api/auth/logout', async () => {
    await delay(200);

    currentUser = null;
    sessionToken = null;

    return HttpResponse.json({ success: true });
  }),

  // getCurrentUser endpoint (uses /api/chat/status)
  http.get('*/api/chat/status', async ({ request }) => {
    await delay(200);

    const authorization = request.headers.get('Authorization');
    if (!authorization || authorization !== `Bearer ${sessionToken}`) {
      return HttpResponse.json(
        { message: 'Unauthorized' },
        { status: 401 }
      );
    }

    if (!currentUser) {
      return HttpResponse.json(
        { message: 'User not found' },
        { status: 404 }
      );
    }

    // Return user data in the format expected by getCurrentUser
    return HttpResponse.json({
      user_id: currentUser.id,
      id: currentUser.id,
      email: currentUser.email,
      full_name: currentUser.full_name,
      is_active: currentUser.is_active,
      subscription_tier: currentUser.subscription_tier,
      questions_used_current_cycle: currentUser.questions_used_current_cycle,
      cycle_reset_time: currentUser.cycle_reset_time,
      is_verified: currentUser.is_verified,
    });
  }),

  // Chat endpoints
  http.get('*/api/chat/conversations', async ({ request }) => {
    await delay(300);

    const authorization = request.headers.get('Authorization');
    if (!authorization || authorization !== `Bearer ${sessionToken}`) {
      return HttpResponse.json(
        { message: 'Unauthorized' },
        { status: 401 }
      );
    }

    const conversations = Object.values(mockConversations).map(conv => ({
      id: conv.id,
      title: conv.title,
      created_at: conv.lastMessageAt,
      updated_at: conv.lastMessageAt,
      last_message_preview: conv.lastMessage,
      message_count: conv.messages.length,
    }));

    return HttpResponse.json(conversations);
  }),

  http.get('*/api/chat/conversations/:id/messages', async ({ request, params }) => {
    await delay(200);

    const authorization = request.headers.get('Authorization');
    if (!authorization || authorization !== `Bearer ${sessionToken}`) {
      return HttpResponse.json(
        { message: 'Unauthorized' },
        { status: 401 }
      );
    }

    const conversationId = params.id as string;
    const conversation = mockConversations[conversationId];

    if (!conversation) {
      return HttpResponse.json(
        { message: 'Conversation not found' },
        { status: 404 }
      );
    }

    // Transform messages to match expected format
    const messages = conversation.messages.map(msg => ({
      id: msg.id,
      role: msg.isUser ? 'user' : 'assistant',
      content: msg.content,
      timestamp: msg.timestamp,
    }));

    return HttpResponse.json(messages);
  }),

  http.post('*/api/chat/message', async ({ request }) => {
    await delay(600); // Simulate AI response time

    const authorization = request.headers.get('Authorization');
    if (!authorization || authorization !== `Bearer ${sessionToken}`) {
      return HttpResponse.json(
        { message: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Handle FormData - React Native FormData doesn't have .get() method
    const formData = await request.formData();
    // Use type assertion to access FormData methods in test environment
    const message = (formData as any).get('message') as string;
    const conversationId = (formData as any).get('conversation_id') as string | null;

    if (!message) {
      return HttpResponse.json(
        { message: 'Message is required' },
        { status: 400 }
      );
    }

    // Create new conversation if none exists
    let targetConversationId = conversationId;
    if (!targetConversationId) {
      targetConversationId = String(Object.keys(mockConversations).length + 1);
      mockConversations[targetConversationId] = {
        id: targetConversationId,
        title: message.substring(0, 50) + '...',
        lastMessage: '',
        lastMessageAt: new Date().toISOString(),
        messages: [],
      };
    }

    const conversation = mockConversations[targetConversationId];
    if (!conversation) {
      return HttpResponse.json(
        { message: 'Conversation not found' },
        { status: 404 }
      );
    }

    // Generate AI response
    const aiResponse = `I understand your question about: "${message}". This is a mock AI response for testing purposes. In the real application, this would be generated by an AI legal assistant.`;

    // Add both user message and AI response
    const userMessage: Message = {
      id: String(Date.now()),
      content: message,
      isUser: true,
      timestamp: new Date().toISOString(),
      conversationId: targetConversationId,
    };

    const assistantMessage: Message = {
      id: String(Date.now() + 1),
      content: aiResponse,
      isUser: false,
      timestamp: new Date().toISOString(),
      conversationId: targetConversationId,
    };

    conversation.messages.push(userMessage, assistantMessage);
    conversation.lastMessage = aiResponse;
    conversation.lastMessageAt = assistantMessage.timestamp;

    return HttpResponse.json({
      response: aiResponse,
      conversation_id: targetConversationId,
      message_id: assistantMessage.id,
      user_message_id: userMessage.id,
    });
  }),

  // Error simulation endpoints
  http.get('*/api/test/network-error', () => {
    return HttpResponse.error();
  }),

  http.get('*/api/test/slow-response', async () => {
    await delay(5000);
    return HttpResponse.json({ success: true, data: 'slow response' });
  }),

  http.get('*/api/test/server-error', () => {
    return HttpResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }),
];

// Create the server
export const server = setupServer(...handlers);

// Test utilities for controlling server behavior
export const serverUtils = {
  // Reset all data to initial state
  resetData: () => {
    currentUser = null;
    sessionToken = null;
    // Reset conversations to initial state
    Object.keys(mockConversations).forEach(key => {
      delete mockConversations[key];
    });
    mockConversations['1'] = {
      id: '1',
      title: 'Legal Question about Contracts',
      lastMessage: 'Thank you for the detailed explanation.',
      lastMessageAt: '2024-01-15T10:30:00Z',
      messages: [
        {
          id: '1',
          content: 'I have a question about contract law.',
          isUser: true,
          timestamp: '2024-01-15T10:00:00Z',
          conversationId: '1',
        },
        {
          id: '2',
          content: 'I\'d be happy to help you with contract law. What specific aspect would you like to discuss?',
          isUser: false,
          timestamp: '2024-01-15T10:01:00Z',
          conversationId: '1',
        },
      ],
    };
  },

  // Get current session state
  getCurrentUser: () => currentUser,
  getSessionToken: () => sessionToken,

  // Set up specific test scenarios
  setAuthenticatedUser: (user: User, token: string) => {
    currentUser = user;
    sessionToken = token;
  },

  // Add test data
  addUser: (email: string, userData: User & { password: string }) => {
    mockUsers[email] = userData;
  },

  addConversation: (conversation: Conversation) => {
    mockConversations[conversation.id] = conversation;
  },
};
