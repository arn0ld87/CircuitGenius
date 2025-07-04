from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, RootModel
from typing import List, Dict, Any, Union

from circuit_solver import solve_series_circuit, solve_parallel_circuit, solve_mixed_circuit

app = FastAPI()

# CORS middleware to allow requests from the frontend
origins = [
    "http://localhost:3000",  # React frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a recursive model for the mixed circuit structure
class CircuitComponent(RootModel):
    root: Union[float, List['CircuitComponent']]

class CircuitPayload(BaseModel):
    circuit_type: str
    resistors: Union[List[float], List[Any]] # Allow flat list for simple, nested for mixed
    total_voltage: float

@app.post("/api/solve")
def solve_circuit(payload: CircuitPayload) -> Dict[str, Any]:
    """
    API endpoint to solve a circuit.
    """
    if payload.circuit_type == "series":
        # Ensure resistors are floats for this case
        resistor_values = [float(r) for r in payload.resistors]
        return solve_series_circuit(resistor_values, payload.total_voltage)
    elif payload.circuit_type == "parallel":
        # Ensure resistors are floats for this case
        resistor_values = [float(r) for r in payload.resistors]
        return solve_parallel_circuit(resistor_values, payload.total_voltage)
    elif payload.circuit_type == "mixed":
        return solve_mixed_circuit(payload.resistors, payload.total_voltage)
    else:
        return {"error": "Invalid circuit type"}
