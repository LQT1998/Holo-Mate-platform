from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str, *, status_code: int | None = None, code: str | None = None):
        super().__init__(message)
        if status_code:
            self.status_code = status_code
        if code:
            self.code = code
        self.message = message


def as_json(exc: AppError) -> dict:
    return {"error": exc.code, "message": exc.message}


async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(as_json(exc), status_code=exc.status_code)
