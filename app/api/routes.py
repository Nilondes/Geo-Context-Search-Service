from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.db import AsyncSessionLocal
from app.models.schemas import SearchRequest, SearchResponse
from app.services.geo_service import GeoService

router = APIRouter()


async def get_session() -> AsyncSession:
    """
    Dependency: async DB session.
    """
    async with AsyncSessionLocal() as session:
        yield session


@router.post("/search", response_model=SearchResponse, status_code=status.HTTP_200_OK)
async def search_endpoint(
    request: SearchRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchResponse:
    """
    High-level endpoint: parse context -> geo search -> return results.
    """
    try:
        service = GeoService(session)
        response = await service.search(request)
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
