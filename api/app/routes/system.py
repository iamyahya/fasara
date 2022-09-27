from fastapi import APIRouter

from app.config import settings


router = APIRouter()


@router.get("/info")
def route_info():
    return {
        "email": settings.admin_email,
        "is_bare": settings.is_bare
    }



