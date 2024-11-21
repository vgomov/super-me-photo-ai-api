from typing import Optional
from decouple import config
from fastapi import (
    Depends,
    FastAPI, 
    HTTPException,
    Request,
    )
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from pydantic import BaseModel

import helpers
from helpers.ratelimiting import lifespan as my_ratelimit_lifespan

REDIS_URL = config('REDIS_URL')
API_KEY_HEADER = "X-API-Key"
API_ACCESS_KEY = config('API_ACCESS_KEY')

app = FastAPI(lifespan=my_ratelimit_lifespan)

@app.middleware("http")
async def custom_api_key_middleware(request:Request, call_next):
    req_key_header = request.headers.get(API_KEY_HEADER)
    if f"{req_key_header}" != API_ACCESS_KEY:
        return JSONResponse(status_code=403, content={"detail": "Invalid Key, try again."})
    response = await call_next(request)
    return response

@app.get("/", dependencies=[
    Depends(RateLimiter(times=2, seconds=5)),
    Depends(RateLimiter(times=4, seconds=20))
])
def read_root():
    # helpers.generate_image()
    return {"Hello": "World"}


class ImageGenerationRequest(BaseModel):
    prompt:str

@app.post('/generate', 
        dependencies=[
            Depends(RateLimiter(times=2, seconds=5)),
            Depends(RateLimiter(times=10, minutes=1))
        ]
)
def create_image(data: ImageGenerationRequest):
    try:
        pred_result = helpers.generate_image(data.prompt)
        return pred_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/processing", dependencies=[
    Depends(RateLimiter(times=1000, seconds=20))
])
def list_processing_view():
    results = helpers.list_prediction_results(status="processing")
    return results


@app.get("/predictions", dependencies=[
    Depends(RateLimiter(times=1000, seconds=20))
])
def list_predictions_view(status:Optional[str] = None):
    results = helpers.list_prediction_results(status=status)
    return results
