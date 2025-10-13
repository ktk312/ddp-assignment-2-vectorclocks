from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Numbers(BaseModel):
    x: int
    y: int

@app.post("/add")
def add(nums: Numbers):
    return {"result": nums.x + nums.y}

@app.post("/multiply")
def multiply(nums: Numbers):
    return {"result": nums.x * nums.y}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
