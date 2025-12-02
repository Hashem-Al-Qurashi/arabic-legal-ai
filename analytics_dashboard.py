"""Simple Analytics Dashboard - No AI needed, just basic counting!"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import hashlib

class QuestionAnalytics:
    def __init__(self, db_path="questions.db"):
        self.conn = sqlite3.connect(db_path)
        self.setup_database()
    
    def setup_database(self):
        """Create tables to track questions"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT,
                original_question TEXT,
                normalized_question TEXT,
                response TEXT,
                cost REAL,
                processing_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                count INTEGER DEFAULT 1
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS question_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cache_hit BOOLEAN,
                user_ip TEXT
            )
        """)
        self.conn.commit()
    
    def log_question(self, question, response, cost, time_ms, cache_hit=False):
        """Log every question asked"""
        # Normalize for matching similar questions
        normalized = self.normalize_question(question)
        cache_key = hashlib.md5(normalized.encode()).hexdigest()
        
        # Log this request
        self.conn.execute("""
            INSERT INTO question_logs (cache_key, cache_hit)
            VALUES (?, ?)
        """, (cache_key, cache_hit))
        
        if not cache_hit:
            # First time seeing this question - store it
            self.conn.execute("""
                INSERT INTO questions (cache_key, original_question, normalized_question, response, cost, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cache_key, question, normalized, json.dumps(response), cost, time_ms))
        else:
            # Seen before - increment counter
            self.conn.execute("""
                UPDATE questions 
                SET count = count + 1 
                WHERE cache_key = ?
            """, (cache_key,))
        
        self.conn.commit()
    
    def normalize_question(self, question):
        """Simple normalization - no AI needed!"""
        normalized = question.lower().strip()
        # Remove common variations
        normalized = normalized.replace("؟", "")
        normalized = normalized.replace("?", "")
        normalized = normalized.replace("ما هي", "")
        normalized = normalized.replace("ما هو", "")
        normalized = normalized.replace("كيف", "")
        normalized = normalized.replace("من فضلك", "")
        normalized = normalized.replace("أريد أن أعرف", "")
        return normalized
    
    def get_top_questions(self, limit=100):
        """Get most asked questions - SIMPLE SQL!"""
        cursor = self.conn.execute("""
            SELECT 
                original_question,
                COUNT(l.id) as total_asks,
                q.cost,
                q.processing_time_ms,
                q.created_at
            FROM questions q
            JOIN question_logs l ON q.cache_key = l.cache_key
            GROUP BY q.cache_key
            ORDER BY total_asks DESC
            LIMIT ?
        """, (limit,))
        
        return cursor.fetchall()
    
    def get_dashboard_stats(self):
        """Get stats for monitoring - NO AI, just SQL!"""
        stats = {}
        
        # Total questions asked
        stats['total_requests'] = self.conn.execute(
            "SELECT COUNT(*) FROM question_logs"
        ).fetchone()[0]
        
        # Unique questions
        stats['unique_questions'] = self.conn.execute(
            "SELECT COUNT(DISTINCT cache_key) FROM questions"
        ).fetchone()[0]
        
        # Cache hit rate
        cache_hits = self.conn.execute(
            "SELECT COUNT(*) FROM question_logs WHERE cache_hit = 1"
        ).fetchone()[0]
        stats['cache_hit_rate'] = (cache_hits / stats['total_requests'] * 100) if stats['total_requests'] > 0 else 0
        
        # Cost saved by caching
        stats['cost_saved'] = self.conn.execute("""
            SELECT SUM(q.cost * (l.hit_count - 1))
            FROM questions q
            JOIN (
                SELECT cache_key, COUNT(*) as hit_count
                FROM question_logs
                WHERE cache_hit = 1
                GROUP BY cache_key
            ) l ON q.cache_key = l.cache_key
        """).fetchone()[0] or 0
        
        # Questions today
        stats['questions_today'] = self.conn.execute("""
            SELECT COUNT(*) FROM question_logs
            WHERE DATE(timestamp) = DATE('now')
        """).fetchone()[0]
        
        # Top categories (simple keyword matching)
        all_questions = self.conn.execute(
            "SELECT original_question FROM questions"
        ).fetchall()
        
        categories = Counter()
        for (question,) in all_questions:
            if any(word in question for word in ["طلاق", "زواج", "حضانة", "نفقة"]):
                categories["Family Law"] += 1
            elif any(word in question for word in ["عمل", "راتب", "مكافأة", "فصل"]):
                categories["Labor Law"] += 1
            elif any(word in question for word in ["ضريبة", "زكاة", "VAT"]):
                categories["Tax Law"] += 1
            elif any(word in question for word in ["شركة", "تجارة", "عقد"]):
                categories["Commercial"] += 1
            elif any(word in question for word in ["جريمة", "سرقة", "عقوبة"]):
                categories["Criminal"] += 1
            else:
                categories["Other"] += 1
        
        stats['categories'] = dict(categories)
        
        return stats
    
    def print_daily_report(self):
        """Simple daily report - no AI needed!"""
        print("\n" + "="*60)
        print("📊 DAILY ANALYTICS REPORT")
        print("="*60)
        
        stats = self.get_dashboard_stats()
        
        print(f"\n📈 Overall Stats:")
        print(f"  Total Requests: {stats['total_requests']:,}")
        print(f"  Unique Questions: {stats['unique_questions']}")
        print(f"  Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
        print(f"  Money Saved: ${stats['cost_saved']:.2f}")
        print(f"  Questions Today: {stats['questions_today']}")
        
        print(f"\n📂 Categories:")
        for category, count in stats['categories'].items():
            print(f"  {category}: {count}")
        
        print(f"\n🏆 TOP 10 QUESTIONS:")
        print("-"*60)
        
        top_questions = self.get_top_questions(10)
        for i, (question, count, cost, time_ms, created) in enumerate(top_questions, 1):
            print(f"\n{i}. Asked {count} times")
            print(f"   Question: {question[:70]}...")
            print(f"   First asked: {created}")
            print(f"   Cost per query: ${cost:.3f}")
            saves = (count - 1) * cost
            print(f"   💰 Saved by caching: ${saves:.2f}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if stats['cache_hit_rate'] < 50:
            print("  ⚠️ Low cache hit rate - keep building cache")
        elif stats['cache_hit_rate'] < 80:
            print("  📈 Good progress - cache warming up")
        else:
            print("  ✅ Excellent cache performance!")
        
        # Questions needing optimization
        expensive_questions = self.conn.execute("""
            SELECT original_question, cost, COUNT(*) as asks
            FROM questions q
            JOIN question_logs l ON q.cache_key = l.cache_key
            WHERE cost > 0.02
            GROUP BY q.cache_key
            HAVING asks > 5
            ORDER BY asks DESC
            LIMIT 5
        """).fetchall()
        
        if expensive_questions:
            print("\n⚠️ Expensive questions to optimize:")
            for question, cost, asks in expensive_questions:
                print(f"  • {question[:50]}... (${cost:.3f} × {asks} = ${cost*asks:.2f})")

# Web dashboard endpoint
def create_web_dashboard():
    """Simple HTML dashboard - no framework needed!"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HOKM AI Analytics</title>
        <style>
            body { font-family: Arial; margin: 20px; background: #f5f5f5; }
            .card { background: white; padding: 20px; margin: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric { display: inline-block; margin: 10px 20px; }
            .metric-value { font-size: 32px; font-weight: bold; color: #2563eb; }
            .metric-label { color: #666; margin-top: 5px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; font-weight: 600; }
            .cache-hit { color: green; }
            .cache-miss { color: orange; }
        </style>
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(() => location.reload(), 30000);
        </script>
    </head>
    <body>
        <h1>🎯 HOKM AI Question Analytics</h1>
        
        <div class="card">
            <h2>📊 Real-Time Metrics</h2>
            <div class="metric">
                <div class="metric-value">{total_requests}</div>
                <div class="metric-label">Total Requests</div>
            </div>
            <div class="metric">
                <div class="metric-value">{unique_questions}</div>
                <div class="metric-label">Unique Questions</div>
            </div>
            <div class="metric">
                <div class="metric-value">{cache_hit_rate}%</div>
                <div class="metric-label">Cache Hit Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value">${cost_saved}</div>
                <div class="metric-label">Money Saved</div>
            </div>
        </div>
        
        <div class="card">
            <h2>🏆 Top 20 Questions</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Question</th>
                        <th>Times Asked</th>
                        <th>Cache Status</th>
                        <th>Savings</th>
                    </tr>
                </thead>
                <tbody>
                    {top_questions_rows}
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>📈 Hourly Trend (Last 24 Hours)</h2>
            <canvas id="trend"></canvas>
        </div>
        
        <p style="text-align: center; color: #666;">
            Auto-refreshes every 30 seconds | Last updated: {last_updated}
        </p>
    </body>
    </html>
    """
    
    return html_template

# FastAPI endpoint for monitoring
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
analytics = QuestionAnalytics()

@app.get("/analytics")
async def show_analytics():
    """Simple analytics page - no AI, just data!"""
    stats = analytics.get_dashboard_stats()
    top_questions = analytics.get_top_questions(20)
    
    # Generate HTML
    html = create_web_dashboard()
    
    # Fill in the data
    html = html.format(
        total_requests=f"{stats['total_requests']:,}",
        unique_questions=stats['unique_questions'],
        cache_hit_rate=f"{stats['cache_hit_rate']:.1f}",
        cost_saved=f"{stats['cost_saved']:.2f}",
        top_questions_rows=generate_table_rows(top_questions),
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    return HTMLResponse(html)

@app.get("/api/stats")
async def get_stats():
    """JSON API for monitoring tools"""
    return analytics.get_dashboard_stats()

# Integration with your ensemble
class MonitoredEnsemble:
    def __init__(self, ensemble, analytics):
        self.ensemble = ensemble
        self.analytics = analytics
        self.cache = {}
    
    async def process_question(self, question):
        """Process with automatic monitoring"""
        # Check cache
        cache_key = hashlib.md5(question.lower().encode()).hexdigest()
        
        if cache_key in self.cache:
            # Cache HIT!
            self.analytics.log_question(question, self.cache[cache_key], 0, 0, cache_hit=True)
            return self.cache[cache_key]
        
        # Cache MISS - generate response
        start_time = time.time()
        response = await self.ensemble.process_question(question)
        time_ms = int((time.time() - start_time) * 1000)
        
        # Store in cache
        self.cache[cache_key] = response
        
        # Log to analytics
        self.analytics.log_question(
            question, 
            response, 
            response.get('cost_estimate', 0.03),
            time_ms,
            cache_hit=False
        )
        
        return response

# Run daily report
if __name__ == "__main__":
    analytics = QuestionAnalytics()
    
    # Simulate some data for demo
    test_questions = [
        ("ما هي مكافأة نهاية الخدمة؟", 847),
        ("كيف احسب الزكاة؟", 623),
        ("ما هي شروط الحضانة؟", 456),
        ("ما عقوبة التهرب الضريبي؟", 234),
        ("كيف اطلق زوجتي؟", 198),
    ]
    
    for question, count in test_questions:
        for _ in range(count):
            analytics.log_question(question, {"response": "test"}, 0.03, 15000, cache_hit=(_ > 0))
    
    # Show report
    analytics.print_daily_report()