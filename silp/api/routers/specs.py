from fastapi import APIRouter

router = APIRouter(
    prefix="/api/specs", tags=["specs"])

@router.get("/furniture")
async def get_furniture_specs():
    return {
        "types": ["chair", "table", "sofa", "bed"],
        "materials": ["wood", "metal", "plastic", "glass"],
        "colors": ["red", "blue", "green", "black", "white"]
    }

