#!/usr/bin/env python3
"""
Quick Fix Script for NPO Data Platform Issues
This script diagnoses and fixes common problems with login, registration, and data fetching.
"""

import os
import sys
import sqlite3
from pathlib import Path

def check_backend_directory():
    """Ensure we're running from the backend directory"""
    current_dir = Path.cwd()
    script_dir = Path(__file__).parent
    
    print(f"Current directory: {current_dir}")
    print(f"Script directory: {script_dir}")
    
    # Change to backend directory if not already there
    if current_dir != script_dir:
        os.chdir(script_dir)
        print(f"Changed to backend directory: {script_dir}")
    
    return script_dir

def check_requirements():
    """Check if required Python packages are installed"""
    print("\n=== Checking Python Requirements ===")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'passlib',
        'python-jose',
        'python-multipart'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Missing packages: {missing_packages}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def fix_database():
    """Initialize and fix database issues"""
    print("\n=== Fixing Database Issues ===")
    
    db_path = Path('irs.db')
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check and create users table
        print("Checking users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users table ready ({user_count} users)")
        
        # Check nonprofits table
        print("Checking nonprofits table...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='nonprofits'
        """)
        
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM nonprofits")
            nonprofit_count = cursor.fetchone()[0]
            print(f"✅ Nonprofits table exists ({nonprofit_count} records)")
            
            # Check for required columns
            cursor.execute("PRAGMA table_info(nonprofits)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ['fiscal_year', 'fiscal_month']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                print(f"⚠️ Missing columns: {missing_columns}")
                print("💡 You may need to run: python data_pipeline.py")
            else:
                print("✅ All required columns exist")
        else:
            print("❌ Nonprofits table missing")
            print("💡 Run: python data_pipeline.py")
        
        conn.commit()
        conn.close()
        print("✅ Database checks completed")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_backend_files():
    """Check if essential backend files exist"""
    print("\n=== Checking Backend Files ===")
    
    essential_files = [
        'main.py',
        'requirements.txt',
        'api/search.py',
        'api/filter.py',
        'api/export.py'
    ]
    
    missing_files = []
    
    for file_path in essential_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"💡 Missing files: {missing_files}")
        return False
    
    return True

def test_api_imports():
    """Test if API modules can be imported without errors"""
    print("\n=== Testing API Module Imports ===")
    
    try:
        # Test main imports
        from api.search import router as search_router
        print("✅ Search API module imported successfully")
        
        from api.filter import router as filter_router
        print("✅ Filter API module imported successfully")
        
        from api.export import router as export_router
        print("✅ Export API module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def provide_startup_instructions():
    """Provide instructions for starting the backend server"""
    print("\n=== Startup Instructions ===")
    print("To start the backend server, run:")
    print("  cd backend")
    print("  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\nOr use the start script:")
    print("  cd .. (to project root)")
    print("  start.bat")
    print("\nThe API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")

def main():
    """Main diagnostic and fix routine"""
    print("🔧 NPO Data Platform - Issue Diagnosis and Fix Tool")
    print("=" * 60)
    
    # Step 1: Ensure correct directory
    backend_dir = check_backend_directory()
    
    # Step 2: Check requirements
    requirements_ok = check_requirements()
    
    # Step 3: Check essential files
    files_ok = check_backend_files()
    
    # Step 4: Test imports
    imports_ok = test_api_imports()
    
    # Step 5: Fix database
    database_ok = fix_database()
    
    # Summary
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSIS SUMMARY")
    print("=" * 60)
    
    all_ok = requirements_ok and files_ok and imports_ok and database_ok
    
    if all_ok:
        print("✅ All checks passed! Your backend should work correctly.")
        print("\n💡 If you're still having issues:")
        print("   1. Make sure the backend server is running")
        print("   2. Check browser console for frontend errors")
        print("   3. Verify the frontend is connecting to http://localhost:8000")
    else:
        print("❌ Some issues were found. Please fix them before proceeding.")
        
        if not requirements_ok:
            print("   • Install missing Python packages")
        if not files_ok:
            print("   • Restore missing backend files")
        if not imports_ok:
            print("   • Fix API module import errors")
        if not database_ok:
            print("   • Run data pipeline to create nonprofits table")
    
    # Always provide startup instructions
    provide_startup_instructions()
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 