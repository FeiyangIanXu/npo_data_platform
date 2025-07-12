from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import sqlite3
import csv
import json
import io
from datetime import datetime

router = APIRouter()

def get_export_data(filters: Dict[str, Any] = None, limit: int = 10000):
    """
    获取要导出的数据
    
    Args:
        filters: 筛选条件
        limit: 数据量限制
    """
    try:
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()
        
        sql = "SELECT * FROM nonprofits"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, (list, tuple)):
                        placeholders = ','.join(['?' for _ in value])
                        conditions.append(f"{key} IN ({placeholders})")
                        params.extend(value)
                    else:
                        conditions.append(f"{key} = ?")
                        params.append(value)
            
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
        
        sql += f" LIMIT {limit}"
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        data = [dict(zip(columns, row)) for row in results]
        
        conn.close()
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data: {str(e)}")

@router.post("/export/csv")
async def export_csv(
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10000
):
    """
    导出CSV格式数据
    """
    try:
        data = get_export_data(filters, limit)
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        
        # 创建CSV内容
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        csv_content = output.getvalue()
        output.close()
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nonprofits_export_{timestamp}.csv"
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/json")
async def export_json(
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10000
):
    """
    导出JSON格式数据
    """
    try:
        data = get_export_data(filters, limit)
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nonprofits_export_{timestamp}.json"
        
        return Response(
            content=json.dumps(data, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/excel")
async def export_excel(
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10000
):
    """
    导出Excel格式数据
    """
    try:
        # 检查是否安装了openpyxl
        try:
            import openpyxl
            from openpyxl import Workbook
        except ImportError:
            raise HTTPException(
                status_code=500, 
                detail="Excel export requires openpyxl. Install with: pip install openpyxl"
            )
        
        data = get_export_data(filters, limit)
        
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        
        # 创建Excel工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = "Nonprofits Data"
        
        # 写入表头
        headers = list(data[0].keys())
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # 写入数据
        for row, record in enumerate(data, 2):
            for col, header in enumerate(headers, 1):
                value = record.get(header, "")
                ws.cell(row=row, column=col, value=value)
        
        # 保存到内存
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nonprofits_export_{timestamp}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/status")
async def export_status():
    """
    获取导出功能状态
    """
    try:
        conn = sqlite3.connect('irs.db')
        cursor = conn.cursor()
        
        # 获取数据统计
        cursor.execute("SELECT COUNT(*) FROM nonprofits")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(part_i_summary_12_total_revenue_cy), MAX(part_i_summary_12_total_revenue_cy), AVG(part_i_summary_12_total_revenue_cy) FROM nonprofits WHERE part_i_summary_12_total_revenue_cy > 0")
        income_stats = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(DISTINCT st) FROM nonprofits")
        st_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "total_records": total_count,
            "income_stats": {
                "min": income_stats[0],
                "max": income_stats[1],
                "avg": income_stats[2]
            },
            "states_count": st_count,
            "supported_formats": ["CSV", "JSON", "Excel"],
            "max_export_limit": 10000
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 