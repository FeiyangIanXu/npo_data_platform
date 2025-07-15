import sqlite3
import os

def init_database():
    """
    Initialize database and create users table if it doesn't exist
    """
    # Database file path - use absolute path to ensure it's in backend directory
    import os
    db_path = os.path.join(os.path.dirname(__file__), 'irs.db')
    
    try:
        # Connect to database (creates if doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create users table
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Commit changes
            conn.commit()
            print("[OK] Users table created successfully")
        else:
            print("[OK] Users table already exists")
        
        # Check if nonprofits table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='nonprofits'
        """)
        
        nonprofits_exists = cursor.fetchone() is not None
        
        if nonprofits_exists:
            print("[OK] Nonprofits table exists")
            
            # Check if data exists
            cursor.execute("SELECT COUNT(*) FROM nonprofits")
            count = cursor.fetchone()[0]
            print(f"[INFO] Nonprofits table contains {count} records")
            
            # Check for required columns
            cursor.execute("PRAGMA table_info(nonprofits)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ['fiscal_year', 'fiscal_month']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"[WARNING] Missing standardized columns: {missing_columns}")
                print("[INFO] You may need to run the data pipeline to create standardized columns")
            else:
                print("[OK] All required standardized columns exist")
        else:
            print("[WARNING] Nonprofits table doesn't exist")
            print("[INFO] Please run the data pipeline (data_pipeline.py) to create and populate the nonprofits table")
        
        # Close database connection
        conn.close()
        print(f"[OK] Database initialized at: {db_path}")
        
    except sqlite3.Error as e:
        print(f"[ERROR] Database operation failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        return False
    
    return True

def check_database_health():
    """
    Perform a health check on the database
    """
    db_path = os.path.join(os.path.dirname(__file__), 'irs.db')
    
    if not os.path.exists(db_path):
        print(f"[ERROR] Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic connectivity
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("[OK] Database connectivity test passed")
        else:
            print("[ERROR] Database connectivity test failed")
            conn.close()
            return False
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"[INFO] Available tables: {tables}")
        
        # Test users table
        if 'users' in tables:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"[INFO] Users table: {user_count} records")
        else:
            print("[WARNING] Users table missing")
        
        # Test nonprofits table
        if 'nonprofits' in tables:
            cursor.execute("SELECT COUNT(*) FROM nonprofits")
            nonprofit_count = cursor.fetchone()[0]
            print(f"[INFO] Nonprofits table: {nonprofit_count} records")
        else:
            print("[WARNING] Nonprofits table missing")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Database Initialization ===")
    success = init_database()
    
    if success:
        print("\n=== Database Health Check ===")
        check_database_health()
    else:
        print("[ERROR] Database initialization failed")
