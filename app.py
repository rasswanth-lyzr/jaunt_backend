import uvicorn
from fastapi import FastAPI

from planner.endpoints import router as planner_router

app = FastAPI()

app.include_router(planner_router, tags=["planner"])


@app.get("/")
def read_root():
    return {"message": "OK"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
