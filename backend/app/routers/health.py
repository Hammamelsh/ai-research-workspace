from fastapi import APIRouter, Depends
from app.core.config import get_settings, Settings

router = APIRouter()


@router.get("/health", tags=["System"])
def health_check(settings: Settings = Depends(get_settings)):
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }