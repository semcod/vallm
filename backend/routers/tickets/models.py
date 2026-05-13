"""Tickets Pydantic models and shared helpers."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from database import get_or_create_tenant


# ─── Pydantic Models ───────────────────────────────────────────────────────────


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    repo: str = Field(..., min_length=1)
    provider: str = "github"
    description: str = ""
    ticket_type: str = Field(..., pattern="^(feature|bugfix)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(
        None, pattern="^(open|analyzing|in_progress|pr_created|merged|closed|error)$"
    )
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    pr_url: Optional[str] = None
    pr_branch: Optional[str] = None
    pr_number: Optional[int] = None


class TicketResponse(BaseModel):
    ticket_id: str
    repo: str
    provider: str
    title: str
    description: str
    ticket_type: str
    status: str
    priority: str
    pr_url: Optional[str]
    pr_branch: Optional[str]
    pr_number: Optional[int]
    redsl_decisions: List[Dict]
    files_modified: List[str]
    error_message: str
    created_at: str
    updated_at: str
    resolved_at: Optional[str]


class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    by_status: Dict[str, int]


class TicketStatsResponse(BaseModel):
    total: int
    open: int
    in_progress: int
    pr_created: int
    merged: int
    by_type: Dict[str, int]
    success_rate: float


class RedslAutoPRRequest(BaseModel):
    project_path: str
    max_actions: int = 10
    dry_run: bool = False
    auto_create_pr: bool = True


class RedslAutoPRResponse(BaseModel):
    status: str
    ticket_id: str
    decisions_count: int
    files_modified: List[str]
    pr_url: Optional[str]
    branch: Optional[str]
    error: Optional[str]


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _get_tenant_for_user(user: dict, db) -> Dict:
    """Get or create tenant for authenticated user."""
    provider_user_id = str(
        user.get("github_id") or user.get("gitlab_id") or user.get("gitea_id") or user.get("id")
    )
    return get_or_create_tenant(
        provider=user.get("provider", "github"),
        provider_user_id=provider_user_id,
        login=user.get("login", ""),
        name=user.get("name", ""),
        avatar_url=user.get("avatar_url", ""),
    )
