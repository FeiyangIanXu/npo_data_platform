import sqlite3
import os
from datetime import datetime
from config.database import get_database_path, get_backup_dir

class DatabaseManager:
    def __init__(self):
        self.db_path = get_database_path()
        self.backup_dir = get_backup_dir()

    def check_database(self):
        """检查数据库完整性"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查数据库是否可以正常打开和查询
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # 检查每个表的完整性
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table[0]})")
                if not cursor.fetchall():
                    return False, f"Table {table[0]} has no columns"
                
                # 尝试查询每个表
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                
            conn.close()
            return True, "Database check passed"
            
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"
        
    def backup_database(self):
        """创建数据库备份"""
        if not os.path.exists(self.db_path):
            return False, "Database file not found"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"irs_backup_{timestamp}.db")
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True, f"Backup created at {backup_path}"
        except Exception as e:
            return False, f"Backup failed: {str(e)}"
            
    def fix_database(self):
        """修复数据库问题"""
        success, message = self.check_database()
        if success:
            return True, "No fixes needed"
            
        # 先创建备份
        backup_success, backup_message = self.backup_database()
        if not backup_success:
            return False, f"Cannot proceed with fix: {backup_message}"
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 运行VACUUM来整理数据库文件
            cursor.execute("VACUUM")
            
            # 检查并修复索引
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            for index in indexes:
                cursor.execute(f"REINDEX {index[0]}")
                
            conn.commit()
            conn.close()
            
            return True, "Database fixed successfully"
            
        except sqlite3.Error as e:
            return False, f"Fix failed: {str(e)}"

def main():
    db_manager = DatabaseManager()
    
    # 检查数据库
    check_success, check_message = db_manager.check_database()
    print(f"Database check: {check_message}")
    
    if not check_success:
        # 如果检查失败，尝试修复
        fix_success, fix_message = db_manager.fix_database()
        print(f"Database fix attempt: {fix_message}")

if __name__ == "__main__":
    main()