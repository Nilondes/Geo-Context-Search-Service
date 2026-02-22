from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.db import get_session
from app.models.schemas import SearchRequest, SearchResponse
from app.services.geo_service import GeoService

router = APIRouter()


@router.post("/search", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def search_endpoint(
    request: SearchRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchResponse:
    """
    High-level endpoint: parse context -> geo search -> return results.
    """
    try:
        # Keep orchestration in the service layer; endpoint stays thin.
        service = GeoService(session)
        response = await service.search(request)
        return response
    except Exception as exc:
        # Fail fast with a generic 500 to avoid leaking internal errors.
        raise HTTPException(status_code=500, detail=str(exc))
