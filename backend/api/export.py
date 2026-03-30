from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import csv
import json
import io
from datetime import datetime

from db_utils import get_connection, get_table_columns, resolve_table_name


router = APIRouter()


def get_export_data(filters: Optional[Dict[str, Any]] = None, limit: int = 10000, dataset: str = "default"):
    try:
        table_name = resolve_table_name(dataset)
        valid_columns = set(get_table_columns(table_name))

        with get_connection() as conn:
            cursor = conn.cursor()
            sql = f'SELECT * FROM "{table_name}"'
            params = []

            if filters:
                conditions = []
                for key, value in filters.items():
                    if key not in valid_columns or value is None:
                        continue
                    if isinstance(value, (list, tuple)):
                        placeholders = ",".join(["?" for _ in value])
                        conditions.append(f"{key} IN ({placeholders})")
                        params.extend(value)
                    else:
                        conditions.append(f"{key} = ?")
                        params.append(value)
                if conditions:
                    sql += " WHERE " + " AND ".join(conditions)

            sql += f" LIMIT {limit}"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data: {str(e)}")


@router.post("/export/csv")
async def export_csv(filters: Optional[Dict[str, Any]] = None, limit: int = 10000, dataset: str = "default"):
    try:
        data = get_export_data(filters, limit, dataset)
        if not data:
            raise HTTPException(status_code=404, detail="No data found")

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dataset}_nonprofits_export_{timestamp}.csv"
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/json")
async def export_json(filters: Optional[Dict[str, Any]] = None, limit: int = 10000, dataset: str = "default"):
    try:
        data = get_export_data(filters, limit, dataset)
        if not data:
            raise HTTPException(status_code=404, detail="No data found")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dataset}_nonprofits_export_{timestamp}.json"
        return Response(
            content=json.dumps(data, indent=2, ensure_ascii=False),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export/excel")
async def export_excel(filters: Optional[Dict[str, Any]] = None, limit: int = 10000, dataset: str = "default"):
    try:
        try:
            from openpyxl import Workbook
        except ImportError:
            raise HTTPException(status_code=500, detail="Excel export requires openpyxl. Install with: pip install openpyxl")

        data = get_export_data(filters, limit, dataset)
        if not data:
            raise HTTPException(status_code=404, detail="No data found")

        wb = Workbook()
        ws = wb.active
        ws.title = "Nonprofits Data"

        headers = list(data[0].keys())
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)

        for row_num, record in enumerate(data, 2):
            for col_num, header in enumerate(headers, 1):
                ws.cell(row=row_num, column=col_num, value=record.get(header, ""))

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dataset}_nonprofits_export_{timestamp}.xlsx"
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/status")
async def export_status(dataset: str = "default"):
    try:
        table_name = resolve_table_name(dataset)
        available_columns = set(get_table_columns(table_name))

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            total_count = cursor.fetchone()[0]

            income_stats = (None, None, None)
            if "part_i_summary_12_total_revenue_cy" in available_columns:
                cursor.execute(
                    f'SELECT MIN(part_i_summary_12_total_revenue_cy), MAX(part_i_summary_12_total_revenue_cy), AVG(part_i_summary_12_total_revenue_cy) FROM "{table_name}" WHERE part_i_summary_12_total_revenue_cy > 0'
                )
                income_stats = cursor.fetchone()

            cursor.execute(f'SELECT COUNT(DISTINCT st) FROM "{table_name}"')
            state_count = cursor.fetchone()[0]

        return {
            "success": True,
            "dataset": dataset,
            "total_records": total_count,
            "income_stats": {
                "min": income_stats[0],
                "max": income_stats[1],
                "avg": income_stats[2],
            },
            "states_count": state_count,
            "supported_formats": ["CSV", "JSON", "Excel"],
            "max_export_limit": 10000,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
