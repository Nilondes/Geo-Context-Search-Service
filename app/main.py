from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Geo Context Search Service")

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Geo Context Search Service is running"}
