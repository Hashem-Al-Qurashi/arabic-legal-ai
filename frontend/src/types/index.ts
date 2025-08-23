// =====================================================================
// 🏗️ COMPREHENSIVE TYPE DEFINITIONS - EXTRACTED FROM 4550-LINE APP.TSX
// =====================================================================

/**
 * Conversation route parameters for URL routing
 */
export interface ConversationRouteParams extends Record<string, string | undefined> {
  conversationId?: string;
}

/**
 * Props for conversation-aware components
 */
export interface ConversationRouteProps {
  conversationId?: string;
  onConversationChange?: (conversationId: string | null) => void;
}

/**
 * Return type for the conversation routing hook
 */
export interface UseConversationRoutingReturn {
  conversationId: string | null;
  navigateToConversation: (conversationId: string) => void;
  navigateToHome: () => void;
  isValidConversationId: (conversationId: string) => boolean;
}

// =====================================================================
// UI COMPONENT PROPS
// =====================================================================

/**
 * Props for rename popup component
 */
export interface RenamePopupProps {
  isOpen: boolean;
  currentTitle: string;
  onSave: (newTitle: string) => void;
  onCancel: () => void;
}

/**
 * Props for delete confirmation popup
 */
export interface DeletePopupProps {
  isOpen: boolean;
  conversationTitle: string;
  onConfirm: () => void;
  onCancel: () => void;
}

/**
 * Props for premium progress indicator
 */
export interface PremiumProgressProps {
  current: number;
  max: number;
  label: string;
  type: 'messages' | 'exports' | 'exchanges' | 'citations';
}

/**
 * Props for feature tease component
 */
export interface FeatureTeaseProps {
  title: string;
  description: string;
  icon: string;
  disabled: boolean;
  onUpgrade: () => void;
}

/**
 * Props for actions bar component
 */
export interface ActionsBarProps {
  content: string;
  isLastMessage: boolean;
  messages: Message[];
  conversations: Conversation[];
  selectedConversation: string | null;
}

/**
 * Props for formatted message component
 */
export interface FormattedMessageProps {
  content: string;
  role: 'user' | 'assistant';
  sidebarOpen: boolean;
  isLastMessage?: boolean;
  messages?: Message[];
  conversations?: Conversation[];
  selectedConversation?: string | null;
  isDark?: boolean;
}

// =====================================================================
// MESSAGE PARSING AND FORMATTING
// =====================================================================

/**
 * Parsed HTML element structure
 */
export interface ParsedElement {
  type: 'heading' | 'paragraph' | 'text' | 'strong' | 'emphasis' | 'listItem';
  content: string;
  level?: number;
  children?: ParsedElement[];
}

/**
 * Message content element structure
 */
export interface MessageElement {
  type: 'heading' | 'paragraph' | 'list' | 'listItem' | 'strong' | 'emphasis' | 'text';
  level?: number; // for headings (1-6)
  content: string;
  children?: MessageElement[];
}

/**
 * Table data structure for comparison tables
 */
export interface TableData {
  headers: string[];
  rows: string[][];
}

// =====================================================================
// CORE DATA MODELS
// =====================================================================

/**
 * Message data structure
 */
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  processing_time_ms?: number;
}

/**
 * Conversation data structure
 */
export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message_preview: string | null;
  message_count: number;
}

// =====================================================================
// UTILITY TYPES
// =====================================================================

/**
 * Toast notification types
 */
export type ToastType = 'error' | 'success' | 'info' | 'warning';

/**
 * Theme types
 */
export type Theme = 'light' | 'dark';

/**
 * API response wrapper
 */
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

/**
 * Chat request payload
 */
export interface ChatRequest {
  message: string;
  conversationId?: string;
  stream?: boolean;
}

/**
 * Chat response payload
 */
export interface ChatResponse {
  response: string;
  conversationId: string;
  messageId: string;
}

// =====================================================================
// AUTHENTICATION TYPES (imported from existing context)
// =====================================================================

/**
 * User data structure (from AuthContext)
 */
export interface User {
  id: string;
  email: string;
  full_name: string;
  subscription_tier: string;
  is_active: boolean;
  is_verified: boolean;
  questions_used_current_cycle: number;
  cycle_reset_time: string;
}

/**
 * Authentication state
 */
export interface AuthState {
  user: User | null;
  loading: boolean;
  isGuest: boolean;
  isAuthenticated: boolean;
}

/**
 * Login credentials
 */
export interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * Registration credentials
 */
export interface RegisterCredentials extends LoginCredentials {
  full_name: string;
}

// =====================================================================
// PREMIUM FEATURE TYPES
// =====================================================================

/**
 * Premium feature configuration
 */
export interface PremiumFeature {
  id: string;
  name: string;
  description: string;
  icon: string;
  enabled: boolean;
  requiresUpgrade: boolean;
}

/**
 * Usage limits configuration
 */
export interface UsageLimits {
  messages: { current: number; max: number };
  exports: { current: number; max: number };
  exchanges: { current: number; max: number };
  citations: { current: number; max: number };
}

// =====================================================================
// MOBILE AND RESPONSIVE TYPES
// =====================================================================

/**
 * Mobile configuration
 */
export interface MobileConfig {
  isMobile: boolean;
  screenWidth: number;
  touchDevice: boolean;
}

/**
 * Sidebar configuration
 */
export interface SidebarConfig {
  isOpen: boolean;
  width: number;
  collapsible: boolean;
}

// =====================================================================
// ADVANCED MESSAGE TYPES
// =====================================================================

/**
 * Multi-agent response indicators
 */
export interface MultiAgentIndicators {
  hasAgents: boolean;
  agentCount: number;
  sections: string[];
}

/**
 * Citation data structure
 */
export interface Citation {
  id: string;
  text: string;
  source: string;
  url?: string;
  confidence: number;
}

/**
 * Legal document reference
 */
export interface LegalReference {
  type: 'law' | 'regulation' | 'case' | 'article';
  title: string;
  number?: string;
  section?: string;
  year?: number;
  jurisdiction: string;
}

// =====================================================================
// ERROR HANDLING TYPES
// =====================================================================

/**
 * Application error structure
 */
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
}

/**
 * Validation error structure
 */
export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

// =====================================================================
// EXPORT ALL TYPES FOR EASY IMPORTING
// =====================================================================

export * from '../contexts/AuthContext';