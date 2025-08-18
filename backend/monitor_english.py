#!/usr/bin/env python3
"""
English-only monitoring for Quranic embedding process
No Arabic text issues in terminal
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
        
        # Get latest verse (show only reference number)
        cursor.execute("SELECT surah_number, ayah_number, created_at FROM quranic_verses ORDER BY created_at DESC LIMIT 1")
        latest = cursor.fetchone()
        
        # Get total cost
        cursor.execute("SELECT SUM(cost) FROM quranic_verses")
        total_cost = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "verses": verses_count,
            "chunks": chunks_count,
            "latest_verse": f"Surah {latest[0]}:{latest[1]}" if latest else "None",
            "latest_time": latest[2] if latest else "Never",
            "total_cost": round(total_cost, 4),
            "status": "Active"
        }
    except Exception as e:
        return {"error": str(e), "status": "Database error"}

def get_log_summary():
    """Get summary of recent log activity (English only)"""
    log_path = "logs/quranic_embedding.log"
    
    if not os.path.exists(log_path):
        return {"status": "No log file", "recent_activity": "None"}
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_lines = lines[-20:]
        
        # Count recent activity
        successful_embeddings = sum(1 for line in recent_lines if "Generated embedding" in line)
        failed_processes = sum(1 for line in recent_lines if "Failed to process verse" in line)
        checkpoints = sum(1 for line in recent_lines if "Checkpoint saved" in line)
        
        # Get last meaningful activity
        last_activity = "Unknown"
        for line in reversed(recent_lines):
            if any(keyword in line for keyword in ["Processing batch", "Checkpoint saved", "Generated embedding"]):
                # Extract English parts only
                if "Processing batch" in line:
                    last_activity = "Processing new batch"
                elif "Checkpoint saved" in line:
                    last_activity = "Checkpoint saved"
                elif "Generated embedding" in line:
                    last_activity = "Generating embeddings"
                break
        
        return {
            "status": "Active",
            "successful_embeddings": successful_embeddings,
            "failed_processes": failed_processes,
            "checkpoints": checkpoints,
            "last_activity": last_activity
        }
    except Exception as e:
        return {"status": f"Error: {e}", "recent_activity": "Error reading log"}

def check_for_errors():
    """Check recent log entries for errors (count only)"""
    log_path = "logs/quranic_embedding.log"
    
    if not os.path.exists(log_path):
        return {"error_count": 0, "critical_errors": 0}
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_lines = lines[-50:]
        
        error_count = sum(1 for line in recent_lines if "ERROR" in line)
        critical_count = sum(1 for line in recent_lines if any(word in line for word in ["CRITICAL", "Budget limit", "All services failed"]))
        
        return {"error_count": error_count, "critical_errors": critical_count}
    except:
        return {"error_count": -1, "critical_errors": -1}

def calculate_progress():
    """Calculate estimated progress and completion time"""
    stats = get_database_stats()
    
    if stats.get("verses", 0) == 0:
        return {"progress": 0.0, "eta": "Unknown", "rate": 0.0}
    
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
            eta_str = "Calculating..."
            rate_per_min = 0
    except:
        eta_str = "Unknown"
        rate_per_min = 0
    
    return {
        "progress": progress_percent,
        "eta": eta_str,
        "rate": rate_per_min
    }

def main():
    """Main monitoring loop"""
    print("QURANIC EMBEDDING MONITOR")
    print("=" * 60)
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"Monitor Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Check process status
        is_running = get_process_status()
        status_icon = "[RUNNING]" if is_running else "[STOPPED]"
        print(f"Process Status: {status_icon}")
        
        # Get database stats
        db_stats = get_database_stats()
        print(f"Verses Processed: {db_stats.get('verses', 0)}/3870")
        print(f"Chunks Created: {db_stats.get('chunks', 0)}")
        print(f"Total Cost: ${db_stats.get('total_cost', 0.0):.4f}")
        
        if db_stats.get('latest_verse'):
            print(f"Latest Verse: {db_stats['latest_verse']}")
            print(f"Last Update: {db_stats['latest_time']}")
        
        # Progress calculation
        progress = calculate_progress()
        print(f"Progress: {progress['progress']:.1f}%")
        print(f"Rate: {progress['rate']:.1f} verses/10min")
        print(f"ETA: {progress['eta']}")
        
        print("\n" + "-" * 60)
        
        # Log summary
        log_summary = get_log_summary()
        print("RECENT ACTIVITY:")
        print(f"  Last Action: {log_summary.get('last_activity', 'Unknown')}")
        print(f"  Successful Embeddings: {log_summary.get('successful_embeddings', 0)}")
        print(f"  Failed Processes: {log_summary.get('failed_processes', 0)}")
        print(f"  Checkpoints: {log_summary.get('checkpoints', 0)}")
        
        # Error summary
        errors = check_for_errors()
        print(f"\nERROR SUMMARY:")
        print(f"  Recent Errors: {errors.get('error_count', 0)}")
        print(f"  Critical Issues: {errors.get('critical_errors', 0)}")
        
        print("\n" + "=" * 60)
        
        # Status indicators
        if not is_running and db_stats.get('verses', 0) < 3870:
            print("ALERT: Process stopped before completion!")
            print("Run: python3 quranic_embedding_processor.py --resume <session_id>")
        
        if db_stats.get('total_cost', 0) > 1.5:
            print("WARNING: Cost approaching budget limit!")
        
        if errors.get('critical_errors', 0) > 0:
            print("CRITICAL: System has critical errors!")
        
        if db_stats.get('verses', 0) == 3870:
            print("SUCCESS: All verses processed successfully!")
            print("Total Cost: $" + str(db_stats.get('total_cost', 0)))
            print("Process completed!")
            break
        
        print("\nUpdating every 30 seconds... Press Ctrl+C to exit")
        
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nMonitor stopped.")
            break

if __name__ == "__main__":
    main()