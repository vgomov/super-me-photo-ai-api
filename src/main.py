from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import helpers

app = FastAPI()

@app.get("/")
def read_root():
    # helpers.generate_image()
    return {"Hello": "World"}


class ImageGenerationRequest(BaseModel):
    prompt:str

@app.post('/generate')
def create_image(data: ImageGenerationRequest):
    try:
        pred_result = helpers.generate_image(data.prompt)
        return pred_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    