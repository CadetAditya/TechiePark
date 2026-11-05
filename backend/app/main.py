import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.app.config import settings
from backend.app.routers import auth
from backend.app.database import init_db, test_mysql_connection, DB_MODE

# Resolve frontend path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Techie Park - Student Collaboration & Teammate Discovery Platform"
)

# CORS configuration for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication Routes
app.include_router(auth.router)

@app.on_event("startup")
def on_startup():
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    # Attempt to initialize MySQL database tables
    init_db()

@app.get("/api/health", tags=["System"])
def health_check():
    """Health check endpoint to verify backend and database connection."""
    from backend.app.database import DB_MODE
    mysql_live = test_mysql_connection()
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "database": {
            "active_mode": DB_MODE,
            "mysql_accessible": mysql_live,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "database_name": settings.DB_NAME
        }
    }

# Mount static subdirectories so relative paths work directly
if FRONTEND_DIR.exists():
    css_dir = FRONTEND_DIR / "css"
    js_dir = FRONTEND_DIR / "js"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse({"message": "Techie Park API is running. index.html not found."})
