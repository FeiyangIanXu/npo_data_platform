from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
import sqlite3

router = APIRouter()

class FilterCondition(BaseModel):
    field: str
    operator: str  # equals, not_equals, contains, in, not_in, greater_than, less_than, between
    value: Union[str, int, float, List[Any]]

class FilterRequest(BaseModel):
    conditions: List[FilterCondition]
    logic: str = "AND"  # AND or OR
    limit: int = 100
    offset: int = 0
    order_by: Optional[str] = None
    order_direction: str = "ASC"

def build_sql_condition(condition: FilterCondition) -> tuple:
    """
    构建SQL条件
    
    Returns:
        (sql_condition, params)
    """
    field = condition.field
    operator = condition.operator
    value = condition.value
    
    if operator == "equals":
        return f"{field} = ?", [value]
    elif operator == "not_equals":
        return f"{field} != ?", [value]
    elif operator == "contains":
        return f"{field} LIKE ?", [f"%{value}%"]
    elif operator == "in":
        if isinstance(value, list):
            placeholders = ','.join(['?' for _ in value])
            return f"{field} IN ({placeholders})", value
        else:
            return f"{field} = ?", [value]
    elif operator == "not_in":
        if isinstance(value, list):
            placeholders = ','.join(['?' for _ in value])
            return f"{field} NOT IN ({placeholders})", value
        else:
            return f"{field} != ?", [value]
    elif operator == "greater_than":
        return f"{field} > ?", [value]
    elif operator == "less_than":
        return f"{field} < ?", [value]
    elif operator == "greater_equal":
        return f"{field} >= ?", [value]
    elif operator == "less_equal":
        return f"{field} <= ?", [value]
    elif operator == "between":
        if isinstance(value, list) and len(value) == 2:
            return f"{field} BETWEEN ? AND ?", value
        else:
            raise ValueError("Between operator requires a list with exactly 2 values")
    elif operator == "is_null":
        return f"{field} IS NULL", []
    elif operator == "is_not_null":
        return f"{field} IS NOT NULL", []
    else:
        raise ValueError(f"Unsupported operator: {operator}")

