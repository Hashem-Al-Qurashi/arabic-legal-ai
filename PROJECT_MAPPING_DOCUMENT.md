# Arabic Legal AI Assistant - Complete Project Mapping Document

## 🏗️ Project Overview
**Name:** Arabic Legal AI Assistant  
**Type:** Full-stack web application  
**Domain:** Legal consultation platform for Saudi Arabian law  
**Architecture:** Modern microservices-style with React frontend + FastAPI backend

---

## 📁 Project Structure

### Root Directory
```
/home/sakr_quraish/Projects/legal/
├── arabic_legal_ai/          # Main application
├── clean_ae0f31e/           # Backup/clean version
└── ...
```

### Main Application Structure
```
arabic_legal_ai/
├── backend/                 # Python FastAPI backend
├── frontend/               # React TypeScript frontend
├── infrastructure/         # AWS deployment configs
├── data/                   # Database files
├── chroma_storage/         # Vector database
└── docker-compose.yml      # Container orchestration
```

---

## 🖥️ Frontend Architecture

### Technology Stack
- **Framework:** React 18.2.0 with TypeScript
- **Build Tool:** Vite 4.4.5
- **Routing:** React Router DOM 6.20.1
- **State Management:** React Context API
- **Forms:** React Hook Form 7.48.2 + Zod validation
- **HTTP Client:** Axios 1.6.0
- **Styling:** Custom CSS with theme system
- **Toast Notifications:** React Hot Toast 2.4.1
- **Security:** DOMPurify 3.2.6

### Component Architecture
```
src/
├── components/
│   ├── actions/           # Action bar components
│   │   ├── ActionBar.tsx
│   │   └── index.ts
│   ├── auth/              # Authentication components
│   │   ├── AuthScreen.tsx
│   │   ├── GoogleSignInButton.tsx
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── index.ts
│   ├── chat/              # Main chat interface
│   │   ├── AttachmentPreview.tsx
│   │   ├── ChatApp.tsx    # Core 1900+ line component
│   │   ├── FileUploadButton.tsx
│   │   └── index.ts
│   ├── message/           # Message rendering
│   │   ├── FormattedMessage.tsx
│   │   ├── MessageRenderer.tsx
│   │   └── index.ts
│   ├── premium/           # Premium features
│   │   ├── FeatureTease.tsx
│   │   ├── PremiumProgress.tsx
│   │   └── index.ts
│   └── ui/                # Reusable UI components
│       ├── DeletePopup.tsx
│       ├── RenamePopup.tsx
│       └── index.ts
├── contexts/
│   └── AuthContext.tsx    # Global authentication state
├── hooks/
│   ├── useConversationRouting.ts  # Navigation logic
│   └── useTheme.ts        # Theme management
├── services/
│   └── api.ts             # API client configuration
├── styles/
│   └── theme.config.ts    # Theme configuration
├── types/
│   └── index.ts           # TypeScript definitions
├── utils/
│   ├── helpers.ts         # Utility functions
│   ├── messageParser.ts   # Message formatting
│   └── security.ts        # Security utilities
├── App.tsx                # Main app component (80 lines)
├── App.css                # Application styles
├── index.css              # Global styles
└── main.tsx               # Application entry point
```

### Routing Structure
- **Base Route:** `/` - Home/default chat interface
- **Conversation Route:** `/c/:conversationId` - Specific conversation
- **Auth Route:** `/auth` - Authentication screen
- **Fallback:** `*` - Redirects to home

### Theme System
- **Architecture:** CSS custom properties with light/dark mode
- **Storage:** localStorage persistence
- **Implementation:** CSS classes + React hooks
- **Transitions:** Smooth 0.3s animations
- **Mobile:** Meta theme-color support

---

## 🔧 Backend Architecture

### Technology Stack
- **Framework:** FastAPI 0.104.1
- **Server:** Uvicorn with Gunicorn for production
- **Database:** SQLAlchemy 2.0.23 + Alembic migrations
- **Authentication:** JWT with python-jose + bcrypt
- **Google Auth:** google-auth 2.23.4
- **AI/ML:** OpenAI API 1.3.8
- **OCR:** Google Cloud Vision 3.4.5
- **Document Processing:** python-docx, pypdf2, Pillow
- **Testing:** pytest + pytest-asyncio

