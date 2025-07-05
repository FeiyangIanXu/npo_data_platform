import sqlite3
import os

def init_database():
    """
    初始化数据库，创建 users 表（如果不存在）
    """
    # 数据库文件路径
    db_path = 'irs.db'
    
    try:
        # 连接到数据库（如果不存在会自动创建）
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 users 表是否已存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # 创建 users 表
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)
            
            # 提交更改
            conn.commit()
            print("[OK] users 表已创建")
        else:
            print("[OK] users 表已存在")
        
        # 关闭数据库连接
        conn.close()
        
    except sqlite3.Error as e:
        print(f"[ERROR] 数据库操作出错: {e}")
    except Exception as e:
        print(f"[ERROR] 发生错误: {e}")

if __name__ == "__main__":
    init_database()
