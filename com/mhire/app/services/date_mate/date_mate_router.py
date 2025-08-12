from fastapi import APIRouter, HTTPException
from com.mhire.app.services.date_mate.date_mate import DateMate
from com.mhire.app.services.date_mate.date_mate_schema import ChatRequest
from com.mhire.app.config.config import Config

config = Config()
router = APIRouter(
    prefix="/date-mate",
    tags=["date-mate"],
    responses={404: {"description": "Not found"}},
)

date_mate_service = DateMate(config)

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await date_mate_service.app.router.routes[-1].endpoint(request)
        return response
    except DateMateError as e:
        raise HTTPException(status_code=500, detail=str(e))
