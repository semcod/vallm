"""Tickets router — ticket-driven auto-PR generation.

Split from the original monolith into:
  models.py  — Pydantic schemas + shared helpers
  crud.py    — CRUD endpoints (create, list, get, update, delete, search, stats)
  redsl.py   — reDSL processing + background PR task + status polling
  webhook.py — PR webhook handler + bulk operations
"""

from fastapi import APIRouter

from .crud import router as crud_router
from .redsl import router as redsl_router
from .webhook import router as webhook_router

router = APIRouter(tags=["tickets"])

router.include_router(crud_router, prefix="/api/tickets")
router.include_router(redsl_router, prefix="/api/tickets")
router.include_router(webhook_router, prefix="/api/tickets")
