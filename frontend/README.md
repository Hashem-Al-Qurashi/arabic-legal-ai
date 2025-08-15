# حكم - Arabic Legal AI Assistant Frontend

## 🚀 Enterprise-Grade React Application

Advanced frontend for the Arabic Legal AI Assistant with modern architecture, zero technical debt, and mobile-first design.

## 🏗️ Architecture Highlights

- **Senior-Level Height Constraint System**: Unbroken viewport → grid → flex → scroll chain
- **Modern CSS Touch Events**: Zero JavaScript touch handling conflicts
- **Progressive Web App**: Full offline support with service worker
- **RTL Arabic Layout**: Native right-to-left design system
- **Real-time Streaming**: Live AI response updates
- **Mobile-First Responsive**: ChatGPT-style mobile experience

## 📱 Key Features

### ✨ **Advanced UI/UX**
- Dark/Light theme switching with persistence
- Responsive sidebar with proper scroll containment  
- Real-time AI response streaming
- Mobile ChatGPT-replica design
- Arabic typography optimization

### 🔧 **Technical Excellence**
- TypeScript for type safety
- Vite for lightning-fast builds
- Modern CSS architecture (Grid + Flexbox)
- PWA with offline capabilities
- AWS CloudFront deployment

### 🌐 **Internationalization**
- RTL (Right-to-Left) Arabic layout
- Proper Arabic text rendering
- Cultural design considerations
- Multi-device compatibility

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Modern browser with ES2020+ support

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production  
npm run build

# Preview production build
npm run preview
```

### Environment Configuration
```bash
# Create .env file
VITE_API_URL=your_api_endpoint
VITE_APP_TITLE="حكم - المساعد القانوني الذكي"
```

## 📁 Project Structure

```
src/
├── components/           # React components
│   ├── chat/            # Chat interface components
│   ├── auth/            # Authentication components
│   ├── ui/              # Reusable UI components
│   └── premium/         # Premium feature components
├── contexts/            # React context providers
├── hooks/               # Custom React hooks
├── services/            # API and external services
├── utils/               # Utility functions
├── types/               # TypeScript type definitions
└── styles/              # Global styles and themes
```

## 🎯 Architecture Deep Dive

### Height Constraint System
Our breakthrough **senior-level height constraint architecture** solves the mobile scrolling problem:

```css
/* Viewport → Grid → Flex → Scroll Chain */
.chat-grid-container {
  height: 100dvh !important;  /* Never breaks constraint */
}

.sidebar-scroll-container {
  flex: 1;
  min-height: 0;             /* Critical for flex shrinking */
}

.sidebar-scroll {
  position: absolute;         /* Isolated scroll boundary */
  overflow-y: auto;
}
```

### Modern Touch Events
Zero-conflict touch handling with CSS-native approach:

```css
.sidebar-container {
  touch-action: pan-y !important;    /* Only vertical scroll */
}

.mobile-backdrop {
  touch-action: none !important;     /* Block all gestures */
}
```

## 🔄 State Management

### Context Architecture
- **AuthContext**: User authentication and session management
- **ThemeContext**: Dark/light mode with system preference detection  
- **ChatContext**: Real-time conversation state

### Data Flow
```
User Input → Component → Context → API Service → Backend → Streaming Response → UI Update
```

## 📱 Mobile-First Design

### Responsive Breakpoints
- **Mobile**: `< 768px` - Overlay sidebar, ChatGPT-style
- **Tablet**: `768px - 1024px` - Adaptive layout
- **Desktop**: `> 1024px` - Side-by-side layout

### Mobile Optimizations
- Dynamic viewport units (`100dvh`)
- Touch-friendly 44px minimum targets
- iOS Safari compatibility fixes
- Gesture-based navigation

## 🚀 Performance

### Core Web Vitals
- **LCP**: < 2.5s (Largest Contentful Paint)
- **FID**: < 100ms (First Input Delay)
- **CLS**: < 0.1 (Cumulative Layout Shift)

### Bundle Optimization
- **Vite**: Fast builds with tree-shaking
- **Code Splitting**: Dynamic imports for route chunks
- **Asset Optimization**: Compressed images and fonts
- **CDN Delivery**: AWS CloudFront global distribution

## 🔐 Security

### Input Sanitization
```typescript
// Secure HTML content handling
const sanitizedContent = sanitizeHTML(aiResponse);
```

### Authentication
- JWT token management
- Secure route protection
- CSRF protection
- XSS prevention

## 🧪 Testing

### Test Commands
```bash
npm run test              # Unit tests
npm run test:coverage     # Coverage report
npm run test:e2e          # End-to-end tests
```

### Testing Strategy
- **Unit**: Component isolation testing
- **Integration**: API communication testing
- **E2E**: User journey testing
- **Mobile**: Touch interaction testing

## 🌐 Deployment

### AWS Infrastructure
```bash
# Build and deploy
npm run build
aws s3 sync dist/ s3://hokm-frontend-bucket/
aws cloudfront create-invalidation --distribution-id XXXXX --paths "/*"
```

### CI/CD Pipeline
1. **Build**: Vite production build
2. **Test**: Automated test suite  
3. **Deploy**: S3 sync + CloudFront invalidation
4. **Monitor**: Performance and error tracking

## 📚 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: Detailed technical architecture
- **[API.md](./API.md)**: API integration documentation
- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Deployment procedures

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main`
2. Implement changes with tests
3. Run `npm run lint` and `npm run test`
4. Submit pull request with description

### Code Standards
- **TypeScript**: Strict type checking
- **ESLint**: Airbnb configuration
- **Prettier**: Consistent formatting
- **Conventional Commits**: Semantic commit messages

## 🔧 Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+
- **Mobile**: iOS Safari 14+, Chrome Mobile 90+
- **Features**: ES2020, CSS Grid, Flexbox, PWA APIs

## 📞 Support

For technical issues or questions:
- Create GitHub issue with reproduction steps
- Include browser/device information
- Provide error messages and console logs

---

**Built with ❤️ for the Arabic legal community**
