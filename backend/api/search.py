from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import sqlite3
import re
# No longer need complex date parsing functions since data source is clean!

router = APIRouter()

def search_nonprofits(query: str, fields: Optional[List[str]] = None, limit: int = 50):
    """
    Search nonprofit organization data
    
    Args:
        query: Search keyword
        fields: List of fields to search
        limit: Limit of returned results
    """
    if fields is None:
        fields = ['campus', 'address', 'city', 'st', 'zip']
    
    # Build search conditions
    search_conditions = []
    params = []
    
    for field in fields:
        if field in ['campus', 'address', 'city', 'st', 'zip']:
            search_conditions.append(f"{field} LIKE ?")
            params.append(f"%{query}%")
    
    if not search_conditions:
        raise HTTPException(status_code=400, detail="Invalid search fields")
    
    where_clause = " OR ".join(search_conditions)
    
    try:
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()
        
        sql = f"""
        SELECT * FROM nonprofits 
        WHERE {where_clause}
        ORDER BY 
            CASE 
                WHEN campus LIKE ? THEN 1
                WHEN address LIKE ? THEN 2
                ELSE 3
            END,
            campus
        LIMIT ?
        """
        
        # Add sorting parameters
        params.extend([f"{query}%", f"{query}%", limit])
        
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/search")
async def search_api(
    q: str = Query("", description="Search keyword"),
    fields: Optional[str] = Query("campus,address,city,st", description="Search fields, comma separated"),
    limit: int = Query(50, ge=1, le=1000, description="Limit of returned results (1-1000)")
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
    valid_fields = ['campus', 'address', 'city', 'st', 'zip', 'part_i_summary_12_total_revenue_cy', 'employees']
    field_list = [f for f in field_list if f in valid_fields]
    
    if not field_list:
        field_list = ['campus', 'address', 'city', 'st']
    
    try:
        # If query is empty, fetch preview data
        if not q:
            conn = sqlite3.connect('irs.db')
            cursor = conn.cursor()
            
            sql = "SELECT * FROM nonprofits ORDER BY campus LIMIT ?"
            cursor.execute(sql, [limit])
            results = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            nonprofits = [dict(zip(columns, row)) for row in results]
            
            conn.close()
            
            return {
                "success": True,
                "query": q,
                "fields": field_list,
                "count": len(nonprofits),
                "results": nonprofits
            }
        else:
            results = search_nonprofits(q, field_list, limit)
            return {
                "success": True,
                "query": q,
                "fields": field_list,
                "count": len(results),
                "results": results
            }
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
    limit: int = Query(50, ge=1, le=1000)
):
    """
    Advanced search - supports multiple condition combinations
    """
    try:
        conn = sqlite3.connect('irs.db')
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
        SELECT * FROM nonprofits 
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
            "count": len(nonprofits),
            "results": nonprofits
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/available-years")
async def get_available_years():
    """
    Get all available years (query directly from standardized fiscal_year column)
    Data source is clean, API becomes extremely simple and efficient
    """
    try:
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()
        
        # SQL query becomes extremely simple - directly use clean columns
        cursor.execute(
            "SELECT DISTINCT fiscal_year FROM nonprofits WHERE fiscal_year IS NOT NULL ORDER BY fiscal_year DESC"
        )
        
        # Directly get sorted year list
        years = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"years": years}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get year data: {str(e)}")

@router.get("/available-months")
async def get_available_months(year: int = Query(..., description="Fiscal year to query available months")):
    """
    For a given fiscal year, get all available fiscal end months.
    Now query directly from clean 'fiscal_month' column, efficient and reliable.
    """
    try:
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()

        # SQL query becomes extremely simple - directly use clean columns
        cursor.execute(
            "SELECT DISTINCT fiscal_month FROM nonprofits WHERE fiscal_year = ? AND fiscal_month IS NOT NULL ORDER BY fiscal_month",
            (year,)
        )
        
        # Directly get sorted month list
        months = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return {"months": months}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available months: {str(e)}") 