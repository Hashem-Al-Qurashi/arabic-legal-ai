# 🔬 Arabic Legal AI - Technical Deep Dive & Function Analysis

## 📋 Function-by-Function Analysis

### 🎨 Frontend Functions

#### App.tsx - Main Application Functions

**Function**: `AppContent`
```typescript
const AppContent: React.FC = () => {
  const { loading } = useAuth();
  // Returns loading spinner or route configuration
}
```
- **Purpose**: Renders loading state or main application routes
- **Dependencies**: useAuth hook from AuthContext
- **Output**: JSX for either loading UI or Routes configuration

**Function**: `App` 
```typescript
const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
};
```
- **Purpose**: Application entry point with context providers
- **Providers**: AuthProvider for authentication, Router for navigation
- **Architecture**: HOC pattern with context injection

#### AuthContext.tsx - Authentication Management

**Function**: `useAuth`
```typescript
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```
- **Purpose**: Hook to access authentication context
- **Error Handling**: Throws error if used outside provider
- **Return Type**: AuthContextType interface

**Function**: `AuthProvider`
```typescript
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isGuest, setIsGuest] = useState(true);
  const [cooldownInfo, setCooldownInfo] = useState<CooldownInfo>({...});
  // ... implementation
};
```
- **State Management**: 
  - `user`: Current user data or null
  - `loading`: Authentication check in progress
  - `isGuest`: Whether user is in guest mode
  - `cooldownInfo`: Rate limiting information

**Function**: `checkAuth` (useCallback)
```typescript
const checkAuth = useCallback(async () => {
  try {
    const token = localStorage.getItem('access_token');
    if (token) {
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
      setIsGuest(false);
    } else {
      setIsGuest(true);
    }
  } catch (error) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsGuest(true);
  } finally {
    setLoading(false);
  }
}, []);
```
- **Purpose**: Validates existing authentication tokens
- **Flow**: Check localStorage → Validate with API → Update state
- **Error Handling**: Clear invalid tokens and set guest mode

**Function**: `login` (useCallback)
```typescript
const login = useCallback(async (email: string, password: string) => {
  console.log('🔑 Starting login process...');
  await authAPI.login({ email, password });
  const currentUser = await authAPI.getCurrentUser();
  setUser(currentUser);
  setIsGuest(false);
  await new Promise(resolve => setTimeout(resolve, 100));
}, []);
```
- **Purpose**: Authenticate user with credentials
- **API Calls**: authAPI.login() → authAPI.getCurrentUser()
- **State Updates**: Set user data and exit guest mode
- **Timing**: 100ms delay for UI state synchronization

**Function**: `incrementQuestionUsage` (useCallback)
```typescript
const incrementQuestionUsage = useCallback(() => {
  setCooldownInfo(prev => {
    const newUsed = prev.questionsUsed + 1;
    const maxQuestions = isGuest ? 5 : 20;
    
    if (newUsed >= maxQuestions) {
      const resetTime = new Date(Date.now() + 90 * 60 * 1000); // 1.5 hours
      return {
        questionsUsed: newUsed,
        maxQuestions,
        isInCooldown: true,
        resetTime,
        timeUntilReset: 90,
        canAskQuestion: false,
        resetTimeFormatted: resetTime.toLocaleTimeString(...)
      };
    }
    
    return { ...prev, questionsUsed: newUsed, maxQuestions, canAskQuestion: true };
  });
}, [isGuest]);
```
- **Purpose**: Handle question usage tracking and cooldown logic
- **Limits**: 5 questions for guests, 20 for authenticated users
- **Cooldown**: 90 minutes when limit reached
- **Real-time**: Updates immediately with formatted time display

#### API Service (services/api.ts)

