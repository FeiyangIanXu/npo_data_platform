from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Import new API modules
from api.search import router as search_router
from api.export import router as export_router
from api.filter import router as filter_router

# Data models
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str

# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "sqlite:///./irs.db"

# Create FastAPI application
app = FastAPI(
    title="IRS Nonprofit Organization Data Platform",
    description="Provides query and analysis services for IRS Form 990 and other public data",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register new API routes
app.include_router(search_router, prefix="/api", tags=["Search"])
app.include_router(export_router, prefix="/api", tags=["Export"])
app.include_router(filter_router, prefix="/api", tags=["Filter"])

# Database configuration
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password encryption configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Helper functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# API endpoints
@app.get("/")
async def root():
    return {
        "message": "IRS Nonprofit Organization Data Platform API", 
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/health")
async def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.post("/api/register")
async def register(user_data: UserRegister):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM users WHERE username = :username"), {"username": user_data.username})
            if result.fetchone():
                raise HTTPException(status_code=409, detail="Username already exists")
            
            password_hash = get_password_hash(user_data.password)
            conn.execute(text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)"), 
                        {"username": user_data.username, "password_hash": password_hash})
            conn.commit()
            
        return {"message": "Registration successful", "username": user_data.username}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/login")
async def login(user_data: UserLogin):
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT password_hash FROM users WHERE username = :username"), {"username": user_data.username})
            user = result.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid username or password")
            
            password_hash = user[0]
            if not verify_password(user_data.password, password_hash):
                raise HTTPException(status_code=401, detail="Invalid username or password")
            
            access_token = create_access_token(data={"sub": user_data.username})
            
        return {"access_token": access_token, "token_type": "bearer", "username": user_data.username}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/fields")
async def get_available_fields():
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
        raise HTTPException(status_code=500, detail=f"Failed to get field information: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 