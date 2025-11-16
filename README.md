# 🏛️ Legal AI Vanilla Ensemble System

A sophisticated ensemble system that combines 4 AI models with 3 judges to provide superior legal responses based on Saudi law, using pure vanilla generation without RAG or external context.

## 🎯 System Architecture

### Step 1: Multi-Model Vanilla Generation
- **4 Models**: GPT-4o, DeepSeek, Grok-2, Gemini-1.5-Flash
- Each model responds with pure vanilla legal knowledge
- No external context or RAG - just like using ChatGPT directly

### Step 2: Component Extraction by 3 Judges
- **3 Judges**: Claude-3.5-Sonnet, GPT-4o, Gemini-1.5-Flash
- Extract the BEST version of 7 components from all responses:
  - Direct Answer
  - Legal Foundation  
  - Article Citations
  - Numerical Examples
  - Step-by-Step Procedures
  - Edge Cases & Exceptions
  - Practical Advice

### Step 3: Consensus Voting
- Majority voting (2/3 judges) for each component
- Special rule: Take union of all cited articles
- Highest individual score used when no consensus

### Step 4: Response Assembly
- Combine winning components into coherent response
- AI adds smooth transitions between components
- Keep extracted text exactly as-is

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Edit `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key  
GEMINI_API_KEY=your_gemini_key
```

### 3. Run the Server
```bash
python app.py
```

### 4. Open the UI
Navigate to: http://localhost:8000

## 📊 System Features

### Comprehensive Logging
- **Real-time logs** for every step of processing
- **File logging** with timestamps for audit trails
- **Console output** for immediate feedback
- **Error tracking** with detailed error messages

### Monitoring Dashboard
- **Health checks** - API status and system readiness
- **Live logs** - Recent system activity in real-time
- **Statistics** - System performance and usage metrics
- **Cost tracking** - Per-request cost estimation

### Performance Metrics
- **Processing Time**: Typically 30-60 seconds
- **Cost per Query**: ~$0.29 (4 models + 3 judges + assembly)
- **Success Rate**: Tracked for each model and judge
- **Response Quality**: Consensus scoring system

## 🧪 Test Questions

Try these sample questions:
- `ما هي مدة الإجازة السنوية؟` (What is the annual leave duration?)
- `كيف أحسب مكافأة نهاية الخدمة؟` (How to calculate end-of-service gratuity?)
- `ما عقوبات التأخير عن العمل؟` (What are the penalties for work delays?)

## 📡 API Endpoints

### POST /ask
**Request:**
```json
{
  "question": "ما هي مدة الإجازة السنوية؟"
}
```

**Response:**
```json
{
  "final_response": "assembled response from best components",
  "processing_time_ms": 45000,
  "cost_estimate": 0.25,
  "models_used": 4,
  "judges_used": 3,
  "components_extracted": 7,
  "consensus_score": 8.5
}
```

### GET /health
Check system health and API key status

### GET /logs  
Get recent system logs for debugging

### GET /stats
Get system statistics and performance metrics

## 🔧 System Configuration

### Model Configuration
- **Generation Models**: 4 models for diverse perspectives
- **Judge Models**: 3 models for robust evaluation
- **Timeout**: 30 seconds per API call
- **Retries**: 3 attempts for failed calls

### Cost Optimization
- **Parallel Processing**: All API calls run simultaneously
- **Smart Fallbacks**: Graceful degradation when models fail
- **Cost Tracking**: Real-time cost estimation per request

### Error Handling
- **Robust Retries**: Automatic retry on temporary failures
- **Graceful Degradation**: Continue with available models
- **Detailed Logging**: Full error context for debugging

## 📁 Project Structure

```
legal_ai_ensemble/
├── vanilla_ensemble.py    # Core ensemble engine
├── app.py                # FastAPI server
├── test.html            # Web UI for testing
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── ensemble_*.log      # System logs
└── app_*.log          # Server logs
```

## 🔍 Logging Details

The system provides comprehensive logging at every step:

### Generation Phase
```
🤖 Calling OpenAI model: gpt-4o
✅ gpt-4o responded in 3.45s, cost: $0.0423
```

### Judging Phase  
```
⚖️ Judge evaluation with gpt-4o
✅ gpt-4o: Score 8.5, $0.0234, 2.1s
```

### Consensus Voting
```
🗳️ Computing consensus from 3 judges
📊 Voting for component: direct_answer
✅ direct_answer: Winner selected (score: 8.5)
```

### Final Assembly
```
🔧 Starting Step 4: Response Assembly
✅ Step 4 Complete: Response assembled in 1.23s, cost: $0.02
```

## 💡 Key Benefits

1. **Superior Quality**: Ensemble approach beats any single model
2. **Robust Processing**: Continues even if some models fail
3. **Full Transparency**: Complete logging of every step
4. **Cost Effective**: ~$0.29 per comprehensive legal analysis
5. **Saudi Law Focus**: Specialized for Saudi legal framework
6. **No Dependencies**: Pure vanilla generation without external data

## 🛠️ Troubleshooting

### Check API Keys
```bash
curl http://localhost:8000/health
```

### View Recent Logs
```bash
curl http://localhost:8000/logs
```

### Monitor Performance
```bash
curl http://localhost:8000/stats
```

### Common Issues
- **Slow responses**: Normal for ensemble processing (30-60s)
- **Model failures**: Check logs for specific API errors
- **Cost concerns**: Monitor `/stats` endpoint for usage tracking

---

**Note**: This system focuses on vanilla AI generation without RAG or external context, making it a pure test of ensemble methodology for legal AI applications.