### API Structure
```
app/
├── api/                   # API endpoints
│   ├── chat.py           # Chat/conversation endpoints
│   ├── export.py         # Document export
│   ├── google_auth.py    # Google OAuth
│   ├── ocr.py           # OCR processing
│   └── simple_auth.py    # JWT authentication
├── core/                 # Core configuration
│   ├── config.py         # Settings management
│   ├── database.py       # Database setup
│   ├── security.py       # Security utilities
│   └── strategic_templates.py
├── dependencies/         # FastAPI dependencies
│   ├── auth.py          # Auth dependencies
│   └── simple_auth.py    # Simple auth deps
├── legal_reasoning/      # AI processing
│   ├── ai_domain_classifier.py
│   ├── document_generator.py
│   ├── issue_analyzer.py
│   └── memo_processor.py
├── models/              # Database models
│   ├── base.py          # Base model
│   ├── consultation.py   # Consultation model
│   ├── conversation.py   # Conversation/Message models
│   └── user.py          # User model
├── schemas/             # Pydantic schemas
│   ├── auth.py          # Auth schemas
│   ├── consultation.py   # Consultation schemas
│   └── user.py          # User schemas
├── services/            # Business logic
│   ├── auth_service.py   # Authentication logic
│   ├── chat_service.py   # Chat functionality
│   ├── cooldown_service.py # Rate limiting
│   ├── document_service.py # Document handling
│   ├── guest_service.py  # Guest user logic
│   └── user_service.py   # User management
├── storage/             # Data storage
│   ├── sqlite_store.py   # SQLite operations
│   └── vector_store.py   # Vector database
└── utils/               # Utilities
    └── chromadb_manager.py # Vector DB management
```

### API Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login  
- `POST /api/auth/google` - Google OAuth
- `GET /api/auth/google/status` - Google auth status

#### Chat System
- `POST /api/chat/message` - Send message (unified endpoint)
- `GET /api/chat/conversations` - List user conversations
- `GET /api/chat/conversations/{id}/messages` - Get conversation messages
- `PUT /api/chat/conversations/{id}/title` - Update conversation title
- `DELETE /api/chat/conversations/{id}` - Delete conversation
- `GET /api/chat/status` - System status

#### Document Processing
- `POST /api/ocr/extract` - OCR text extraction
- `GET /api/ocr/status` - OCR status
- `GET /export/docx` - Export conversation to DOCX
- `GET /export/test` - Export functionality test

#### System
- `GET /` - API root with system info
- `GET /health` - Health check
- `POST /api/ask` - Legacy endpoint (deprecated, returns 410)

---

## 🗄️ Database Schema

### Core Models
1. **User** - User accounts and authentication
2. **Conversation** - Chat conversations
3. **Message** - Individual messages
4. **Consultation** - Legal consultation records

### Database Files
- `arabic_legal.db` - Main application database
- `vectors.db` - Vector embeddings
- `quranic_foundation.db` - Islamic law knowledge base

---

## 🎨 UI/UX Design System

