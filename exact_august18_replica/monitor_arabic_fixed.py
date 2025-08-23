#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arabic-friendly monitoring for Quranic embedding process
Properly handles Arabic text display and direction
"""
import time
import sqlite3
import subprocess
import os
from datetime import datetime
import json
import sys

# Ensure UTF-8 encoding
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Try to import arabic text processing
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("Installing Arabic text support...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "arabic-reshaper", "python-bidi"])
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True

def fix_arabic_text(text):
    """Fix Arabic text for proper terminal display"""
    if not text or not ARABIC_SUPPORT:
        return text
    
    try:
        # Reshape Arabic text (connect letters)
        reshaped_text = arabic_reshaper.reshape(text)
        # Apply bidirectional algorithm
        display_text = get_display(reshaped_text)
        return display_text
    except:
        return text

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
        
        # Get latest verse with Arabic name
        cursor.execute("SELECT surah_name, ayah_number, created_at FROM quranic_verses ORDER BY created_at DESC LIMIT 1")
        latest = cursor.fetchone()
        
        # Get total cost
        cursor.execute("SELECT SUM(cost) FROM quranic_verses")
        total_cost = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        latest_verse = ""
        if latest:
            surah_name = fix_arabic_text(latest[0]) if latest[0] else "Unknown"
            latest_verse = f"{surah_name}:{latest[1]}"
        
        return {
            "verses": verses_count,
            "chunks": chunks_count,
            "latest_verse": latest_verse,
            "latest_time": latest[2] if latest else "Never",
            "total_cost": round(total_cost, 4),
            "status": "Active"
        }
    except Exception as e:
        return {"error": str(e), "status": "Database error"}

def get_recent_verses(limit=3):
    """Get recent verses with proper Arabic display"""
    db_path = "data/quranic_foundations.db"
    
    if not os.path.exists(db_path):
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT surah_name, ayah_number, created_at 
            FROM quranic_verses 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        formatted_results = []
        for row in results:
            surah_name = fix_arabic_text(row[0]) if row[0] else "Unknown"
            formatted_results.append({
                "verse": f"{surah_name}:{row[1]}",
                "time": row[2]
            })
        
        return formatted_results
    except:
        return []

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
                eta_str = f"{eta_hours/24:.1f} أيام"
            elif eta_hours > 1:
                eta_str = f"{eta_hours:.1f} ساعات"
            else:
                eta_str = f"{eta_minutes:.0f} دقائق"
        else:
            eta_str = "جاري الحساب..."
            rate_per_min = 0
    except:
        eta_str = "غير معروف"
        rate_per_min = 0
    
    return {
        "progress": progress_percent,
        "eta": fix_arabic_text(eta_str),
        "rate": rate_per_min
    }

def check_for_errors():
    """Check recent log entries for errors"""
    log_path = "logs/quranic_embedding.log"
    
    if not os.path.exists(log_path):
        return {"error_count": 0, "last_error": ""}
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        recent_lines = lines[-50:]
        
        error_count = sum(1 for line in recent_lines if "ERROR" in line)
        
        # Get last error (without Arabic to avoid display issues)
        last_error = ""
        for line in reversed(recent_lines):
            if "ERROR" in line and "Failed to process verse" in line:
                last_error = "Failed to process verse (see log for details)"
                break
            elif "ERROR" in line:
                # Extract English part only
                if "Failed to generate embeddings" in line:
                    last_error = "Failed to generate embeddings"
                elif "Token limit exceeded" in line:
                    last_error = "Token limit exceeded"
                else:
                    last_error = "Processing error"
                break
        
        return {"error_count": error_count, "last_error": last_error}
    except:
        return {"error_count": -1, "last_error": "Cannot read log"}

def print_arabic_header():
    """Print header with Arabic support"""
    header = fix_arabic_text("مراقب معالجة القرآن الكريم")
    print("🕌 " + header)
    print("=" * 70)

def main():
    """Main monitoring loop with Arabic support"""
    
    # Set terminal to UTF-8
    os.system('export LANG=en_US.UTF-8')
    
    while True:
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print_arabic_header()
        print(f"⏰ وقت المراقبة: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Check process status
        is_running = get_process_status()
        status_text = fix_arabic_text("يعمل") if is_running else fix_arabic_text("متوقف")
        status_icon = "🟢" if is_running else "🔴"
        print(f"{status_icon} حالة العملية: {status_text}")
        
        # Get database stats
        db_stats = get_database_stats()
        processed_text = fix_arabic_text("الآيات المعالجة")
        chunks_text = fix_arabic_text("القطع المنشأة")
        cost_text = fix_arabic_text("التكلفة الإجمالية")
        
        print(f"📊 {processed_text}: {db_stats.get('verses', 0)}/3870")
        print(f"📦 {chunks_text}: {db_stats.get('chunks', 0)}")
        print(f"💰 {cost_text}: ${db_stats.get('total_cost', 0.0):.4f}")
        
        if db_stats.get('latest_verse'):
            latest_text = fix_arabic_text("آخر آية")
            print(f"📄 {latest_text}: {db_stats['latest_verse']}")
            time_text = fix_arabic_text("آخر تحديث")
            print(f"⏰ {time_text}: {db_stats['latest_time']}")
        
        # Progress calculation
        progress = calculate_progress()
        progress_text = fix_arabic_text("التقدم")
        rate_text = fix_arabic_text("المعدل")
        eta_text = fix_arabic_text("الوقت المتبقي")
        
        print(f"📈 {progress_text}: {progress['progress']:.1f}%")
        print(f"⚡ {rate_text}: {progress['rate']:.1f} آيات/10دقائق")
        print(f"🎯 {eta_text}: {progress['eta']}")
        
        print("\n" + "=" * 70)
        
        # Recent verses
        recent_text = fix_arabic_text("الآيات الأخيرة المعالجة")
        print(f"📝 {recent_text}:")
        recent_verses = get_recent_verses(3)
        for verse in recent_verses:
            print(f"   ✅ {verse['verse']} - {verse['time']}")
        
        # Error summary
        errors = check_for_errors()
        error_text = fix_arabic_text("الأخطاء الحديثة")
        print(f"\n⚠️ {error_text}: {errors.get('error_count', 0)}")
        if errors.get('last_error'):
            print(f"   آخر خطأ: {errors['last_error']}")
        
        print("\n" + "=" * 70)
        
        # Status alerts
        if not is_running and db_stats.get('verses', 0) < 3870:
            alert_text = fix_arabic_text("تنبيه: توقفت العملية قبل الانتهاء!")
            print(f"🚨 {alert_text}")
        
        if db_stats.get('total_cost', 0) > 1.5:
            cost_alert = fix_arabic_text("تحذير: التكلفة تقترب من الحد الأقصى!")
            print(f"💸 {cost_alert}")
        
        if db_stats.get('verses', 0) == 3870:
            success_text = fix_arabic_text("تم الانتهاء من معالجة جميع الآيات!")
            print(f"🎉 {success_text}")
            break
        
        update_text = fix_arabic_text("التحديث كل 30 ثانية... اضغط Ctrl+C للخروج")
        print(f"\n{update_text}")
        
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            exit_text = fix_arabic_text("تم إيقاف المراقبة.")
            print(f"\n👋 {exit_text}")
            break

if __name__ == "__main__":
    # Install required packages if not available
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
    except ImportError:
        print("Installing Arabic text support packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "arabic-reshaper", "python-bidi"])
        print("Packages installed. Restarting monitor...")
        import arabic_reshaper
        from bidi.algorithm import get_display
    
    main()