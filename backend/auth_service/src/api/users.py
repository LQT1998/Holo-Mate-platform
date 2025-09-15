from fastapi import APIRouter


router = APIRouter(tags=["Users"])


# TODO: Add user endpoints when needed by roadmap tests


@router.get("/me")
async def get_me():
    # TODO: sau này thay bằng get_current_user
    return {"id": 1, "email": "test@example.com"}
