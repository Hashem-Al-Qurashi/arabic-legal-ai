"""
Setup Islamic System
One-click setup for Islamic legal integration
"""
import asyncio
import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def install_dependencies():
    """Install required dependencies for Islamic system"""
    logger.info("📦 Installing dependencies...")
    
    dependencies = [
        "datasets",  # HuggingFace datasets
        "sentence-transformers",  # For embeddings
        "numpy",  # For vector operations
    ]
    
    for dep in dependencies:
        try:
            logger.info(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            logger.info(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True


def create_data_directories():
    """Create necessary data directories"""
    logger.info("📁 Creating data directories...")
    
    directories = [
        "data",
        "data/islamic",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(exist_ok=True)
        logger.info(f"✅ Created directory: {directory}")


def setup_environment_variables():
    """Setup environment variables for Islamic system"""
    logger.info("⚙️ Setting up environment variables...")
    
    env_vars = {
        "ENABLE_ISLAMIC_SOURCES": "true",
        "ISLAMIC_MAX_RESULTS": "3",
        "ISLAMIC_THRESHOLD": "0.5",
        "ISLAMIC_TIMEOUT": "2000"
    }
    
    env_file = Path(".env")
    
    # Read existing .env file
    existing_vars = {}
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    existing_vars[key] = value
    
    # Add new variables
    for key, value in env_vars.items():
        if key not in existing_vars:
            existing_vars[key] = value
            logger.info(f"✅ Added {key}={value}")
    
    # Write back to .env file
    with open(env_file, 'w', encoding='utf-8') as f:
        for key, value in existing_vars.items():
            f.write(f"{key}={value}\n")
    
    logger.info("✅ Environment variables configured")


async def build_islamic_database():
    """Build the Islamic database from Al-Qurtubi dataset"""
    logger.info("🕌 Building Islamic database...")
    
    try:
        # Import and run the processor
        from islamic_data_processor import build_islamic_database
        
        success = await build_islamic_database()
        
        if success:
            logger.info("✅ Islamic database built successfully!")
            return True
        else:
            logger.error("❌ Failed to build Islamic database")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Failed to import Islamic processor: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to build Islamic database: {e}")
        return False


async def test_islamic_system():
    """Test the Islamic system integration"""
    logger.info("🧪 Testing Islamic system integration...")
    
    try:
        from enhanced_rag_engine import process_query_enhanced, health_check_enhanced
        
        # Test queries
        test_queries = [
            "ما أحكام الميراث؟",  # Should include Islamic
            "كيف أقدم طلب للمحكمة؟"  # Should NOT include Islamic
        ]
        
        for query in test_queries:
            logger.info(f"Testing: {query}")
            result = await process_query_enhanced(query)
            
            has_islamic = result.get('has_islamic_context', False)
            processing_time = result.get('processing_time_ms', 0)
            
            logger.info(f"  ✅ Islamic context: {has_islamic}, Time: {processing_time}ms")
        
        # Health check
        health = await health_check_enhanced()
        logger.info(f"🏥 Health check: {health.get('enhanced_rag', {}).get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        return False


async def main():
    """Main setup function"""
    logger.info("🚀 Starting Islamic System Setup...")
    
    # Step 1: Install dependencies
    if not install_dependencies():
        logger.error("❌ Dependency installation failed")
        return False
    
    # Step 2: Create directories
    create_data_directories()
    
    # Step 3: Setup environment
    setup_environment_variables()
    
    # Step 4: Build Islamic database
    logger.info("⏳ Building Islamic database (this may take a few minutes)...")
    if not await build_islamic_database():
        logger.error("❌ Islamic database build failed")
        return False
    
    # Step 5: Test system
    if not await test_islamic_system():
        logger.error("❌ System testing failed")
        return False
    
    logger.info("🎉 Islamic System Setup Complete!")
    logger.info("""
📋 Setup Summary:
✅ Dependencies installed
✅ Directories created  
✅ Environment configured
✅ Islamic database built
✅ System tested

🚀 Your system is now ready with Islamic legal integration!

To use the enhanced system:
1. Set ENABLE_ISLAMIC_SOURCES=true in your .env file (already done)
2. Use enhanced_rag_engine.process_query_enhanced() instead of regular RAG
3. Islamic sources will automatically be included for relevant queries

🔧 Configuration:
- Islamic sources: ENABLED
- Max Islamic results: 3 per query
- Relevance threshold: 0.5
- Timeout: 2 seconds
""")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)