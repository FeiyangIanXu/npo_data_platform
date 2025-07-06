from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from typing import Optional, List, Dict, Any
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import sqlite3

# 创建FastAPI应用
app = FastAPI(
    title="IRS非营利组织数据平台",
    description="提供IRS Form 990等公开数据的查询和分析服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DATABASE_URL = "sqlite:///./irs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# JWT配置
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 安全配置
security = HTTPBearer()

def get_db():
    """数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的Token")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "IRS非营利组织数据平台API", 
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.post("/api/register")
async def register(username: str, password: str):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM users WHERE username = :username"), {"username": username})
            if result.fetchone():
                raise HTTPException(status_code=409, detail="用户名已存在")
            
            # 加密密码
            password_hash = get_password_hash(password)
            
            # 插入新用户
            conn.execute(text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"), 
                        {"username": username, "password_hash": password_hash})
            conn.commit()
            
        return {"message": "注册成功", "username": username}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

@app.post("/api/login")
async def login(username: str, password: str):
    """用户登录"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT password_hash FROM users WHERE username = :username"), {"username": username})
            user = result.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            
            password_hash = user[0]
            if not verify_password(password, password_hash):
                raise HTTPException(status_code=401, detail="用户名或密码错误")
            
            # 创建访问令牌
            access_token = create_access_token(data={"sub": username})
            
        return {"access_token": access_token, "token_type": "bearer", "username": username}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@app.get("/api/fields")