**Function**: `getApiBaseUrl`
```typescript
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  
  // Local development
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // Local network IP ranges
  if (hostname.match(/^(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)/)) {
    return `http://${hostname}:8000`;
  }
  
  // Production domains
  if (hostname.includes('hokm.ai') || hostname.includes('cloudfront.net')) {
    return 'https://d14ao1bx3dkdxo.cloudfront.net';
  }
  
  return `https://api.${hostname}`;
};
```
- **Purpose**: Dynamic API endpoint detection based on environment
- **Logic**: Regex pattern matching for different deployment scenarios
- **Environments**: Local dev, network testing, production CloudFront

**Function**: `authAPI.login`
```typescript
async login(credentials: LoginRequest): Promise<AuthResponse> {
  const response = await api.post('/api/auth/login', credentials);
  const { access_token, refresh_token, expires_in } = response.data;
  setToken(access_token);
  localStorage.setItem('refresh_token', refresh_token);
  return response.data;
}
```
- **Purpose**: Authenticate user and store tokens
- **API**: POST /api/auth/login with email/password
- **Token Storage**: access_token in memory, refresh_token in localStorage
- **Return**: Complete auth response with token data

**Function**: `chatAPI.sendMessageStreaming`
```typescript
async sendMessageStreaming(
  message: string,
  conversationId?: string,
  sessionId?: string,
  onChunk?: (chunk: string) => void,
  onComplete?: (response: any) => void,
  onError?: (error: string) => void
): Promise<void> {
  const formData = new FormData();
  formData.append('message', message);
  
  if (conversationId) formData.append('conversation_id', conversationId);
  if (sessionId) formData.append('session_id', sessionId);

  const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
    method: 'POST',
    headers: {
      'Accept': 'text/event-stream',
      ...(getToken() && { 'Authorization': `Bearer ${getToken()}` }),
    },
    body: formData
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6).trim();
        if (data === '[DONE]') return;

        try {
          const parsed = JSON.parse(data);
          if (parsed.type === 'chunk' && onChunk) {
            onChunk(parsed.content);
          } else if (parsed.type === 'complete' && onComplete) {
            onComplete(parsed);
          }
        } catch (e) {
          // Skip invalid JSON
        }
      }
    }
  }
}
```
- **Purpose**: Real-time streaming chat with Server-Sent Events
- **Protocol**: SSE with data: prefixed JSON chunks
- **Error Handling**: Graceful JSON parsing failures
- **Callbacks**: onChunk for real-time updates, onComplete for final response

#### Message Parser (utils/messageParser.ts)

**Function**: `formatAIResponse`
```typescript
export const formatAIResponse = (content: string): string => {
  // Step 1: Clean input
  let cleaned = content
    .replace(/<\/?bold>/gi, '')
    .replace(/[\u200e\u200f\u202a-\u202e\uFEFF]/g, '')
    .trim();

  // Step 2: Fix stuck markdown headers
  cleaned = cleaned
    .replace(/([^\s\n])(#{1,6})/g, '$1\n\n$2')
    .replace(/([.!?؟])([A-Z\u0600-\u06FF])/g, '$1\n\n$2');

  // Step 3: Convert markdown to HTML
  let html = cleaned
    .replace(/^#{6}\s*(.*$)/gim, '<h6>$1</h6>')
    .replace(/^#{5}\s*(.*$)/gim, '<h5>$1</h5>')
    .replace(/^#{4}\s*(.*$)/gim, '<h4>$1</h4>')
    .replace(/^#{3}\s*(.*$)/gim, '<h3>$1</h3>')
    .replace(/^#{2}\s*(.*$)/gim, '<h2>$1</h2>')
    .replace(/^#{1}\s*(.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^[-•]\s+(.*)$/gm, '<li>$1</li>')
    .replace(/^\d+\.\s+(.*)$/gm, '<li>$1</li>');

  // Step 4: Wrap lists and paragraphs
  const paragraphs = html.split(/\n\s*\n/).filter(p => p.trim());
  html = paragraphs.map(p => {
    p = p.trim();
    return p.match(/^<[holu]/i) ? p : `<p>${p}</p>`;
  }).join('\n');

  return html;
};
```
- **Purpose**: Convert AI markdown responses to formatted HTML
- **Cleaning**: Remove control characters and fix spacing issues
- **Markdown**: Support for headers (h1-h6), bold, italic, lists
- **Arabic Support**: Unicode ranges for Arabic text detection
- **HTML Generation**: Proper semantic markup with paragraphs and lists

### 🔧 Backend Functions

#### Main Application (app/main.py)

**Function**: `root`
```python
@app.get("/")
async def root():
    return {
        "service": "Arabic Legal Assistant - Unified Edition",
        "version": "3.0.0",
        "status": "active",
        "features": {...},
        "endpoints": {...},
        "architecture": {...},
        "cors_origins": settings.allowed_origins,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now().isoformat()
    }
```
- **Purpose**: API information endpoint with system status
- **Returns**: Service metadata, available endpoints, configuration
- **Usage**: Health check and API discovery

**Function**: `health_check`
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "Arabic Legal Assistant - Unified Edition",
        "version": "3.0.0",
        "features": [...]
    }
```
- **Purpose**: Application health monitoring
- **Used By**: Load balancers, monitoring systems
- **Returns**: Service status and feature list

#### Chat Service (app/services/chat_service.py)

**Function**: `create_conversation`
```python
@staticmethod
def create_conversation(db: Session, user_id: str, title: Optional[str] = None) -> Conversation:
    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title or "محادثة جديدة",
        is_active=True
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation
```
- **Purpose**: Create new conversation for authenticated users
- **Database**: SQLAlchemy ORM with PostgreSQL/SQLite
- **UUID**: Generates unique conversation identifier
- **Default Title**: Arabic "New Conversation" if none provided

**Function**: `get_conversation_context`
```python
@staticmethod
def get_conversation_context(db: Session, conversation_id: str, max_messages: int = 10) -> List[Dict[str, str]]:
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.desc()
    ).limit(max_messages).all()
    
    messages.reverse()  # Chronological order
    
    return [{
        "role": message.role,
        "content": message.content
    } for message in messages]
```
- **Purpose**: Retrieve conversation history for AI context
- **Database Query**: Last N messages ordered by creation time
- **Order**: Reversed to chronological (oldest first) for AI context
- **Return Format**: Role/content pairs for AI conversation format

**Function**: `process_chat_message`
```python
@staticmethod
async def process_chat_message(
    db: Session,
    user: User,
    conversation_id: Optional[str],
    message_content: str
) -> Dict[str, Any]:
    start_time = datetime.utcnow()
    
    # Check user limits
    can_proceed, limit_message = AuthService.check_user_limits(db, user.id)
    if not can_proceed:
        raise Exception(limit_message)
    
    # Get or create conversation
    if conversation_id:
        conversation = db.query(Conversation).filter(...).first()
    else:
        conversation = ChatService.create_conversation(db, user.id, ...)
    
    # Add user message
    user_message = ChatService.add_message(db, conversation_id, "user", message_content)
    
    # Get context and process with RAG
    context_messages = ChatService.get_conversation_context(db, conversation_id, 10)
    rag_instance = get_rag_engine()
    
    chunks = []
    async for chunk in rag_instance.ask_question_with_context_streaming(message_content, context_messages):
        chunks.append(chunk)
    ai_response = ''.join(chunks)
    
    # Save AI response and update usage
    ai_message = ChatService.add_message(db, conversation_id, "assistant", ai_response, ...)
    UserService.increment_question_usage(db, user.id)
    
    return {...}  # Formatted response with all message data
```
- **Purpose**: Complete authenticated user message processing pipeline
- **Rate Limiting**: Check user question limits before processing
- **Conversation Management**: Create new or use existing conversation
- **AI Processing**: RAG engine with conversation context
- **Database Operations**: Store user/AI messages, update usage counters
- **Performance**: Track processing time in milliseconds

**Function**: `process_guest_message`
```python
@staticmethod
async def process_guest_message(
    session_id: str,
    message_content: str
) -> Dict[str, Any]:
    start_time = datetime.utcnow()
    
    if not session_id:
        session_id = ChatService.create_guest_session()
    
    # Add user message to session
    ChatService.add_guest_message(session_id, "user", message_content)
    
    # Get conversation context
    context_messages = ChatService.get_guest_context(session_id, 10)
    
    # Process with RAG engine
    rag_instance = get_rag_engine()
    chunks = []
    async for chunk in rag_instance.ask_question_with_context_streaming(message_content, context_messages):
        chunks.append(chunk)
    ai_response = ''.join(chunks)
    
    # Add AI response to session
    ChatService.add_guest_message(session_id, "assistant", ai_response)
    
    return {...}  # Formatted response similar to authenticated users
```
- **Purpose**: Process messages for guest users without database persistence
- **Session Management**: In-memory storage with session IDs
- **Context**: Same conversation context as authenticated users
- **AI Processing**: Identical RAG engine processing
- **No Database**: Everything stored in memory for guest experience

#### RAG Engine (rag_engine.py)

**Function**: `SimpleCitationFixer.fix_citations`
```python
def fix_citations(self, ai_response: str, available_documents: List[Chunk]) -> str:
    if not available_documents:
        return ai_response
    
    # Get statute titles only (no memos)
    real_titles = [doc.title for doc in available_documents]
    statute_titles = [title for title in real_titles 
             if any(term in title for term in [
                 "نظام", "المادة", "لائحة", "مرسوم", "التعريفات",
                 "قانون", "قرار وزاري", "تعليمات", "ضوابط", "قواعد"
             ]) 
             and 'مذكرة' not in title.lower()
             and 'دفع' not in title.lower()
             and 'حجة' not in title.lower()]
    
    # Remove memo citations with comprehensive regex patterns
    memo_citation_patterns = [
        r'وفقاً\s*لـ\s*["\']?مذكرة[^"\'.\n]*["\']?',
        r'استناداً\s*إلى\s*["\']?مذكرة[^"\'.\n]*["\']?',
        # ... more patterns
    ]
    
    for pattern in memo_citation_patterns:
        fixed_response = re.sub(pattern, '', fixed_response, flags=re.IGNORECASE)
    
    # Replace weak citations with strong statute citations
    citation_patterns = [
        (r'وفقاً لـ"[^"]*"', f'وفقاً لـ"{statute_titles[0]}"'),
        (r'استناداً إلى "[^"]*"', f'استناداً إلى "{statute_titles[1] if len(statute_titles) > 1 else statute_titles[0]}"'),
        # ... more replacements
    ]
    
    return fixed_response
```
- **Purpose**: Clean AI responses by removing inappropriate citations and enhancing legal references
- **Arabic Legal Terms**: Filters for official statutes vs informal memos
- **Regex Patterns**: Comprehensive Arabic citation pattern matching
- **Citation Enhancement**: Replace generic references with specific statute titles

### 🗄️ Database Operations

#### User Model Functions

**Field**: `questions_used_current_cycle`
- **Type**: Integer
- **Purpose**: Track questions used in current cooldown cycle
- **Reset**: When cycle_reset_time expires
- **Limits**: 5 for guests, 20 for authenticated users

**Field**: `cycle_reset_time`
- **Type**: DateTime with timezone
- **Purpose**: When the current usage cycle resets
- **Calculation**: Current time + 90 minutes when limit reached
- **Used By**: Frontend countdown timer and backend rate limiting

#### Conversation Model Functions

**Relationship**: `messages`
```python
messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
```
- **Purpose**: One-to-many relationship with Message model
- **Cascade**: Delete all messages when conversation is deleted
- **Order**: Messages ordered by created_at timestamp

**Method**: `__repr__`
```python
def __repr__(self):
    return f"<Conversation(id='{self.id}', title='{self.title}', user_id='{self.user_id}')>"
```
- **Purpose**: String representation for debugging
- **Includes**: Primary key, title, and user association

#### Message Model Functions

**Field**: `role`
- **Type**: String(20)
- **Values**: 'user' or 'assistant'
- **Purpose**: Distinguish between user input and AI responses

**Field**: `content`
- **Type**: Text (unlimited length)
- **Purpose**: Store full message content
- **Format**: Plain text for user messages, markdown for AI responses

**Field**: `processing_time_ms`
- **Type**: String(10) 
- **Purpose**: Store AI processing time for performance monitoring
- **Format**: Milliseconds as string for easy display

### 🔐 Security Functions

#### Token Management

**Function**: `create_access_token`
```python
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```
- **Purpose**: Generate JWT access tokens for authentication
- **Expiration**: 30 minutes by default
- **Claims**: User email, expiration, token type
- **Algorithm**: HS256 with secret key

**Function**: `create_refresh_token`
```python
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```
- **Purpose**: Generate longer-lived refresh tokens
- **Expiration**: 7 days by default
- **Usage**: Obtain new access tokens without re-authentication

#### CORS Configuration

**Property**: `allowed_origins` (config.py)
```python
@property
def allowed_origins(self) -> List[str]:
    cors_env = os.environ.get('CORS_ORIGINS') or self.cors_origins
    if cors_env:
        origins = [origin.strip() for origin in cors_env.split(",")]
        return [origin for origin in origins if origin]
    
    if self.environment == Environment.DEVELOPMENT:
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000", 
            "http://192.168.1.10:3000",
            "https://hokm.ai",
            # ... more development origins
        ]
    else:  # Production
        return [
            "https://hokm.ai",
            "https://www.hokm.ai",
            "https://d19s2p97xyms4l.cloudfront.net",
            # ... production CloudFront distributions
        ]
```
- **Purpose**: Environment-specific CORS origin configuration
- **Development**: Localhost, local network IPs, test domains
- **Production**: Official domains and CloudFront distributions
- **Security**: No wildcards in production, specific domain whitelist

### 📊 Performance Monitoring

#### Processing Time Tracking
```python
start_time = datetime.utcnow()
# ... AI processing ...
processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
```
- **Measurement**: Millisecond precision timing
- **Storage**: Saved with each message for analytics
- **Usage**: Performance monitoring and optimization

#### Memory Management

**Guest Sessions**: `_guest_sessions: Dict[str, List[Dict[str, str]]]`
- **Lifecycle**: In-memory storage, cleared on restart
- **Limits**: Maximum 20 messages per session
- **Cleanup**: Automatic trimming of old messages

#### Database Query Optimization
```python
# Efficient conversation retrieval with limits
return db.query(Conversation).filter(
    Conversation.user_id == user_id,
    Conversation.is_active == True
).order_by(
    Conversation.updated_at.desc()
).limit(limit).all()
```
- **Indexing**: user_id and is_active columns indexed
- **Ordering**: Most recent conversations first
- **Limits**: Configurable result set size for performance

### 🚀 Deployment Functions

#### Environment Detection
```python
def validate_configuration(self):
    # Validate debug mode in production
    if self.environment == Environment.PRODUCTION and self.debug:
        raise ValueError("Debug mode cannot be enabled in production")
    
    # Validate AI provider configuration
    if not self.openai_api_key and not self.deepseek_api_key:
        raise ValueError("At least one AI provider API key must be configured")
```
- **Purpose**: Prevent configuration errors in production
- **Checks**: Debug mode, API keys, database settings
- **Fail-fast**: Application won't start with invalid configuration

#### Health Monitoring
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "features": ["unified_chat", "guest_sessions", "conversation_memory", ...]
    }
```
- **Purpose**: Load balancer and monitoring system integration
- **Data**: Service status, timestamp, feature list
- **Usage**: AWS ALB health checks, Kubernetes probes

---

## 🔄 Data Flow Analysis

### Message Processing Pipeline

1. **Frontend Input**: User types message in ChatApp component
2. **Validation**: React Hook Form validates input length and content
3. **API Call**: chatAPI.sendMessageStreaming() with FormData
4. **Authentication**: JWT token automatically added by Axios interceptor
5. **Backend Routing**: FastAPI routes to /api/chat/message endpoint
6. **Rate Limiting**: cooldown_service.can_user_ask_question() check
7. **Conversation Logic**: Create new or retrieve existing conversation
8. **Database Write**: Save user message to messages table
9. **Context Retrieval**: Get last 10 messages for AI context
10. **RAG Processing**: Vector search + AI generation with context
11. **Streaming Response**: Server-Sent Events with chunked AI response
12. **Frontend Updates**: Real-time UI updates with streaming content
13. **Database Write**: Save complete AI response to messages table
14. **Usage Tracking**: Increment user question counter
15. **Final State**: UI shows complete conversation with all messages

### Authentication Flow

1. **Initial Load**: App.tsx loads, AuthProvider checks localStorage
2. **Token Validation**: If token exists, call /api/chat/status endpoint
3. **User Data**: Backend returns user profile and usage statistics
4. **State Update**: AuthContext updates with user data or guest mode
5. **Route Protection**: Routes conditionally render based on auth state
6. **Token Refresh**: Automatic refresh when access token expires
7. **Logout**: Clear tokens and redirect to authentication screen

### Real-Time Communication

1. **WebSocket Alternative**: Server-Sent Events for browser compatibility
2. **Stream Format**: `data: {"type": "chunk", "content": "text"}\n\n`
3. **Error Handling**: Graceful fallback for connection failures
4. **Buffering**: Client-side buffer management for partial chunks
5. **Completion**: `data: [DONE]\n\n` signals end of stream

---

*This technical documentation provides comprehensive function-level analysis of the Arabic Legal AI system. Every major function, database operation, and API endpoint has been documented with its purpose, parameters, and integration points.*