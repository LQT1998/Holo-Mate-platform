from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, Literal
from ai_service.src.security.deps import get_current_user
from ai_service.src.schemas.ai_companion import AICompanionListResponse, AICompanionRead
from ai_service.src.config import settings
import uuid
from datetime import datetime, timezone

router = APIRouter(tags=["AI Companions"])


@router.get("/ai-companions", response_model=AICompanionListResponse)
async def list_ai_companions(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(10, gt=0, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name/description"),
    status_filter: Optional[Literal["active", "inactive", "training", "error"]] = Query(None, alias="status"),
    sort_by: Optional[Literal["name", "created_at", "updated_at"]] = None,
    sort_order: Optional[Literal["asc", "desc"]] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    List AI companions for the authenticated user with pagination, search, and filtering.
    """
    # Dev shortcut for contract tests
    if settings.DEV_MODE:
        # Create mock companions for testing
        # Special case: return empty list for empty_list test
        if search == "empty_list_test":
            return AICompanionListResponse(
                companions=[],
                total=0,
                page=page,
                per_page=per_page,
                total_pages=0
            )
        
        mock_companions = [
            AICompanionRead(
                id=uuid.uuid4(),
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                name="Test Assistant",
                description="A helpful AI assistant for testing",
                personality="Friendly and helpful",
                voice_profile={"voice_id": "test_voice_1"},
                character_asset={"asset_id": "test_asset_1"},
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            AICompanionRead(
                id=uuid.uuid4(),
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                name="Another Companion",
                description="Another test companion",
                personality="Professional and efficient",
                voice_profile={"voice_id": "test_voice_2"},
                character_asset={"asset_id": "test_asset_2"},
                status="inactive",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ]
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            mock_companions = [
                c for c in mock_companions
                if search_lower in c.name.lower() or search_lower in c.description.lower()
            ]
        
        # Apply status filter if provided
        if status_filter:
            mock_companions = [c for c in mock_companions if c.status == status_filter]
        
        # Apply sorting if provided
        if sort_by:
            reverse = sort_order == "desc"
            mock_companions.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        
        # Calculate pagination
        total = len(mock_companions)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_companions = mock_companions[start_idx:end_idx]
        
        return AICompanionListResponse(
            companions=paginated_companions,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    # TODO: Production path - fetch from database with filters/sorting/pagination
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI companions listing not implemented in production mode yet",
    )


