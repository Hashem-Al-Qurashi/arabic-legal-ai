/**
 * Chat-related type definitions
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  processing_time_ms?: number;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message_preview: string | null;
}

// Parsed message elements for structured content
export interface ParsedElement {
  type: 'text' | 'citation' | 'header' | 'list' | 'table' | 'heading' | 'paragraph' | 'listItem' | 'strong' | 'emphasis';
  content: string;
  metadata?: Record<string, any>;
  level?: number; // For heading levels (h1-h6)
  children?: ParsedElement[]; // For nested elements
}