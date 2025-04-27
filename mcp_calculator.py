# file: mcp_math_calculator.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
import uvicorn

app = FastAPI(title="Math Calculator MCP Server")

class MathRequest(BaseModel):
    operation: Literal["add", "subtract", "multiply", "divide"]
    num1: float
    num2: float

@app.get("/manifest.json")
async def manifest():
    return {
        "name": "Math Calculator MCP Server",
        "version": "1.0",
        "actions": [
            {
                "name": "process",
                "description": "Perform basic math operations",
                "input_model": MathRequest.schema()
            }
        ]
    }

@app.post("/process")
async def process_math(req: MathRequest):
    if req.operation == "add":
        return {"result": req.num1 + req.num2}
    if req.operation == "subtract":
        return {"result": req.num1 - req.num2}
    if req.operation == "multiply":
        return {"result": req.num1 * req.num2}
    if req.operation == "divide":
        if req.num2 == 0:
            return {"error": "Division by zero"}
        return {"result": req.num1 / req.num2}
    return {"error": "Invalid operation"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