@router.post("/filter")
async def advanced_filter(request: FilterRequest):
    """
    高级筛选API
    
    支持的操作符:
    - equals: 等于
    - not_equals: 不等于
    - contains: 包含
    - in: 在列表中
    - not_in: 不在列表中
    - greater_than: 大于
    - less_than: 小于
    - greater_equal: 大于等于
    - less_equal: 小于等于
    - between: 在范围内
    - is_null: 为空
    - is_not_null: 不为空
    """
    try:
        if not request.conditions:
            raise HTTPException(status_code=400, detail="至少需要一个筛选条件")
        
        if request.logic not in ["AND", "OR"]:
            raise HTTPException(status_code=400, detail="逻辑操作符必须是 AND 或 OR")
        
        # 验证字段名
        valid_fields = [
            'campus', 'address', 'city', 'st', 'zip', 
            'part_i_summary_12_total_revenue_cy', 'employees', 'ein'
        ]
        
        for condition in request.conditions:
            if condition.field not in valid_fields:
                raise HTTPException(
                    status_code=400, 
                    detail=f"无效的字段名: {condition.field}"
                )
        
        # 构建SQL查询
        conditions = []
        params = []
        
        for condition in request.conditions:
            try:
                sql_condition, condition_params = build_sql_condition(condition)
                conditions.append(sql_condition)
                params.extend(condition_params)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # 构建WHERE子句
        where_clause = f" {request.logic} ".join(conditions)
        
        # 构建ORDER BY子句
        order_clause = ""
        if request.order_by:
            if request.order_by in valid_fields:
                order_direction = "DESC" if request.order_direction.upper() == "DESC" else "ASC"
                order_clause = f" ORDER BY {request.order_by} {order_direction}"
            else:
                raise HTTPException(status_code=400, detail=f"无效的排序字段: {request.order_by}")
        
        # 执行查询
        sql = f"""
        SELECT * FROM nonprofits 
        WHERE {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?
        """
        
        params.extend([request.limit, request.offset])
        
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # 获取总记录数
        count_sql = f"SELECT COUNT(*) FROM nonprofits WHERE {where_clause}"
        cursor.execute(count_sql, params[:-2])  # 去掉LIMIT和OFFSET参数
        total_count = cursor.fetchone()[0]
        
        # 获取列名
        columns = [description[0] for description in cursor.description]
        
        # 转换为字典列表
        nonprofits = []
        for row in results:
            nonprofit = dict(zip(columns, row))
            nonprofits.append(nonprofit)
        
        conn.close()
        
        return {
            "success": True,
            "total_count": total_count,
            "filtered_count": len(nonprofits),
            "limit": request.limit,
            "offset": request.offset,
            "has_more": (request.offset + request.limit) < total_count,
            "results": nonprofits
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filter/fields")
async def get_filter_fields():
    """
    获取可用的筛选字段信息
    """
    return {
        "success": True,
        "fields": {
            "campus": {
                "type": "string",
                "description": "组织名称",
                "operators": ["equals", "not_equals", "contains", "is_null", "is_not_null"]
            },
            "address": {
                "type": "string", 
                "description": "地址",
                "operators": ["equals", "not_equals", "contains", "is_null", "is_not_null"]
            },
            "city": {
                "type": "string",
                "description": "城市",
                "operators": ["equals", "not_equals", "contains", "in", "not_in", "is_null", "is_not_null"]
            },
            "st": {
                "type": "string",
                "description": "州",
                "operators": ["equals", "not_equals", "in", "not_in", "is_null", "is_not_null"]
            },
            "zip": {
                "type": "string",
                "description": "邮编",
                "operators": ["equals", "not_equals", "contains", "in", "not_in", "is_null", "is_not_null"]
            },
            "part_i_summary_12_total_revenue_cy": {
                "type": "number",
                "description": "当前年度总收入",
                "operators": ["equals", "not_equals", "greater_than", "less_than", "greater_equal", "less_equal", "between", "is_null", "is_not_null"]
            },
            "employees": {
                "type": "number", 
                "description": "员工数量",
                "operators": ["equals", "not_equals", "greater_than", "less_than", "greater_equal", "less_equal", "between", "is_null", "is_not_null"]
            },
            "filing_date": {
                "type": "date",
                "description": "申报日期",
                "operators": ["equals", "not_equals", "greater_than", "less_than", "greater_equal", "less_equal", "between", "is_null", "is_not_null"]
            },
            "ein": {
                "type": "string",
                "description": "雇主识别号",
                "operators": ["equals", "not_equals", "contains", "is_null", "is_not_null"]
            }
        },
        "logic_operators": ["AND", "OR"],
        "order_directions": ["ASC", "DESC"]
    }

@router.get("/filter/examples")
async def get_filter_examples():
    """
    获取筛选示例
    """
    return {
        "success": True,
        "examples": [
            {
                "name": "高收入组织",
                "description": "查找收入超过100万美元的组织",
                "conditions": [
                    {"field": "part_i_summary_12_total_revenue_cy", "operator": "greater_than", "value": 1000000}
                ],
                "logic": "AND"
            },
            {
                "name": "加州医院",
                "description": "查找加州的医院组织",
                "conditions": [
                    {"field": "st", "operator": "equals", "value": "CA"},
                    {"field": "campus", "operator": "contains", "value": "hospital"}
                ],
                "logic": "AND"
            },
            {
                "name": "大城市组织",
                "description": "查找纽约、洛杉矶、芝加哥的组织",
                "conditions": [
                    {"field": "city", "operator": "in", "value": ["NEW YORK", "LOS ANGELES", "CHICAGO"]}
                ],
                "logic": "OR"
            },
            {
                "name": "中等规模组织",
                "description": "查找员工数量在10-100之间的组织",
                "conditions": [
                    {"field": "employees", "operator": "between", "value": [10, 100]}
                ],
                "logic": "AND"
            }
        ]
    } 