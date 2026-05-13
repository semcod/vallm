"""Tickets reDSL auto-PR integration endpoints."""

from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from db_session import get_db
from db_module.tickets_orm import (
    get_ticket,
    update_ticket,
    update_ticket_redsl_results,
    mark_ticket_error,
)
from routers.auth import get_current_user
from services.redsl_client import RedslClient

from .models import (
    RedslAutoPRRequest,
    RedslAutoPRResponse,
    _get_tenant_for_user,
)

router = APIRouter(tags=["tickets"])


@router.post("/{ticket_id}/process", response_model=RedslAutoPRResponse)
async def process_ticket_with_redsl(
    ticket_id: str,
    data: RedslAutoPRRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> RedslAutoPRResponse:
    """
    Process ticket with reDSL engine to auto-generate PR.

    Flow:
      1. Analyze ticket description with reDSL decide()
      2. Run reDSL refactor() on identified files
      3. Create branch and commit changes
      4. Open PR on GitHub
      5. Update ticket with PR info
    """
    # Verify ticket ownership
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    tenant = _get_tenant_for_user(user, db)
    if ticket["tenant_id"] != tenant["id"]:
        raise HTTPException(403, "Not authorized")

    # Get GitHub token
    token = user.get("github_token", "")
    if not token:
        raise HTTPException(401, "GitHub token required for auto-PR")

    # Update status to analyzing
    update_ticket(db, ticket_id, {"status": "analyzing"})

    try:
        # Initialize reDSL client
        redsl = RedslClient()
        available = await redsl.health()

        if not available:
            mark_ticket_error(db, ticket_id, "reDSL engine not available")
            return RedslAutoPRResponse(
                status="redsl_unavailable",
                ticket_id=ticket_id,
                decisions_count=0,
                files_modified=[],
                error="reDSL engine is not running",
            )

        # Step 1: Decide — analyze where to make changes based on ticket
        decide_result = await redsl.decide(
            project_path=data.project_path,
            description=ticket["description"],
            ticket_type=ticket["ticket_type"],
        )

        target_files = decide_result.get("target_files", [])
        if not target_files:
            update_ticket(db, ticket_id, {"status": "open"})  # Reset to open
            return RedslAutoPRResponse(
                status="no_targets",
                ticket_id=ticket_id,
                decisions_count=0,
                files_modified=[],
                error="No target files identified for this ticket",
            )

        # Step 2: Refactor — apply changes
        refactor_result = await redsl.refactor(
            project_path=data.project_path,
            target_files=target_files,
            max_actions=data.max_actions,
            dry_run=data.dry_run,
            ticket_type=ticket["ticket_type"],
            description=ticket["description"],
        )

        decisions = refactor_result.get("decisions", [])
        if not decisions and not data.dry_run:
            update_ticket(db, ticket_id, {"status": "open"})
            return RedslAutoPRResponse(
                status="no_changes",
                ticket_id=ticket_id,
                decisions_count=0,
                files_modified=[],
                error="No refactoring decisions made",
            )

        # Update ticket with reDSL results
        modified_files = [d.get("target_file", "") for d in decisions if d.get("target_file")]
        update_ticket_redsl_results(db, ticket_id, decisions, modified_files)

        # Step 3: Create PR (if not dry_run)
        if data.auto_create_pr and not data.dry_run:
            # Queue background task for PR creation
            background_tasks.add_task(
                _create_pr_for_ticket,
                ticket_id,
                ticket["repo"],
                ticket["provider"],
                data.project_path,
                decisions,
                modified_files,
                token,
                tenant["id"],
            )

            return RedslAutoPRResponse(
                status="processing",
                ticket_id=ticket_id,
                decisions_count=len(decisions),
                files_modified=modified_files,
                pr_url=None,  # Will be updated by background task
                branch=None,
            )

        # Dry run — just return analysis
        return RedslAutoPRResponse(
            status="dry_run" if data.dry_run else "analyzed",
            ticket_id=ticket_id,
            decisions_count=len(decisions),
            files_modified=modified_files,
        )

    except Exception as e:
        mark_ticket_error(db, ticket_id, str(e))
        return RedslAutoPRResponse(
            status="error", ticket_id=ticket_id, decisions_count=0, files_modified=[], error=str(e)
        )


async def _create_pr_for_ticket(
    ticket_id: str,
    repo: str,
    provider: str,
    project_path: str,
    decisions: List[Dict],
    files_modified: List[str],
    token: str,
    tenant_id: int,
):
    """Background task to create PR for processed ticket."""
    from worker.tasks.autopr import create_auto_pr

    try:
        # Generate branch name
        branch = f"ticket-{ticket_id[:8]}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

        # Prepare patches from modified files
        patches = []
        for file_path in files_modified:
            full_path = f"{project_path}/{file_path}"
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                patches.append(
                    {
                        "path": file_path,
                        "content": content,
                    }
                )
            except Exception:
                continue  # Skip files that can't be read

        if not patches:
            mark_ticket_error(get_db().__next__(), ticket_id, "No patchable files found")
            return

        # Queue Celery task for PR creation
        result = create_auto_pr.delay(
            repo=repo,
            base_branch="main",  # TODO: detect default branch
            patches=patches,
            proposal_type=f"ticket-{ticket_id[:8]}",
            llm_prompt=f"Ticket: {ticket_id}",
            token=token,
            provider_type=provider,
        )

        # Note: Actual PR URL will be updated via webhook or polling
        # For now, mark as in_progress
        update_ticket(
            get_db().__next__(),
            ticket_id,
            {
                "status": "in_progress",
                "pr_branch": branch,
            },
        )

    except Exception as e:
        mark_ticket_error(get_db().__next__(), ticket_id, str(e))


@router.get("/{ticket_id}/status")
async def get_ticket_processing_status(
    ticket_id: str,
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
) -> Dict:
    """Get processing status for a ticket (polling endpoint)."""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    tenant = _get_tenant_for_user(user, db)
    if ticket["tenant_id"] != tenant["id"]:
        raise HTTPException(403, "Not authorized")

    return {
        "ticket_id": ticket_id,
        "status": ticket["status"],
        "pr_url": ticket["pr_url"],
        "pr_branch": ticket["pr_branch"],
        "files_modified_count": len(ticket["files_modified"]),
        "decisions_count": len(ticket["redsl_decisions"]),
        "error_message": ticket["error_message"],
        "updated_at": ticket["updated_at"],
    }
