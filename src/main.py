import redis.asyncio as redis

from contextlib import asynccontextmanager
from typing import Union

from decouple import config
from fastapi import (
    Depends,
    FastAPI, 
    HTTPException
    )
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from pydantic import BaseModel

import helpers

REDIS_URL = config('REDIS_URL')

@asynccontextmanager
async def lifespan(_:FastAPI):
    redis_conn = redis.from_url(REDIS_URL)
    await FastAPILimiter.init(
        redis_conn
    )
    yield
    await FastAPILimiter.close()

app = FastAPI(lifespan=lifespan)

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
    