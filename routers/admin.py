from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
def get_admin_stats():
    return {"message": "Admin stats endpoint (under construction)"}