### Design Language
- **Primary Colors:** Saudi green (#006C35, #004A24)
- **Typography:** Noto Sans Arabic for Arabic text
- **Layout:** Responsive with mobile-first approach
- **Interactions:** Smooth transitions and micro-animations
- **Accessibility:** ARIA labels and keyboard navigation

### Key UI Components
- **ChatApp:** Main conversational interface
- **AuthScreen:** Login/registration forms
- **MessageRenderer:** AI response formatting
- **ActionBar:** Message actions (export, copy, etc.)
- **PremiumProgress:** Usage tracking display
- **FileUploadButton:** Document upload functionality

---

## 🔐 Security Architecture

### Authentication
- **Method:** JWT tokens with refresh mechanism
- **Storage:** localStorage for tokens
- **Google OAuth:** Alternative authentication method
- **Session Management:** Automatic token refresh

### Security Features
- **Input Sanitization:** DOMPurify for HTML content
- **CORS:** Configured for specific origins
- **Rate Limiting:** Cooldown system for API usage
- **Validation:** Zod schemas for form validation
- **SQL Injection:** SQLAlchemy ORM protection

---

## 🌐 Deployment & Infrastructure

### Development Environment
- **Frontend:** Vite dev server on port 3000
- **Backend:** Uvicorn on port 8000
- **Database:** SQLite for development
- **CORS:** Configured for localhost

### Production Architecture
- **Domain:** hokm.ai
- **API Domain:** api.hokm.ai
- **CDN:** CloudFront distribution
- **Infrastructure:** AWS-based (Terraform configs available)

### Environment Detection
```javascript
// Frontend automatically detects:
// - localhost/127.0.0.1 -> http://localhost:8000
// - Local network IPs -> http://IP:8000  
// - hokm.ai domains -> https://api.hokm.ai
// - Other domains -> https://api.${domain}
```

---

## 🚀 Key Features

### Core Functionality
1. **AI Legal Consultation** - Saudi law-specific advice
2. **Conversation Memory** - Persistent chat history
3. **Guest Mode** - Session-based conversations for non-registered users
4. **Document Upload** - OCR processing for legal documents
5. **Export Capabilities** - DOCX export with Arabic support
6. **User Management** - Registration, login, cooldown systems

### Technical Features
1. **Unified Chat API** - Single endpoint for all user types
2. **Real-time Responses** - Streaming AI responses
3. **Context Awareness** - Conversation history integration
4. **Theme System** - Light/dark mode with persistence
5. **Mobile Optimization** - Responsive design
6. **Security** - Input sanitization and authentication

---

## 📊 Architecture Patterns

### Frontend Patterns
- **Component Composition** - Modular, reusable components
- **Custom Hooks** - Shared logic extraction
- **Context API** - Global state management
- **Error Boundaries** - Graceful error handling
- **Lazy Loading** - Performance optimization

### Backend Patterns
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic separation
- **Dependency Injection** - FastAPI dependencies
- **Factory Pattern** - Configuration management
- **Strategy Pattern** - Different AI processing strategies

---

## 🔄 Data Flow

### User Message Flow
1. User inputs message in ChatApp
2. Frontend validates and sanitizes input
3. API call to `/api/chat/message`
4. Backend processes through AI reasoning chain
5. Response streamed back to frontend
6. Message stored in database
7. UI updated with formatted response

### Authentication Flow
1. User submits credentials
2. Backend validates against database
3. JWT token generated and returned
4. Frontend stores token in localStorage
5. Subsequent requests include Authorization header
6. Backend validates token on protected routes

---

## 🎯 Mobile Conversion Considerations

### Current Web Features to Preserve
- ✅ Real-time AI chat interface
- ✅ User authentication (JWT + Google OAuth)
- ✅ Conversation history and persistence
- ✅ Document upload and OCR processing
- ✅ Dark/light theme switching
- ✅ Arabic language support
- ✅ Export functionality
- ✅ Guest mode access
- ✅ Rate limiting and cooldowns

### Mobile-Specific Adaptations Needed
- 📱 Touch-optimized UI components
- 📱 Native file picker integration
- 📱 Push notifications for responses
- 📱 Offline capability for conversation history
- 📱 Platform-specific navigation patterns
- 📱 Biometric authentication integration
- 📱 Native sharing capabilities
- 📱 Camera integration for document capture

### API Compatibility
The existing REST API is fully mobile-ready:
- Standard HTTP endpoints
- JSON request/response format
- JWT authentication
- CORS properly configured
- No web-specific dependencies

---

## 📝 Development Notes

### Code Quality
- **TypeScript:** Full type safety in frontend
- **Code Organization:** Clean separation of concerns
- **Error Handling:** Comprehensive error boundaries
- **Performance:** Optimized with React best practices
- **Maintainability:** Well-documented and modular

### Recent Refactoring
- Original 4,550-line App.tsx successfully broken down into modular components
- Zero functionality lost during refactoring
- Enterprise-ready architecture implemented
- Clean file structure for team development

### Testing Infrastructure
- pytest for backend testing
- Component testing setup available
- API integration tests implemented

---

*This document serves as the complete mapping for web-to-mobile conversion, ensuring perfect feature parity and understanding of the existing architecture.*