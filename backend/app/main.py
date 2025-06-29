"""
Main FastAPI application with authentication system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.consultations import router as consultations_router

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    🇸🇦 استشارة قانونية ومالية وإدارية ذكية مبنية على القانون السعودي
    
    Professional Arabic Legal Assistant with:
    - User authentication and management
    - AI-powered legal consultations
    - Document export capabilities
    - Subscription management
    """,
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(consultations_router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "debug": settings.debug
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "مرحباً بك في المساعد القانوني الذكي",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "auth": "/api/auth",
            "users": "/api/users",
            "consultations": "/api/consultations"
        }
    }