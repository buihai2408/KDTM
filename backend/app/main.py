"""
Personal Finance BI System - Backend API
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    auth_router,
    categories_router,
    wallets_router,
    transactions_router,
    budgets_router,
    summary_router,
    automation_router
)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Personal Finance Intelligent Management System with BI capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
        "http://n8n:5678",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(wallets_router)
app.include_router(transactions_router)
app.include_router(budgets_router)
app.include_router(summary_router)
app.include_router(automation_router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Personal Finance BI System API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy"}
