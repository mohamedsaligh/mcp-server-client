# file: mcp_area_calculator.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import math
import uvicorn

app = FastAPI(title="Area Calculator MCP Server")

class AreaRequest(BaseModel):
    shape: Literal["square", "rectangle", "triangle", "cube", "circle", "sphere"]
    dimension1: float
    dimension2: float = None

@app.get("/manifest.json")
async def manifest():
    return {
        "name": "Area Calculator MCP Server",
        "version": "1.0",
        "actions": [
            {
                "name": "process",
                "description": "Calculate area of different shapes",
                "input_model": AreaRequest.schema()
            }
        ]
    }

@app.post("/process")
async def process_area(req: AreaRequest):
    if req.shape == "square":
        return {"area": req.dimension1 ** 2}
    if req.shape == "rectangle":
        if req.dimension2 is None:
            return {"error": "dimension2 required for rectangle"}
        return {"area": req.dimension1 * req.dimension2}
    if req.shape == "triangle":
        if req.dimension2 is None:
            return {"error": "dimension2 required for triangle"}
        return {"area": 0.5 * req.dimension1 * req.dimension2}
    if req.shape == "cube":
        return {"area": 6 * (req.dimension1 ** 2)}
    if req.shape == "circle":
        return {"area": math.pi * (req.dimension1 ** 2)}
    if req.shape == "sphere":
        return {"area": 4 * math.pi * (req.dimension1 ** 2)}
    return {"error": "Invalid shape"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

