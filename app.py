from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.osm_service import get_restaurants_by_radius

app = FastAPI()

class CityQuery(BaseModel):
    cities: List[str]
    radius: Optional[int] = 1000  # default radius in meters

@app.post("/restaurants")
def restaurants_endpoint(query: CityQuery):
    try:
        results = get_restaurants_by_radius(query.cities, query.radius)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))