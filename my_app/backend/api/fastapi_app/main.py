"""FastAPI application factory that wires routers and shared settings."""

from fastapi import FastAPI

from .routers import show_plans

web_title = "Synthetic indoor layout planner"

app = FastAPI(title=web_title)
app.include_router(show_plans.router)
