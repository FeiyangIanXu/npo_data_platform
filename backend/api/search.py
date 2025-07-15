from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
import sqlite3
import re
from utils.helpers import extract_fiscal_year

router = APIRouter()

def search_nonprofits(query: str, fields: Optional[List[str]] = None, limit: int = 50):
    """
    搜索非营利组织数据
    
    Args:
        query: 搜索关键词
        fields: 要搜索的字段列表
        limit: 返回结果数量限制
    """
    if fields is None:
        fields = ['campus', 'address', 'city', 'st', 'zip']
    
    # 构建搜索条件
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
        
        # 添加排序参数
        params.extend([f"{query}%", f"{query}%", limit])
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # 获取列名
        columns = [description[0] for description in cursor.description]
        
        # 转换为字典列表
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
    q: str = Query(..., description="搜索关键词"),
    fields: Optional[str] = Query("campus,address,city,st", description="搜索字段，用逗号分隔"),
    limit: int = Query(50, ge=1, le=1000, description="返回结果数量限制")
):
    """
    搜索非营利组织
    
    - **q**: 搜索关键词
    - **fields**: 要搜索的字段，用逗号分隔（如：name,address,city）
    - **limit**: 返回结果数量限制（1-1000）
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    # 解析搜索字段
    if not fields:
        fields = "campus,address,city,st"
    field_list = [f.strip() for f in fields.split(',') if f.strip()]
    
    # 验证字段
    valid_fields = ['campus', 'address', 'city', 'st', 'zip', 'part_i_summary_12_total_revenue_cy', 'employees']
    field_list = [f for f in field_list if f in valid_fields]
    
    if not field_list:
        field_list = ['campus', 'address', 'city', 'st']
    
    try:
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
    name: Optional[str] = Query(None, description="组织名称"),
    state: Optional[str] = Query(None, description="州"),
    city: Optional[str] = Query(None, description="城市"),
    org_type: Optional[str] = Query(None, description="组织类型"),
    min_income: Optional[float] = Query(None, description="最小收入"),
    max_income: Optional[float] = Query(None, description="最大收入"),
    limit: int = Query(50, ge=1, le=1000)
):
    """
    高级搜索 - 支持多个条件组合
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
        
        # if org_type:
        #     conditions.append("org_type = ?")
        #     params.append(org_type)
        
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
    获取所有可用的年度（以报表期末所在的公历年为准）
    按照WRDS风格，标准化为报表期末所在的公历年
    """
    try:
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()
        
        # 获取所有列名
        cursor.execute('PRAGMA table_info(nonprofits)')
        columns = [col[1] for col in cursor.fetchall()]
        
        # 查找fiscal year end列
        fiscal_year_column = None
        for col in columns:
            if 'fy_ending' in col.lower() or 'fiscal' in col.lower():
                fiscal_year_column = col
                break
        
        if not fiscal_year_column:
            raise HTTPException(status_code=500, detail="未找到报表期末年份相关字段")
        
        # 获取所有唯一的fiscal year end值
        cursor.execute(f'SELECT DISTINCT "{fiscal_year_column}" FROM nonprofits WHERE "{fiscal_year_column}" IS NOT NULL AND "{fiscal_year_column}" != ""')
        fiscal_years = cursor.fetchall()
        
        # 提取并标准化年份
        years = set()
        for (fiscal_year,) in fiscal_years:
            if fiscal_year:
                year = extract_fiscal_year(fiscal_year)
                if year:
                    years.add(year)
        
        conn.close()
        
        # 返回排序后的年份列表（降序，最新的在前）
        return {"years": sorted(list(years), reverse=True)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取年度数据失败: {str(e)}") 