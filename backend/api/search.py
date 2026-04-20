from fastapi import APIRouter, Query, HTTPException, Body
from typing import List, Optional
# No longer need complex date parsing functions since data source is clean!
from db_utils import get_connection, get_table_columns, resolve_table_name

router = APIRouter()

def normalize_fiscal_years(value):
    if value is None:
        return []

    if isinstance(value, list):
        raw_values = value
    elif isinstance(value, str):
        raw_values = value.split(",")
    else:
        raw_values = [value]

    fiscal_years = []
    for raw_value in raw_values:
        if raw_value is None or str(raw_value).strip() == "":
            continue
        fiscal_years.append(int(raw_value))
    return sorted(set(fiscal_years), reverse=True)

def search_nonprofits(query: str, fields: Optional[List[str]] = None, limit: int = 50, dataset: str = "default"):
    """
    Search nonprofit organization data
    
    Args:
        query: Search keyword
        fields: List of fields to search
        limit: Limit of returned results
    """
    if fields is None:
        fields = ['campus', 'address', 'city', 'st', 'zip']
    
    try:
        table_name = resolve_table_name(dataset)
        available_columns = set(get_table_columns(table_name))
        fields = [field for field in fields if field in available_columns]
        if not fields:
            raise HTTPException(status_code=400, detail=f"No searchable fields available for dataset '{dataset}'")

        search_conditions = []
        params = []
        for field in fields:
            if field in ['campus', 'address', 'city', 'st', 'zip', 'ein']:
                search_conditions.append(f"{field} LIKE ?")
                params.append(f"%{query}%")

        if not search_conditions:
            raise HTTPException(status_code=400, detail="Invalid search fields")

        where_clause = " OR ".join(search_conditions)
        order_by = "campus" if "campus" in available_columns else "ein"

        conn = get_connection()
        cursor = conn.cursor()
        
        sql = f"""
        SELECT * FROM "{table_name}" 
        WHERE {where_clause}
        ORDER BY {order_by}
        LIMIT ?
        """
        
        params.append(limit)
        
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
        return nonprofits
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search")
async def search_api(
    q: str = Query("", description="Search keyword"),
    fields: Optional[str] = Query("campus,address,city,st", description="Search fields, comma separated"),
    limit: int = Query(50, ge=1, le=1000, description="Limit of returned results (1-1000)"),
    dataset: str = Query("default", description="Dataset name: default or propublica"),
):
    """
    Search nonprofit organizations
    
    - **q**: Search keyword
    - **fields**: Fields to search, comma separated (e.g.: name,address,city)
    - **limit**: Limit of returned results (1-1000)
    """
    # Allow empty query for preview data
    if not q.strip():
        q = ""  # Set to empty string for fetching preview data
    
    # Parse search fields
    if not fields:
        fields = "campus,address,city,st"
    field_list = [f.strip() for f in fields.split(',') if f.strip()]
    
    # Validate fields
    table_name = resolve_table_name(dataset)
    available_columns = set(get_table_columns(table_name))
    valid_fields = ['campus', 'address', 'city', 'st', 'zip', 'part_i_summary_12_total_revenue_cy', 'employees', 'ein']
    field_list = [f for f in field_list if f in valid_fields]
    field_list = [f for f in field_list if f in available_columns]
    
    if not field_list:
        field_list = [field for field in ['campus', 'address', 'city', 'st', 'ein'] if field in available_columns]
    
    try:
        # If query is empty, fetch preview data
        if not q:
            conn = get_connection()
            cursor = conn.cursor()
            
            order_by = "campus" if "campus" in available_columns else "ein"
            sql = f'SELECT * FROM "{table_name}" ORDER BY {order_by} LIMIT ?'
            cursor.execute(sql, [limit])
            results = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            nonprofits = [dict(zip(columns, row)) for row in results]
            
            conn.close()
            
            return {
                "success": True,
                "dataset": dataset,
                "query": q,
                "fields": field_list,
                "count": len(nonprofits),
                "results": nonprofits
            }
        else:
            results = search_nonprofits(q, field_list, limit, dataset)
            return {
                "success": True,
                "dataset": dataset,
                "query": q,
                "fields": field_list,
                "count": len(results),
                "results": results
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/advanced")
async def advanced_search(
    name: Optional[str] = Query(None, description="Organization name"),
    state: Optional[str] = Query(None, description="State"),
    city: Optional[str] = Query(None, description="City"),
    fiscal_year: Optional[int] = Query(None, description="Fiscal year (e.g. 2023)"),
    fiscal_month: Optional[int] = Query(None, description="Fiscal end month (1-12)"),
    min_income: Optional[float] = Query(None, description="Minimum income"),
    max_income: Optional[float] = Query(None, description="Maximum income"),
    limit: int = Query(50, ge=1, le=1000),
    dataset: str = Query("default", description="Dataset name: default or propublica"),
):
    """
    Advanced search - supports multiple condition combinations
    """
    try:
        table_name = resolve_table_name(dataset)
        conn = get_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if name:
            conditions.append("campus LIKE ?")
            params.append(f"%{name}%")
        
        if state:
            conditions.append("st = ?")
            params.append(state.upper())
        
        if city:
            conditions.append("city LIKE ?")
            params.append(f"%{city}%")
        
        if fiscal_year is not None:
            conditions.append("fiscal_year = ?")
            params.append(fiscal_year)
        
        if fiscal_month is not None:
            conditions.append("fiscal_month = ?")
            params.append(fiscal_month)
        
        if min_income is not None:
            conditions.append("part_i_summary_12_total_revenue_cy >= ?")
            params.append(min_income)
        
        if max_income is not None:
            conditions.append("part_i_summary_12_total_revenue_cy <= ?")
            params.append(max_income)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
        SELECT * FROM "{table_name}" 
        WHERE {where_clause}
        ORDER BY part_i_summary_12_total_revenue_cy DESC, campus
        LIMIT ?
        """
        
        params.append(limit)
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        nonprofits = [dict(zip(columns, row)) for row in results]
        
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

@router.get("/available-years")
async def get_available_years(dataset: str = Query("default", description="Dataset name: default or propublica")):
    """
    Get all available years (query directly from standardized fiscal_year column)
    Data source is clean, API becomes extremely simple and efficient
    """
    try:
        table_name = resolve_table_name(dataset)
        conn = get_connection()
        cursor = conn.cursor()
        
        # SQL query becomes extremely simple - directly use clean columns
        cursor.execute(
            f'SELECT DISTINCT fiscal_year FROM "{table_name}" WHERE fiscal_year IS NOT NULL ORDER BY fiscal_year DESC'
        )
        
        # Directly get sorted year list
        years = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"dataset": dataset, "years": years}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get year data: {str(e)}")

@router.get("/available-months")
async def get_available_months(
    year: int = Query(..., description="Fiscal year to query available months"),
    dataset: str = Query("default", description="Dataset name: default or propublica"),
):
    """
    For a given fiscal year, get all available fiscal end months.
    Now query directly from clean 'fiscal_month' column, efficient and reliable.
    """
    try:
        table_name = resolve_table_name(dataset)
        conn = get_connection()
        cursor = conn.cursor()

        # SQL query becomes extremely simple - directly use clean columns
        cursor.execute(
            f'SELECT DISTINCT fiscal_month FROM "{table_name}" WHERE fiscal_year = ? AND fiscal_month IS NOT NULL ORDER BY fiscal_month',
            (year,)
        )
        
        # Directly get sorted month list
        months = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"dataset": dataset, "months": months}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available months: {str(e)}")

@router.get("/available-states")
async def get_available_states(
    fiscal_year: Optional[int] = Query(None, description="Fiscal year to filter states"),
    dataset: str = Query("default", description="Dataset name: default or propublica"),
):
    """
    Get all available states, optionally filtered by fiscal year
    """
    try:
        table_name = resolve_table_name(dataset)
        conn = get_connection()
        cursor = conn.cursor()
        
        if fiscal_year:
            cursor.execute(
                f'SELECT DISTINCT st FROM "{table_name}" WHERE fiscal_year = ? AND st IS NOT NULL ORDER BY st',
                (fiscal_year,)
            )
        else:
            cursor.execute(
                f'SELECT DISTINCT st FROM "{table_name}" WHERE st IS NOT NULL ORDER BY st'
            )
        
        states = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"dataset": dataset, "states": states}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available states: {str(e)}")

@router.get("/available-cities")
async def get_available_cities(
    fiscal_year: Optional[int] = Query(None, description="Fiscal year to filter cities"),
    state: Optional[str] = Query(None, description="State to filter cities"),
    dataset: str = Query("default", description="Dataset name: default or propublica"),
):
    """
    Get all available cities, optionally filtered by fiscal year and/or state
    """
    try:
        table_name = resolve_table_name(dataset)
        conn = get_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if fiscal_year:
            conditions.append("fiscal_year = ?")
            params.append(fiscal_year)
        
        if state:
            conditions.append("st = ?")
            params.append(state.upper())
        
        # Always filter out null cities
        conditions.append("city IS NOT NULL")
        
        where_clause = " AND ".join(conditions) if conditions else "city IS NOT NULL"
        
        sql = f'SELECT DISTINCT city FROM "{table_name}" WHERE {where_clause} ORDER BY city'
        cursor.execute(sql, params)
        
        cities = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"dataset": dataset, "cities": cities}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available cities: {str(e)}")

# Enhanced search endpoint to support batch search from frontend
@router.post("/search/batch")
async def batch_search_api(
    request: dict = Body(...)
):
    """
    Batch search for multiple organization names or EINs
    Supports the enhanced frontend search functionality with search_type differentiation
    """
    try:
        fiscal_year = request.get('fiscal_year')
        fiscal_years = request.get('fiscal_years')
        fiscal_month = request.get('fiscal_month')
        search_terms = request.get('search_terms', [])
        search_type = request.get('search_type', 'name')  # 'name' or 'ein'
        dataset = request.get('dataset', 'default')
        
        selected_years = normalize_fiscal_years(fiscal_years)
        if fiscal_year is not None:
            selected_years.extend(normalize_fiscal_years(fiscal_year))
            selected_years = sorted(set(selected_years), reverse=True)

        if not selected_years:
            raise HTTPException(status_code=400, detail="At least one fiscal year is required")
        
        if not search_terms:
            raise HTTPException(status_code=400, detail="Search terms are required")
        
        table_name = resolve_table_name(dataset)
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build search conditions for multiple terms
        all_results = []
        
        print(f"=== BATCH SEARCH DEBUG ===")
        print(f"Search type: {search_type}")
        print(f"Search terms: {search_terms}")
        print(f"Fiscal years: {selected_years}")
        print(f"Fiscal month: {fiscal_month}")
        print(f"=========================")
        
        for term in search_terms:
            term = term.strip()
            if not term:
                continue
                
            # Base conditions
            conditions = []
            params = []
            
            # Add fiscal year condition
            year_placeholders = ", ".join(["?" for _ in selected_years])
            conditions.append(f"fiscal_year IN ({year_placeholders})")
            params.extend(selected_years)
            
            # Add fiscal month condition if provided
            if fiscal_month:
                conditions.append("fiscal_month = ?")
                params.append(fiscal_month)
            
            # Search based on search_type
            if search_type == 'ein':
                # Search only in EIN field - exact match or starts with
                search_condition = "ein LIKE ?"
                conditions.append(search_condition)
                params.append(f"{term}%")
                
                order_clause = "ein"
            else:
                # Search only in campus (organization name) field
                search_condition = "campus LIKE ?"
                conditions.append(search_condition)
                params.append(f"%{term}%")
                
                order_clause = f"""
                CASE 
                    WHEN campus LIKE ? THEN 1
                    WHEN campus LIKE ? THEN 2
                    ELSE 3
                END,
                campus"""
            
            where_clause = " AND ".join(conditions)
            
            if search_type == 'ein':
                sql = f"""
                SELECT * FROM "{table_name}" 
                WHERE {where_clause}
                ORDER BY {order_clause}
                LIMIT 50
                """
            else:
                sql = f"""
                SELECT * FROM "{table_name}" 
                WHERE {where_clause}
                ORDER BY {order_clause}
                LIMIT 50
                """
                # Add sorting parameters for name search
                params.extend([f"{term}%", f"%{term}%"])
            
            print(f"Executing SQL for term '{term}': {sql}")
            print(f"Parameters: {params}")
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            print(f"Found {len(results)} results for term '{term}'")
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Convert to dictionary list and add to results
            for row in results:
                nonprofit = dict(zip(columns, row))
                # Avoid duplicates by checking EIN
                if not any(existing['ein'] == nonprofit['ein'] for existing in all_results):
                    all_results.append(nonprofit)
        
        conn.close()
        
        print(f"Total unique results: {len(all_results)}")
        
        return {
            "success": True,
            "dataset": dataset,
            "fiscal_years": selected_years,
            "count": len(all_results),
            "results": all_results,
            "search_type": search_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in batch search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