async def get_available_fields():
    """获取所有可用字段"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(nonprofits)"))
            columns = result.fetchall()
            fields = []
            for col in columns:
                fields.append({
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default": col[4],
                    "primary_key": bool(col[5])
                })
            return {"fields": fields, "count": len(fields)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取字段信息失败: {str(e)}")

@app.get("/api/query")
async def query_data(
    organization_name: Optional[str] = Query(None, description="组织名称"),
    ein: Optional[str] = Query(None, description="EIN号码"),
    st: Optional[str] = Query(None, description="州"),
    city: Optional[str] = Query(None, description="城市"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100)
):
    """查询非营利组织数据（支持分页）"""
    try:
        offset = (page - 1) * page_size
        
        # 构建查询条件
        conditions = []
        params = {}
        
        if organization_name:
            conditions.append("campus LIKE :campus")
            params["campus"] = f"%{organization_name}%"
        
        if ein:
            conditions.append("form_990_top_block_box_d_ein_cy LIKE :ein")
            params["ein"] = f"%{ein}%"
        
        if st:
            conditions.append("st LIKE :st")
            params["st"] = f"%{st}%"
        
        if city:
            conditions.append("city LIKE :city")
            params["city"] = f"%{city}%"
        
        # 构建SQL查询
        sql = "SELECT * FROM nonprofits"
        count_sql = "SELECT COUNT(*) FROM nonprofits"
        
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            sql += where_clause
            count_sql += where_clause
        
        # 获取总数
        with engine.connect() as conn:
            count_result = conn.execute(text(count_sql), params)
            count_row = count_result.fetchone()
            total = count_row[0] if count_row else 0
            
            # 添加分页
            sql += f" LIMIT {page_size} OFFSET {offset}"
            
            # 执行查询
            result = conn.execute(text(sql), params)
            rows = result.fetchall()
            
            # 转换为字典列表
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                "data": data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@app.get("/api/statistics")
async def get_statistics():
    """获取数据统计信息"""
    try:
        with engine.connect() as conn:
            # 总记录数
            total_result = conn.execute(text("SELECT COUNT(*) as total FROM nonprofits"))
            total_row = total_result.fetchone()
            total = total_row[0] if total_row else 0
            
            # 州分布
            state_result = conn.execute(text("""
                SELECT st, COUNT(*) as count 
                FROM nonprofits 
                WHERE st IS NOT NULL AND st != '' 
                GROUP BY st 
                ORDER BY count DESC 
                LIMIT 10
            """))
            top_states = [{"state": row[0], "count": row[1]} for row in state_result.fetchall()]
            
            # 城市分布
            city_result = conn.execute(text("""
                SELECT city, COUNT(*) as count 
                FROM nonprofits 
                WHERE city IS NOT NULL AND city != '' 
                GROUP BY city 
                ORDER BY count DESC 
                LIMIT 10
            """))
            top_cities = [{"city": row[0], "count": row[1]} for row in city_result.fetchall()]
            
            # 收入统计
            revenue_result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_orgs,
                    MAX(CAST(REPLACE(REPLACE(part_i_summary_12_total_revenue_cy, '$', ''), ',', '') AS REAL)) as max_revenue
                FROM nonprofits 
                WHERE part_i_summary_12_total_revenue_cy IS NOT NULL AND part_i_summary_12_total_revenue_cy != ''
            """))
            revenue_stats = revenue_result.fetchone()
            
            return {
                "total_records": total,
                "top_states": top_states,
                "top_cities": top_cities,
                "revenue_stats": {
                    "total_organizations": revenue_stats[0] if revenue_stats and revenue_stats[0] is not None else 0,
                    "max_revenue": revenue_stats[1] if revenue_stats and revenue_stats[1] is not None else 0
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@app.get("/api/search")
async def search_organizations(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, description="返回结果数量", ge=1, le=100)
):
    """搜索组织"""
    try:
        sql = """
            SELECT campus, form_990_top_block_box_d_ein_cy, st, city, part_i_summary_12_total_revenue_cy
            FROM nonprofits 
            WHERE campus LIKE :query 
               OR form_990_top_block_box_d_ein_cy LIKE :query 
               OR st LIKE :query 
               OR city LIKE :query
            LIMIT :limit
        """
        
        with engine.connect() as conn:
            result = conn.execute(text(sql), {"query": f"%{q}%", "limit": limit})
            rows = result.fetchall()
            
            data = []
            for row in rows:
                data.append({
                    "organization_name": row[0],  # campus
                    "ein": row[1],  # form_990_top_block_box_d_ein_cy
                    "state": row[2],  # st
                    "city": row[3],  # city
                    "total_revenue": row[4]  # part_i_summary_12_total_revenue_cy
                })
            
            return {"results": data, "count": len(data)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.get("/api/export")
async def export_data(
    organization_name: Optional[str] = Query(None, description="组织名称"),
    ein: Optional[str] = Query(None, description="EIN号码"),
    st: Optional[str] = Query(None, description="州"),
    city: Optional[str] = Query(None, description="城市"),
    format: str = Query("csv", description="导出格式", regex="^(csv|excel)$")
):
    """导出数据为CSV或Excel格式"""
    try:
        # 构建查询条件
        conditions = []
        params = {}
        
        if organization_name:
            conditions.append("campus LIKE :campus")
            params["campus"] = f"%{organization_name}%"
        
        if ein:
            conditions.append("form_990_top_block_box_d_ein_cy LIKE :ein")
            params["ein"] = f"%{ein}%"
        
        if st:
            conditions.append("st LIKE :st")
            params["st"] = f"%{st}%"
        
        if city:
            conditions.append("city LIKE :city")
            params["city"] = f"%{city}%"
        
        # 构建SQL查询
        sql = "SELECT * FROM nonprofits"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        # 执行查询
        with engine.connect() as conn:
            result = conn.execute(text(sql), params)
            rows = result.fetchall()
            columns = list(result.keys())
            
            if format == "csv":
                # 生成CSV内容
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入表头
                writer.writerow(columns)
                
                # 写入数据
                for row in rows:
                    writer.writerow(row)
                
                csv_content = output.getvalue()
                output.close()
                
                return JSONResponse(
                    content={"csv_data": csv_content},
                    headers={"Content-Disposition": "attachment; filename=nonprofits_data.csv"}
                )
            elif format == "excel":
                # 简化Excel导出，返回CSV格式
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # 写入表头
                writer.writerow(columns)
                
                # 写入数据
                for row in rows:
                    writer.writerow(row)
                
                csv_content = output.getvalue()
                output.close()
                
                return JSONResponse(
                    content={"csv_data": csv_content},
                    headers={"Content-Disposition": "attachment; filename=nonprofits_data.csv"}
                )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

@app.get("/api/available-years")
async def get_available_years():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT DISTINCT from_propublica_fy_ending_month_year_12_2023 as year
                FROM nonprofits 
                WHERE from_propublica_fy_ending_month_year_12_2023 IS NOT NULL
                ORDER BY year DESC
            """))
            years = [row[0] for row in result.fetchall()]
            return {"years": years}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/available-states")
async def get_available_states(year: str = Query(None)):
    try:
        with engine.connect() as conn:
            if year:
                result = conn.execute(text("""
                    SELECT DISTINCT st as state, COUNT(*) as count
                    FROM nonprofits 
                    WHERE st IS NOT NULL AND from_propublica_fy_ending_month_year_12_2023 = :year
                    GROUP BY st
                    ORDER BY st
                """), {"year": year})
            else:
                result = conn.execute(text("""
                    SELECT DISTINCT st as state, COUNT(*) as count
                    FROM nonprofits 
                    WHERE st IS NOT NULL
                    GROUP BY st
                    ORDER BY st
                """))
            states = [{"state": row[0], "count": row[1]} for row in result.fetchall()]
            return {"states": states}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/available-cities")
async def get_available_cities(year: str = Query(None), state: str = Query(None)):
    try:
        with engine.connect() as conn:
            query = """
                SELECT DISTINCT city, COUNT(*) as count
                FROM nonprofits 
                WHERE city IS NOT NULL
            """
            params = {}
            
            if year:
                query += " AND from_propublica_fy_ending_month_year_12_2023 = :year"
                params["year"] = year
            
            if state:
                query += " AND st = :state"
                params["state"] = state
                
            query += " GROUP BY city ORDER BY city"
            
            result = conn.execute(text(query), params)
            cities = [{"city": row[0], "count": row[1]} for row in result.fetchall()]
            return {"cities": cities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/field-info")
async def get_field_info():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(nonprofits)"))
            fields = []
            
            for row in result.fetchall():
                field_name = row[1]
                field_type = row[2]
                
                # 创建字段的用户友好名称
                display_name = format_field_name(field_name)
                category = categorize_field(field_name)
                
                fields.append({
                    "field_name": field_name,
                    "display_name": display_name,
                    "category": category,
                    "type": field_type
                })
            
            return {"fields": fields}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/step1-filter")
async def step1_filter(filter_data: dict):
    try:
        with engine.connect() as conn:
            query = "SELECT * FROM nonprofits WHERE 1=1"
            params = {}
            
            # 年份筛选
            if filter_data.get("year"):
                query += " AND from_propublica_fy_ending_month_year_12_2023 = :year"
                params["year"] = filter_data["year"]
            
            # 地理位置筛选
            if filter_data.get("state"):
                query += " AND st = :state"
                params["state"] = filter_data["state"]
            
            if filter_data.get("city"):
                query += " AND city = :city"
                params["city"] = filter_data["city"]
            
            # 财务规模筛选
            if filter_data.get("min_revenue"):
                query += " AND CAST(part_i_summary_12_total_revenue_cy AS REAL) >= :min_revenue"
                params["min_revenue"] = filter_data["min_revenue"]
            
            if filter_data.get("max_revenue"):
                query += " AND CAST(part_i_summary_12_total_revenue_cy AS REAL) <= :max_revenue"
                params["max_revenue"] = filter_data["max_revenue"]
            
            if filter_data.get("min_assets"):
                query += " AND CAST(part_i_summary_20_total_assets_cy AS REAL) >= :min_assets"
                params["min_assets"] = filter_data["min_assets"]
            
            if filter_data.get("max_assets"):
                query += " AND CAST(part_i_summary_20_total_assets_cy AS REAL) <= :max_assets"
                params["max_assets"] = filter_data["max_assets"]
            
            # 运营规模筛选
            if filter_data.get("min_ilu"):
                query += " AND CAST(part_x_balance_sheet_ilu AS REAL) >= :min_ilu"
                params["min_ilu"] = filter_data["min_ilu"]
            
            if filter_data.get("min_alu"):
                query += " AND CAST(part_x_balance_sheet_alu AS REAL) >= :min_alu"
                params["min_alu"] = filter_data["min_alu"]
            
            # 执行查询
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            columns = list(result.keys())
            
            # 格式化结果
            organizations = []
            for row in rows:
                org = dict(zip(columns, row))
                organizations.append({
                    "ein": org.get("form_990_top_block_box_d_ein_cy"),
                    "name": org.get("campus", "Unknown"),
                    "city": org.get("city"),
                    "state": org.get("st"),
                    "total_revenue": org.get("part_i_summary_12_total_revenue_cy"),
                    "total_assets": org.get("part_i_summary_20_total_assets_cy"),
                    "ilu": org.get("part_x_balance_sheet_ilu"),
                    "alu": org.get("part_x_balance_sheet_alu")
                })
            
            return {
                "organizations": organizations,
                "total_count": len(organizations),
                "filter_summary": filter_data
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/step2-filter")
async def step2_filter(filter_data: dict):
    try:
        with engine.connect() as conn:
            selected_organizations = filter_data.get("selected_organizations", [])
            search_type = filter_data.get("search_type", "name")  # "name" or "ein"
            search_terms = filter_data.get("search_terms", [])
            
            if filter_data.get("select_all"):
                # 如果选择全部，返回第一步的结果
                return await step1_filter(filter_data.get("step1_filters", {}))
            
            if search_type == "ein":
                placeholders = ",".join([":ein_" + str(i) for i in range(len(search_terms))])
                query = f"""
                    SELECT * FROM nonprofits 
                    WHERE form_990_top_block_box_d_ein_cy IN ({placeholders})
                """
                params = {f"ein_{i}": term for i, term in enumerate(search_terms)}
            else:
                # 按名称搜索
                placeholders = ",".join([":name_" + str(i) for i in range(len(search_terms))])
                query = f"""
                    SELECT * FROM nonprofits 
                    WHERE campus IN ({placeholders})
                """
                params = {f"name_{i}": term for i, term in enumerate(search_terms)}
            
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            columns = list(result.keys())
            
            organizations = []
            for row in rows:
                org = dict(zip(columns, row))
                organizations.append({
                    "ein": org.get("form_990_top_block_box_d_ein_cy"),
                    "name": org.get("campus", "Unknown"),
                    "city": org.get("city"),
                    "state": org.get("st"),
                    "total_revenue": org.get("part_i_summary_12_total_revenue_cy"),
                    "total_assets": org.get("part_i_summary_20_total_assets_cy")
                })
            
            return {
                "organizations": organizations,
                "total_count": len(organizations)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/final-query")
async def final_query(query_data: dict):
    try:
        with engine.connect() as conn:
            selected_eins = query_data.get("selected_eins", [])
            selected_fields = query_data.get("selected_fields", [])
            
            if not selected_eins:
                raise HTTPException(status_code=400, detail="No organizations selected")
            
            if not selected_fields:
                selected_fields = ["form_990_top_block_box_d_ein_cy", "campus", "city", "st"]
            
            # 构建查询
            fields_str = ", ".join(selected_fields)
            placeholders = ",".join([":ein_" + str(i) for i in range(len(selected_eins))])
            
            query = f"""
                SELECT {fields_str}
                FROM nonprofits 
                WHERE form_990_top_block_box_d_ein_cy IN ({placeholders})
            """
            
            params = {f"ein_{i}": ein for i, ein in enumerate(selected_eins)}
            result = conn.execute(text(query), params)
            rows = result.fetchall()
            columns = list(result.keys())
            
            data = [dict(zip(columns, row)) for row in rows]
            
            return {
                "data": data,
                "columns": columns,
                "total_count": len(data)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 辅助函数
def format_field_name(field_name):
    """将字段名转换为用户友好的显示名称"""
    # 移除前缀，格式化名称
    name = field_name.replace("_", " ").title()
    
    # 特殊处理常见缩写
    replacements = {
        "Cy": "Current Year",
        "Py": "Previous Year",
        "Ein": "EIN",
        "Ceo": "CEO",
        "Cfo": "CFO",
        "Ilu": "Independent Living Units",
        "Alu": "Assisted Living Units",
        "Ncb": "Nursing Care Beds"
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    return name

def categorize_field(field_name):
    """将字段按类别分组"""
    if any(x in field_name for x in ["revenue", "income", "grants", "expenses"]):
        return "财务数据"
    elif any(x in field_name for x in ["compensation", "salary", "ceo", "cfo"]):
        return "薪酬数据"
    elif any(x in field_name for x in ["assets", "liabilities", "balance"]):
        return "资产负债"
    elif any(x in field_name for x in ["ilu", "alu", "ncb", "units"]):
        return "运营数据"
    elif any(x in field_name for x in ["city", "st", "state", "ein"]):
        return "基本信息"
    else:
        return "其他"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 