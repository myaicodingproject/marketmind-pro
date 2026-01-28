from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import traceback

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # Log the full traceback for debugging
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": "Please contact support with this error ID"
        }
    )

class ErrorHandler:
    @staticmethod
    def validation_error(message: str):
        raise HTTPException(status_code=400, detail=message)
    
    @staticmethod
    def not_found(resource: str):
        raise HTTPException(status_code=404, detail=f"{resource} not found")
    
    @staticmethod
    def unauthorized(message: str = "Authentication required"):
        raise HTTPException(status_code=401, detail=message)
    
    @staticmethod
    def forbidden(message: str = "Access denied"):
        raise HTTPException(status_code=403, detail=message)