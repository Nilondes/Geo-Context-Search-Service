from fastapi import APIRouter
from app.models.schemas import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    return SearchResponse(results=[])
