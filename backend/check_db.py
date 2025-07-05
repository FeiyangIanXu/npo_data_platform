import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()
        
        # 检查表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("数据库中的表:", tables)
        
        # 检查非营利组织数据
        if ('nonprofits',) in tables:
            cursor.execute("SELECT COUNT(*) FROM nonprofits")
            count = cursor.fetchone()[0]
            print(f"非营利组织记录数: {count}")
            
            # 显示前几条记录的结构
            cursor.execute("SELECT * FROM nonprofits LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                cursor.execute("PRAGMA table_info(nonprofits)")
                columns = cursor.fetchall()
                print(f"字段数: {len(columns)}")
                print("前几个字段:", [col[1] for col in columns[:5]])
        
        # 检查用户表
        if ('users',) in tables:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"用户数: {user_count}")
            
        conn.close()
        print("数据库检查完成")
        
    except Exception as e:
        print(f"数据库检查失败: {e}")

if __name__ == "__main__":
    check_database() 