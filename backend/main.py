"""
AlgoTrade Engine — FastAPI Application
Main entry point for the REST API backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.data import router as data_router
from api.backtest import router as backtest_router
from api.signals import router as signals_router
from api.algorithms import router as algorithms_router
from api.portfolio import router as portfolio_router

app = FastAPI(
    title="AlgoTrade Engine API",
    description="Algorithmic Trading Backtester using Advanced DAA Paradigms",
    version="1.0.0",
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(data_router, prefix="/api/data", tags=["Data"])
app.include_router(backtest_router, prefix="/api/backtest", tags=["Backtest"])
app.include_router(signals_router, prefix="/api/signals", tags=["Signals"])
app.include_router(algorithms_router, prefix="/api/algorithms", tags=["Algorithms"])
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["Portfolio"])


@app.get("/")
def root():
    return {"name": "AlgoTrade Engine", "version": "1.0.0", "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
