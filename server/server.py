from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict
from vector_clocks import VectorClock



app = FastAPI()
server_id = "server"
server_clock = VectorClock(server_id)


class Numbers(BaseModel):
    x: int
    y: int
    vector_clock: Optional[Dict[str, int]] = None


@app.post("/add")
def add(nums: Numbers):
    if nums.vector_clock:
        server_clock.update(nums.vector_clock)
    server_clock.increment()
    return {
        "result": nums.x + nums.y,
        "server_clock": server_clock.get_clock()
    }


@app.post("/multiply")
def multiply(nums: Numbers):
    if nums.vector_clock:
        server_clock.update(nums.vector_clock)
    server_clock.increment()
    return {
        "result": nums.x * nums.y,
        "server_clock": server_clock.get_clock()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)