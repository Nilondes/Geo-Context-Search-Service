from fastapi import FastAPI

app = FastAPI(title="Geo Context Search Service")

@app.get("/")
async def root():
    return {"message": "Geo Context Search Service is running"}
