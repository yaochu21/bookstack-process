from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lib import extract,publish

class Input(BaseModel):
    url: str

app = FastAPI()

@app.get("/")
async def root():
    raise HTTPException(status_code=200, detail="Wrong endpoint")

@app.post("/process/")
async def process(input: Input):
    if not input.url:
        raise HTTPException(status_code=400, detail="Missing url")
    try:
        return extract(input.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/publish/")
async def process(input: Input):
    if not input.url:
        raise HTTPException(status_code=400, detail="Missing url")
    try:
        return publish(input.url,input.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))