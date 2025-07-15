import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_pagination_params(page: int, page_size: int, max_page_size: int = 1000) -> tuple:
    """
    Validate pagination parameters
    
    Args:
        page: Page number
        page_size: Page size
        max_page_size: Maximum page size
    
    Returns:
        (validated_page, validated_page_size, offset)
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    if page_size > max_page_size:
        page_size = max_page_size
    
    offset = (page - 1) * page_size
    return page, page_size, offset

def format_currency(amount: Union[int, float, None]) -> str:
    """
    格式化货币显示
    
    Args:
        amount: 金额
    
    Returns:
        格式化后的货币字符串
    """
    if amount is None:
        return "N/A"
    
    try:
        amount = float(amount)
        if amount >= 1_000_000_000:
            return f"${amount/1_000_000_000:.1f}B"
        elif amount >= 1_000_000:
            return f"${amount/1_000_000:.1f}M"
        elif amount >= 1_000:
            return f"${amount/1_000:.1f}K"
        else:
            return f"${amount:,.0f}"
    except (ValueError, TypeError):
        return "N/A"

def format_number(num: Union[int, float, None]) -> str:
    """
    格式化数字显示
    
    Args:
        num: 数字
    
    Returns:
        格式化后的数字字符串
    """
    if num is None:
        return "N/A"
    
    try:
        num = float(num)
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:,.0f}"
    except (ValueError, TypeError):
        return "N/A"

def validate_field_name(field: str, valid_fields: List[str]) -> bool:
    """
    验证字段名是否有效
    
    Args:
        field: 字段名
        valid_fields: 有效字段列表
    
    Returns:
        是否有效
    """
    return field in valid_fields

def sanitize_sql_input(input_str: str) -> str:
    """
    Sanitize SQL input to prevent SQL injection
    
    Args:
        input_str: Input string
    
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove dangerous SQL keywords
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER', 
        'EXEC', 'EXECUTE', 'UNION', 'SELECT', 'SCRIPT'
    ]
    
    input_upper = input_str.upper()
    for keyword in dangerous_keywords:
        if keyword in input_upper:
            return ""
    
    return input_str.strip()

def get_database_stats() -> Dict[str, Any]:
    """
    获取数据库统计信息
    
    Returns:
        数据库统计信息
    """
    try:
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM nonprofits")
        total_count = cursor.fetchone()[0]
        
        # 各州统计
        cursor.execute("""
            SELECT st, COUNT(*) as count 
            FROM nonprofits 
            WHERE st IS NOT NULL 
            GROUP BY st 
            ORDER BY count DESC 
            LIMIT 10
        """)
        st_stats = dict(cursor.fetchall())
        
        # 收入统计
        cursor.execute("""
            SELECT 
                MIN(part_i_summary_12_total_revenue_cy) as min_income,
                MAX(part_i_summary_12_total_revenue_cy) as max_income,
                AVG(part_i_summary_12_total_revenue_cy) as avg_income,
                COUNT(CASE WHEN part_i_summary_12_total_revenue_cy > 0 THEN 1 END) as non_zero_income_count
            FROM nonprofits
        """)
        income_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_records": total_count,
            "st_distribution": st_stats,
            "income_statistics": {
                "min": income_stats[0],
                "max": income_stats[1],
                "avg": income_stats[2],
                "non_zero_count": income_stats[3]
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {"error": str(e)}

def handle_database_error(error: Exception) -> Dict[str, Any]:
    """
    处理数据库错误
    
    Args:
        error: 数据库错误
    
    Returns:
        错误响应
    """
    logger.error(f"Database error: {error}")
    
    if "no such table" in str(error).lower():
        return {
            "success": False,
            "error": "Database table not found. Please initialize the database.",
            "code": "TABLE_NOT_FOUND"
        }
    elif "database is locked" in str(error).lower():
        return {
            "success": False,
            "error": "Database is currently busy. Please try again.",
            "code": "DATABASE_LOCKED"
        }
    else:
        return {
            "success": False,
            "error": "Database operation failed.",
            "code": "DATABASE_ERROR"
        }

def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数
    
    Args:
        value: 要转换的值
        default: 默认值
    
    Returns:
        整数值
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    
    Args:
        value: 要转换的值
        default: 默认值
    
    Returns:
        浮点数值
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default 

# 注意：原有的日期解析函数（extract_fiscal_year, extract_month_from_date_str）已移除
# 这些功能现在在数据管道层面的 parse_date 函数中完成，确保数据源头就是干净的
# 这是"治本"方案的体现 - 在数据进入数据库时就标准化，而不是在API层面重复解析
# 
# 所有 API 现在直接使用标准化的 fiscal_year 和 fiscal_month 列，
# 这些列包含纯净的数字数据，无需任何解析处理 