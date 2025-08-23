#!/usr/bin/env python3
"""
Real-time monitoring for Quranic embedding process
"""
import time
import sqlite3
import subprocess
import os
from datetime import datetime
import json

def get_process_status():
    """Check if the embedding process is running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'quranic_embedding_processor'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def get_database_stats():
    """Get current database statistics"""
    db_path = "data/quranic_foundations.db"
    
    if not os.path.exists(db_path):
        return {"verses": 0, "chunks": 0, "status": "No database yet"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count verses
        cursor.execute("SELECT COUNT(*) FROM quranic_verses")
        verses_count = cursor.fetchone()[0]
        
        # Count chunks
        cursor.execute("SELECT COUNT(*) FROM tafseer_chunks")
        chunks_count = cursor.fetchone()[0]
        
        # Get latest verse
        cursor.execute("SELECT verse_reference, created_at FROM quranic_verses ORDER BY created_at DESC LIMIT 1")
        latest = cursor.fetchone()
        
        # Get total cost
        cursor.execute("SELECT SUM(cost) FROM quranic_verses")
        total_cost = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "verses": verses_count,
            "chunks": chunks_count,
            "latest_verse": latest[0] if latest else "None",
            "latest_time": latest[1] if latest else "Never",
            "total_cost": round(total_cost, 4),
            "status": "Active"
        }
    except Exception as e:
        return {"error": str(e), "status": "Database error"}

def get_log_tail(lines=5):
    """Get last few lines of log file"""
    log_path = "logs/quranic_embedding.log"
    
    if not os.path.exists(log_path):
        return ["No log file found"]
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return [line.strip() for line in all_lines[-lines:]]
    except Exception as e:
        return [f"Error reading log: {e}"]

def check_for_errors():
    """Check recent log entries for errors"""
    log_path = "logs/quranic_embedding.log"
    
    if not os.path.exists(log_path):
        return []
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Look for errors in last 50 lines
        recent_lines = lines[-50:]
        errors = []
        
        for line in recent_lines:
            if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception', 'critical']):
                errors.append(line.strip())
        
        return errors[-5:]  # Last 5 errors
    except:
        return ["Could not check for errors"]

def calculate_progress():
    """Calculate estimated progress and completion time"""
    stats = get_database_stats()
    
    if stats.get("verses", 0) == 0:
        return {"progress": "0%", "eta": "Unknown", "rate": "0 verses/min"}
    
    total_verses = 3870
    completed = stats["verses"]
    progress_percent = (completed / total_verses) * 100
    
    # Estimate rate from recent activity
    try:
        conn = sqlite3.connect("data/quranic_foundations.db")
        cursor = conn.cursor()
        
        # Get verses processed in last 10 minutes
        cursor.execute("""
            SELECT COUNT(*) FROM quranic_verses 
            WHERE datetime(created_at) > datetime('now', '-10 minutes')
        """)
        recent_count = cursor.fetchone()[0]
        
        conn.close()
        
        rate_per_min = recent_count  # 10-minute window
        
        if rate_per_min > 0:
            remaining_verses = total_verses - completed
            eta_minutes = remaining_verses / rate_per_min
            eta_hours = eta_minutes / 60
            
            if eta_hours > 24:
                eta_str = f"{eta_hours/24:.1f} days"
            elif eta_hours > 1:
                eta_str = f"{eta_hours:.1f} hours"
            else:
                eta_str = f"{eta_minutes:.0f} minutes"
        else:
            eta_str = "Unknown"
            rate_per_min = 0
    except:
        eta_str = "Unknown"
        rate_per_min = 0
    
    return {
        "progress": f"{progress_percent:.1f}%",
        "eta": eta_str,
        "rate": f"{rate_per_min:.1f} verses/10min"
    }

def main():
    """Main monitoring loop"""
    print("🕌 Quranic Embedding Monitor")
    print("=" * 50)
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"🕒 Monitor Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Check process status
        is_running = get_process_status()
        status_icon = "🟢" if is_running else "🔴"
        print(f"{status_icon} Process Status: {'RUNNING' if is_running else 'STOPPED'}")
        
        # Get database stats
        db_stats = get_database_stats()
        print(f"📊 Verses Processed: {db_stats.get('verses', 0)}/3870")
        print(f"📦 Chunks Created: {db_stats.get('chunks', 0)}")
        print(f"💰 Total Cost: ${db_stats.get('total_cost', 0.0):.4f}")
        
        if db_stats.get('latest_verse'):
            print(f"📄 Latest Verse: {db_stats['latest_verse']}")
            print(f"⏰ Last Update: {db_stats['latest_time']}")
        
        # Progress calculation
        progress = calculate_progress()
        print(f"📈 Progress: {progress['progress']}")
        print(f"⚡ Rate: {progress['rate']}")
        print(f"🎯 ETA: {progress['eta']}")
        
        print("\n" + "=" * 50)
        
        # Check for recent errors
        errors = check_for_errors()
        if errors:
            print("⚠️  RECENT ERRORS:")
            for error in errors:
                print(f"   {error}")
        else:
            print("✅ No recent errors")
        
        print("\n" + "=" * 50)
        print("📝 RECENT LOG ENTRIES:")
        recent_logs = get_log_tail(3)
        for log in recent_logs:
            print(f"   {log}")
        
        print("\n" + "=" * 50)
        
        # Alert conditions
        if not is_running and db_stats.get('verses', 0) < 3870:
            print("🚨 ALERT: Process stopped before completion!")
            print("   Run this to resume:")
            print("   python3 quranic_embedding_processor.py --resume <session_id>")
        
        if db_stats.get('total_cost', 0) > 1.5:
            print("💸 ALERT: Cost approaching budget limit!")
        
        if db_stats.get('verses', 0) == 3870:
            print("🎉 COMPLETED: All verses processed!")
            break
        
        print("\nPress Ctrl+C to exit monitor...")
        
        try:
            time.sleep(30)  # Update every 30 seconds
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped.")
            break

if __name__ == "__main__":
    main()