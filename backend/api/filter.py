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
    Build SQL condition
    
    Returns:
        (sql_condition, params)
    """
    field = condition.field
    operator = condition.operator
    value = condition.value
    
    if operator == "equals" and isinstance(value, str):
        return f"UPPER({field}) = UPPER(?)", [value]
    elif operator == "equals":
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

#
# 这是你要粘贴到 filter.py 的最终代码
#

@router.post("/filter")
async def advanced_filter(request: dict = Body(...)):
    try:
        fiscal_year = request.get('fiscal_year')
        fiscal_month = request.get('fiscal_month')
        geo_filters = request.get('geo_filters')
        financial_filters = request.get('financial_filters')
        operational_filters = request.get('operational_filters')

        sql_conditions = []
        params = []

        # 1. 处理年份 (必须有)
        if fiscal_year:
            sql_conditions.append("fiscal_year = ?")
            params.append(fiscal_year)
        else:
            raise HTTPException(status_code=400, detail="Fiscal year is required.")

        # 2. 处理月份 (可选)
        if fiscal_month:
            sql_conditions.append("fiscal_month = ?")
            params.append(fiscal_month)
            
        # 3. 处理地理筛选 (可选)
        if geo_filters:
            if geo_filters.get('st'):
                sql_conditions.append("UPPER(st) = UPPER(?)")
                params.append(geo_filters['st'])
            if geo_filters.get('city'):
                sql_conditions.append("UPPER(city) = UPPER(?)")
                params.append(geo_filters['city'])

        # 4. 处理财务筛选 (可选)
        if financial_filters:
            if financial_filters.get('min_revenue') is not None:
                sql_conditions.append("part_i_summary_12_total_revenue_cy >= ?")
                params.append(float(financial_filters['min_revenue']))
            if financial_filters.get('max_revenue') is not None:
                sql_conditions.append("part_i_summary_12_total_revenue_cy <= ?")
                params.append(float(financial_filters['max_revenue']))
        
        # 5. 处理运营筛选 (可选) - 假设用 'employees' 字段
        if operational_filters:
            if operational_filters.get('min_ilu') is not None:
                sql_conditions.append("employees >= ?")
                params.append(int(operational_filters['min_ilu']))
            if operational_filters.get('max_ilu') is not None:
                sql_conditions.append("employees <= ?")
                params.append(int(operational_filters['max_ilu']))


        where_clause = " AND ".join(sql_conditions)
        sql = f"SELECT * FROM nonprofits WHERE {where_clause} ORDER BY campus LIMIT 1000"

        # --- 调试代码 ---
        print("\n" + "="*50)
        print("EXECUTING FINAL SQL QUERY (from /api/filter):")
        print("SQL:", sql)
        print("PARAMETERS:", params)
        print("="*50 + "\n")
        
        conn = sqlite3.connect('irs.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {"success": True, "count": len(results), "results": results}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter/fields")
async def get_filter_fields():
    """
    Get available filter field information
    """
    return {
        "success": True,
        "fields": {
            "campus": {
                "type": "string",
                "description": "Organization name",
                "operators": ["equals", "not_equals", "contains", "is_null", "is_not_null"]
            },
            "address": {
                "type": "string", 
                "description": "Address",
                "operators": ["equals", "not_equals", "contains", "is_null", "is_not_null"]
            },
            "city": {
                "type": "string",
                "description": "City",
                "operators": ["equals", "not_equals", "contains", "in", "not_in", "is_null", "is_not_null"]
            },
            "st": {
                "type": "string",
                "description": "State",
                "operators": ["equals", "not_equals", "in", "not_in", "is_null", "is_not_null"]
            },
            "zip": {
                "type": "string",
                "description": "ZIP code",
                "operators": ["equals", "not_equals", "contains", "in", "not_in", "is_null", "is_not_null"]
            },
            "part_i_summary_12_total_revenue_cy": {
                "type": "number",
                "description": "Current year total revenue",
                "operators": ["equals", "not_equals", "greater_than", "less_than", "greater_equal", "less_equal", "between", "is_null", "is_not_null"]
            },
            "employees": {
                "type": "number", 
                "description": "Number of employees",
                "operators": ["equals", "not_equals", "greater_than", "less_than", "greater_equal", "less_equal", "between", "is_null", "is_not_null"]
            },
            "ein": {
                "type": "string",
                "description": "Employer Identification Number",
                "operators": ["equals", "not_equals", "contains", "is_null", "is_not_null"]
            },
            "fiscal_year": {
                "type": "number",
                "description": "Fiscal year (standardized calendar year, e.g. 2023)",
                "operators": ["equals", "not_equals", "greater_than", "less_than", "greater_equal", "less_equal", "between", "in", "not_in", "is_null", "is_not_null"]
            },
            "fiscal_month": {
                "type": "number",
                "description": "Fiscal end month (standardized month number, 1-12)",
                "operators": ["equals", "not_equals", "in", "not_in", "is_null", "is_not_null"]
            }
        },
        "logic_operators": ["AND", "OR"],
        "order_directions": ["ASC", "DESC"]
    }

@router.get("/filter/examples")
async def get_filter_examples():
    """
    Get filter examples
    """
    return {
        "success": True,
        "examples": [
            {
                "name": "High Revenue Organizations",
                "description": "Find organizations with revenue over $1 million",
                "conditions": [
                    {"field": "part_i_summary_12_total_revenue_cy", "operator": "greater_than", "value": 1000000}
                ],
                "logic": "AND"
            },
            {
                "name": "California Hospitals",
                "description": "Find hospital organizations in California",
                "conditions": [
                    {"field": "st", "operator": "equals", "value": "CA"},
                    {"field": "campus", "operator": "contains", "value": "hospital"}
                ],
                "logic": "AND"
            },
            {
                "name": "Major City Organizations",
                "description": "Find organizations in New York, Los Angeles, Chicago",
                "conditions": [
                    {"field": "city", "operator": "in", "value": ["NEW YORK", "LOS ANGELES", "CHICAGO"]}
                ],
                "logic": "OR"
            },
            {
                "name": "Medium Size Organizations",
                "description": "Find organizations with 10-100 employees",
                "conditions": [
                    {"field": "employees", "operator": "between", "value": [10, 100]}
                ],
                "logic": "AND"
            },
            {
                "name": "2023 Fiscal Year Organizations",
                "description": "Find organizations with 2023 fiscal year",
                "conditions": [
                    {"field": "fiscal_year", "operator": "equals", "value": 2023}
                ],
                "logic": "AND"
            },
            {
                "name": "December Year-End",
                "description": "Find organizations with fiscal year ending in December",
                "conditions": [
                    {"field": "fiscal_month", "operator": "equals", "value": 12}
                ],
                "logic": "AND"
            },
            {
                "name": "2023 June Year-End",
                "description": "Find organizations with fiscal year ending in June 2023",
                "conditions": [
                    {"field": "fiscal_year", "operator": "equals", "value": 2023},
                    {"field": "fiscal_month", "operator": "equals", "value": 6}
                ],
                "logic": "AND"
            }
        ]
    } 

