from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from db_utils import get_connection, get_table_columns, resolve_table_name

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
    dataset: str = "default"

def build_sql_condition(condition: FilterCondition) -> tuple:
    """
    Build SQL condition
    
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
    Advanced filtering API
    
    Supported operators:
    - equals: equal to
    - not_equals: not equal to
    - contains: contains
    - in: in list
    - not_in: not in list
    - greater_than: greater than
    - less_than: less than
    - greater_equal: greater than or equal
    - less_equal: less than or equal
    - between: within range
    - is_null: is null
    - is_not_null: is not null
    """
    try:
        if not request.conditions:
            raise HTTPException(status_code=400, detail="At least one filter condition is required")
        
        if request.logic not in ["AND", "OR"]:
            raise HTTPException(status_code=400, detail="Logic operator must be AND or OR")

        table_name = resolve_table_name(request.dataset)
        available_columns = set(get_table_columns(table_name))
        
        # Validate field names (updated to standardized columns)
        valid_fields = [
            'campus', 'address', 'city', 'st', 'zip', 
            'part_i_summary_12_total_revenue_cy', 'employees', 'ein',
            'fiscal_year',   # standardized fiscal year
            'fiscal_month'   # standardized fiscal end month
        ]
        valid_fields = [field for field in valid_fields if field in available_columns]
        
        for condition in request.conditions:
            if condition.field not in valid_fields:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid field name: {condition.field}"
                )
        
        # Build SQL query
        conditions = []
        params = []
        
        for condition in request.conditions:
            try:
                sql_condition, condition_params = build_sql_condition(condition)
                conditions.append(sql_condition)
                params.extend(condition_params)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        # Build WHERE clause
        where_clause = f" {request.logic} ".join(conditions)
        
        # Build ORDER BY clause
        order_clause = ""
        if request.order_by:
            if request.order_by in valid_fields:
                order_direction = "DESC" if request.order_direction.upper() == "DESC" else "ASC"
                order_clause = f" ORDER BY {request.order_by} {order_direction}"
            else:
                raise HTTPException(status_code=400, detail=f"Invalid order field: {request.order_by}")
        
        # Execute query
        sql = f"""
        SELECT * FROM "{table_name}" 
        WHERE {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?
        """
        
        params.extend([request.limit, request.offset])
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        result_columns = [description[0] for description in cursor.description]
        
        # Get total count
        count_sql = f'SELECT COUNT(*) FROM "{table_name}" WHERE {where_clause}'
        cursor.execute(count_sql, params[:-2])  # Remove LIMIT and OFFSET params
        total_count = cursor.fetchone()[0]
        
        # Convert to dictionary list
        nonprofits = []
        for row in results:
            nonprofit = dict(zip(result_columns, row))
            nonprofits.append(nonprofit)
        
        conn.close()
        
        return {
            "success": True,
            "dataset": request.dataset,
            "total_count": total_count,
            "filtered_count": len(nonprofits),
            "limit": request.limit,
            "offset": request.offset,
            "has_more": (request.offset + request.limit) < total_count,
            "results": nonprofits
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filter/fields")
async def get_filter_fields(dataset: str = "default"):
    """
    Get available filter field information
    """
    table_name = resolve_table_name(dataset)
    available_columns = set(get_table_columns(table_name))
    field_definitions = {
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
    }
    return {
        "success": True,
        "dataset": dataset,
        "fields": {name: config for name, config in field_definitions.items() if name in available_columns},
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

@router.get("/filter/revenue-bands")
async def get_revenue_bands(
    fiscal_year: int,
    fiscal_month: Optional[int] = None,
    dataset: str = "default",
):
    """
    Build 5M revenue bands up to the maximum available revenue for the selected scope.
    """
    try:
        table_name = resolve_table_name(dataset)
        conn = get_connection()
        cursor = conn.cursor()

        conditions = ["fiscal_year = ?", "part_i_summary_12_total_revenue_cy IS NOT NULL", "part_i_summary_12_total_revenue_cy >= 0"]
        params = [fiscal_year]

        if fiscal_month is not None:
            conditions.append("fiscal_month = ?")
            params.append(fiscal_month)

        where_clause = " AND ".join(conditions)
        cursor.execute(
            f'SELECT MAX(part_i_summary_12_total_revenue_cy) FROM "{table_name}" WHERE {where_clause}',
            params,
        )
        max_revenue = cursor.fetchone()[0] or 0
        conn.close()

        band_size = 5_000_000
        band_ceiling = band_size if max_revenue <= 0 else int(((max_revenue + band_size - 1) // band_size) * band_size)

        bands = []
        for start in range(0, band_ceiling, band_size):
            end = start + band_size
            max_value = end - 1 if end < max_revenue else max_revenue
            bands.append(
                {
                    "key": f"{start}-{end}",
                    "label": f"{start // 1_000_000}-{end // 1_000_000}M",
                    "min_revenue": start,
                    "max_revenue": max_value,
                }
            )

        return {
            "success": True,
            "dataset": dataset,
            "fiscal_year": fiscal_year,
            "fiscal_month": fiscal_month,
            "band_size": band_size,
            "max_revenue": max_revenue,
            "bands": bands,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/filter/enhanced")
async def enhanced_filter_for_frontend(
    request: dict = Body(...)
):
    """
    Enhanced filter endpoint specifically designed for the frontend QueryForm
    Supports geographic, financial, and operational filtering with fiscal year/month
    """
    try:
        # Extract values from request body
        fiscal_year = request.get('fiscal_year')
        fiscal_month = request.get('fiscal_month')
        geo_filters = request.get('geo_filters')
        financial_filters = request.get('financial_filters')
        operational_filters = request.get('operational_filters')
        workforce_filters = request.get('workforce_filters')
        filing_filters = request.get('filing_filters')
        dataset = request.get('dataset', 'default')
        
        if not fiscal_year:
            raise HTTPException(status_code=400, detail="Fiscal year is required")
        
        table_name = resolve_table_name(dataset)
        conn = get_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        # Always filter by fiscal year
        conditions.append("fiscal_year = ?")
        params.append(fiscal_year)
        
        # Filter by fiscal month if provided
        if fiscal_month:
            conditions.append("fiscal_month = ?")
            params.append(fiscal_month)
        
        # Geographic filters
        if geo_filters:
            st_value = geo_filters.get('st')
            if st_value:
                conditions.append("st = ?")
                params.append(st_value.upper())
            
            city_value = geo_filters.get('city')
            if city_value:
                conditions.append("city = ?")
                params.append(city_value)
        
        # Financial filters
        if financial_filters:
            if financial_filters.get('min_revenue') is not None:
                conditions.append("part_i_summary_12_total_revenue_cy >= ?")
                params.append(financial_filters['min_revenue'])
            
            if financial_filters.get('max_revenue') is not None:
                conditions.append("part_i_summary_12_total_revenue_cy <= ?")
                params.append(financial_filters['max_revenue'])
        
        # Operational filters kept for backward compatibility with the older frontend.
        if operational_filters:
            if operational_filters.get('min_ilu') is not None:
                conditions.append("employees >= ?")
                params.append(operational_filters['min_ilu'])
            
            if operational_filters.get('max_ilu') is not None:
                conditions.append("employees <= ?")
                params.append(operational_filters['max_ilu'])

        # Workforce filters for ProPublica-first query flow.
        if workforce_filters:
            if workforce_filters.get('min_employees') is not None:
                conditions.append("employees >= ?")
                params.append(workforce_filters['min_employees'])

            if workforce_filters.get('max_employees') is not None:
                conditions.append("employees <= ?")
                params.append(workforce_filters['max_employees'])

        # Filing filters for ProPublica form type selection.
        if filing_filters:
            form_types = filing_filters.get('form_types') or []
            normalized_form_types = [str(form_type).strip() for form_type in form_types if str(form_type).strip()]
            if normalized_form_types:
                placeholders = ", ".join(["?" for _ in normalized_form_types])
                conditions.append(f"propublica_form_type IN ({placeholders})")
                params.extend(normalized_form_types)
        
        where_clause = " AND ".join(conditions)
        
        sql = f"""
        SELECT * FROM "{table_name}" 
        WHERE {where_clause}
        ORDER BY part_i_summary_12_total_revenue_cy DESC, campus
        LIMIT 1000
        """
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Convert to dictionary list
        nonprofits = []
        for row in results:
            nonprofit = dict(zip(columns, row))
            nonprofits.append(nonprofit)
        
        conn.close()
        
        return {
            "success": True,
            "dataset": dataset,
            "count": len(nonprofits),
            "results": nonprofits
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
