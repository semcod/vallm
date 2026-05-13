"""Tickets CRUD endpoints."""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException

from db_session import get_db
from db_module.tickets_orm import (
    create_ticket,
    get_tickets_by_tenant,
    get_ticket,
    update_ticket,
    delete_ticket,
    get_tickets_by_repo,
    count_tickets_by_status,
    get_tickets_requiring_action,
    get_ticket_stats,
    search_tickets,
)
from routers.auth import get_current_user

from .models import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TicketStatsResponse,
    _get_tenant_for_user,
)

router = APIRouter(tags=["tickets"])


@router.post("", response_model=TicketResponse)
async def create_new_ticket(
    data: TicketCreate,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> TicketResponse:
    """Create new ticket for auto-PR generation."""
    tenant = _get_tenant_for_user(user, db)

    ticket = create_ticket(
        db=db,
        tenant_id=tenant["id"],
        payload={
            "title": data.title,
            "repo": data.repo,
            "provider": data.provider,
            "description": data.description,
            "ticket_type": data.ticket_type,
            "priority": data.priority,
        },
    )

    return TicketResponse(**ticket)


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    status: Optional[str] = None,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> TicketListResponse:
    """List all tickets for current user."""
    tenant = _get_tenant_for_user(user, db)

    tickets = get_tickets_by_tenant(db, tenant["id"], status=status)
    by_status = count_tickets_by_status(db, tenant["id"])

    return TicketListResponse(
        tickets=[TicketResponse(**t) for t in tickets],
        total=len(tickets),
        by_status=by_status,
    )


@router.get("/stats", response_model=TicketStatsResponse)
async def get_stats(
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> TicketStatsResponse:
    """Get ticket statistics for current user."""
    tenant = _get_tenant_for_user(user, db)
    stats = get_ticket_stats(db, tenant["id"])
    return TicketStatsResponse(**stats)


@router.get("/search")
async def search_tickets_endpoint(
    q: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> List[TicketResponse]:
    """Search tickets by title or description."""
    tenant = _get_tenant_for_user(user, db)
    tickets = search_tickets(db, tenant["id"], q)
    return [TicketResponse(**t) for t in tickets]


@router.get("/repo/{repo}")
async def get_tickets_for_repo(
    repo: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> List[TicketResponse]:
    """Get all tickets for a specific repository."""
    tenant = _get_tenant_for_user(user, db)
    tickets = get_tickets_by_repo(db, tenant["id"], repo)
    return [TicketResponse(**t) for t in tickets]


@router.get("/requiring-action")
async def get_action_required_tickets(
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> List[TicketResponse]:
    """Get tickets that need auto-PR generation (open/analyzing status)."""
    tenant = _get_tenant_for_user(user, db)
    tickets = get_tickets_requiring_action(db, tenant["id"])
    return [TicketResponse(**t) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_single_ticket(
    ticket_id: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> TicketResponse:
    """Get single ticket by ID."""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    # Verify tenant ownership
    tenant = _get_tenant_for_user(user, db)
    if ticket["tenant_id"] != tenant["id"]:
        raise HTTPException(403, "Not authorized to access this ticket")

    return TicketResponse(**ticket)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_existing_ticket(
    ticket_id: str,
    data: TicketUpdate,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> TicketResponse:
    """Update ticket fields."""
    # Verify ownership
    existing = get_ticket(db, ticket_id)
    if not existing:
        raise HTTPException(404, "Ticket not found")

    tenant = _get_tenant_for_user(user, db)
    if existing["tenant_id"] != tenant["id"]:
        raise HTTPException(403, "Not authorized to modify this ticket")

    updates = {k: v for k, v in data.dict().items() if v is not None}
    updated = update_ticket(db, ticket_id, updates)

    if not updated:
        raise HTTPException(500, "Failed to update ticket")

    return TicketResponse(**updated)


@router.delete("/{ticket_id}")
async def delete_existing_ticket(
    ticket_id: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> Dict:
    """Delete (soft delete) a ticket."""
    existing = get_ticket(db, ticket_id)
    if not existing:
        raise HTTPException(404, "Ticket not found")

    tenant = _get_tenant_for_user(user, db)
    if existing["tenant_id"] != tenant["id"]:
        raise HTTPException(403, "Not authorized to delete this ticket")

    success = delete_ticket(db, ticket_id)
    if not success:
        raise HTTPException(500, "Failed to delete ticket")

    return {"status": "deleted", "ticket_id": ticket_id}
