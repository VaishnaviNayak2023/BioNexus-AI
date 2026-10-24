from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers.projects import router as projects_router
from routers.analyses import router as analyses_router
from database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown

app = FastAPI(
    title="eDNA Taxonomy Workbench API",
    description="API for zero-shot eDNA taxonomy and functional traits",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(analyses_router)

@app.get("/")
async def root():
    return {"message": "eDNA Taxonomy Workbench API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
