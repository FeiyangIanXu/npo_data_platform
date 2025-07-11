import os

# 数据库配置
DATABASE_CONFIG = {
    'path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'irs.db'),
    'backup_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'backups'),
}

# 确保备份目录存在
os.makedirs(DATABASE_CONFIG['backup_dir'], exist_ok=True)

def get_database_path():
    """获取数据库文件路径"""
    return DATABASE_CONFIG['path']

def get_backup_dir():
    """获取数据库备份目录"""
    return DATABASE_CONFIG['backup_dir']