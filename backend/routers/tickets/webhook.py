"""Tickets webhook and bulk operation endpoints."""
from typing import Dict, List

from fastapi import APIRouter, Depends

from db_session import get_db
from db_module.tickets_orm import (
    get_ticket,
    update_ticket,
)
from routers.auth import get_current_user

from .models import _get_tenant_for_user

router = APIRouter(tags=["tickets"])


@router.post("/webhook/pr-updated")
async def handle_pr_webhook(
    payload: Dict,
    db=Depends(get_db),
) -> Dict:
    """
    Webhook handler for PR status updates.
    Called by GitHub webhook when PR is opened/merged/closed.
    Updates linked ticket status accordingly.
    """
    pr_number = payload.get("pull_request", {}).get("number")
    repo = payload.get("repository", {}).get("full_name")
    action = payload.get("action")  # opened, closed, merged
    
    if not pr_number or not repo:
        return {"status": "ignored", "reason": "missing PR data"}
    
    # Find linked ticket
    from db_module.tickets_orm import get_ticket_by_pr
    ticket = get_ticket_by_pr(db, pr_number, repo)
    
    if not ticket:
        return {"status": "no_linked_ticket"}
    
    # Update ticket status based on PR action
    new_status = None
    if action == "opened":
        new_status = "pr_created"
    elif action == "closed":
        merged = payload.get("pull_request", {}).get("merged", False)
        new_status = "merged" if merged else "closed"
    
    if new_status:
        update_ticket(db, ticket["ticket_id"], {"status": new_status})
        return {"status": "updated", "ticket_id": ticket["ticket_id"], "new_status": new_status}
    
    return {"status": "no_action_needed"}


@router.post("/bulk/close")
async def bulk_close_tickets(
    ticket_ids: List[str],
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> Dict:
    """Bulk close multiple tickets."""
    tenant = _get_tenant_for_user(user, db)
    
    closed = 0
    for ticket_id in ticket_ids:
        ticket = get_ticket(db, ticket_id)
        if ticket and ticket["tenant_id"] == tenant["id"]:
            update_ticket(db, ticket_id, {"status": "closed"})
            closed += 1
    
    return {"closed": closed, "total": len(ticket_ids)}


@router.post("/bulk/reprocess")
async def bulk_reprocess_tickets(
    ticket_ids: List[str],
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> Dict:
    """Reprocess multiple tickets with reDSL."""
    tenant = _get_tenant_for_user(user, db)
    
    queued = 0
    for ticket_id in ticket_ids:
        ticket = get_ticket(db, ticket_id)
        if ticket and ticket["tenant_id"] == tenant["id"]:
            update_ticket(db, ticket_id, {"status": "open", "error_message": ""})
            queued += 1
    
    return {"queued": queued, "total": len(ticket_ids)}
