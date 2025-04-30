from fastapi import APIRouter

router = APIRouter()

@router.get("/me")
def get_my_profile():
    return {"message": "User profile endpoint (under construction)"}
