from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv
from vanilla_ensemble import VanillaEnsemble
import asyncio
from datetime import datetime

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FastAPIServer')

app = FastAPI(title="Legal AI Vanilla Ensemble", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class EnsembleResponse(BaseModel):
    final_response: str
    processing_time_ms: int
    cost_estimate: float
    models_used: int
    judges_used: int
    components_extracted: int
    generation_responses: int = 0
    successful_generations: int = 0
    successful_evaluations: int = 0
    consensus_score: float = 0.0

ensemble = None

@app.on_event("startup")
async def startup_event():
    global ensemble
    logger.info("🚀 Starting FastAPI Legal AI Ensemble Server")
    
    required_keys = ['OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'GEMINI_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            missing_keys.append(key)
        else:
            logger.info(f"✅ {key}: {'*' * (len(value) - 10) + value[-10:]}")
    
    if missing_keys:
        logger.warning(f"⚠️ Missing API keys: {missing_keys}")
    
    try:
        ensemble = VanillaEnsemble()
        logger.info("✅ Vanilla Ensemble system initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ensemble: {e}")
        raise e

@app.get("/")
async def root():
    logger.info("📄 Serving test page")
    return FileResponse('test.html')

@app.get("/health")
async def health_check():
    logger.info("🏥 Health check requested")
    
    status = {
        "status": "healthy",
        "ensemble_ready": ensemble is not None,
        "api_keys_configured": {
            "openai": bool(os.getenv('OPENAI_API_KEY')),
            "deepseek": bool(os.getenv('DEEPSEEK_API_KEY')), 
            "gemini": bool(os.getenv('GEMINI_API_KEY'))
        }
    }
    
    logger.info(f"🏥 Health status: {status}")
    return status

@app.post("/ask", response_model=EnsembleResponse)
async def ask_question(request: QuestionRequest):
    logger.info("="*80)
    logger.info(f"📥 NEW REQUEST RECEIVED")
    logger.info(f"Question: {request.question}")
    logger.info(f"Request timestamp: {datetime.now().isoformat()}")
    logger.info("="*80)
    
    if not ensemble:
        logger.error("❌ Ensemble system not initialized")
        raise HTTPException(status_code=503, detail="Ensemble system not initialized")
    
    if not request.question.strip():
        logger.error("❌ Empty question received")
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        logger.info("🎯 Starting ensemble processing...")
        
        result = await ensemble.process_question(request.question)
        
        logger.info("="*80)
        logger.info(f"✅ REQUEST COMPLETED SUCCESSFULLY")
        logger.info(f"Processing time: {result['processing_time_ms']}ms")
        logger.info(f"Total cost: ${result['cost_estimate']}")
        logger.info(f"Models: {result['successful_generations']}/{result['generation_responses']}")
        logger.info(f"Judges: {result['successful_evaluations']}")
        logger.info(f"Response length: {len(result['final_response'])} characters")
        logger.info("="*80)
        
        return EnsembleResponse(**result)
        
    except Exception as e:
        logger.error("="*80)
        logger.error(f"❌ REQUEST FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("="*80)
        
        raise HTTPException(status_code=500, detail=f"Ensemble processing failed: {str(e)}")

@app.get("/logs")
async def get_recent_logs():
    logger.info("📋 Log access requested")
    
    try:
        log_files = [f for f in os.listdir('.') if f.startswith(('ensemble_', 'app_')) and f.endswith('.log')]
        
        if not log_files:
            return {"message": "No log files found"}
        
        latest_log = max(log_files, key=lambda f: os.path.getctime(f))
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-50:]
        
        logger.info(f"📋 Returning {len(recent_lines)} recent log lines from {latest_log}")
        
        return {
            "log_file": latest_log,
            "recent_lines": recent_lines,
            "total_lines": len(lines)
        }
        
    except Exception as e:
        logger.error(f"❌ Error reading logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")

@app.get("/stats")
async def get_stats():
    logger.info("📊 Stats requested")
    
    try:
        log_files = [f for f in os.listdir('.') if f.startswith(('ensemble_', 'app_')) and f.endswith('.log')]
        
        stats = {
            "log_files": len(log_files),
            "api_keys_status": {
                "openai": "configured" if os.getenv('OPENAI_API_KEY') else "missing",
                "deepseek": "configured" if os.getenv('DEEPSEEK_API_KEY') else "missing",
                "gemini": "configured" if os.getenv('GEMINI_API_KEY') else "missing"
            },
            "ensemble_status": "ready" if ensemble else "not_initialized"
        }
        
        if log_files:
            latest_log = max(log_files, key=lambda f: os.path.getctime(f))
            stats["latest_log"] = latest_log
            stats["latest_log_size"] = os.path.getsize(latest_log)
        
        logger.info(f"📊 Stats: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🌟 Starting server directly...")
    logger.info("Access the application at: http://localhost:8003")
    logger.info("API docs at: http://localhost:8003/docs")
    logger.info("Health check at: http://localhost:8003/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")