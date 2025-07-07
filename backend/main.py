from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union

from circuit_solver import solve_series_circuit, solve_parallel_circuit, solve_mixed_circuit

app = FastAPI(
    title="CircuitSolver API",
    description="An API for calculating series, parallel, and mixed electrical circuits.",
    version="2.0.0",
)

# CORS middleware to allow requests from the frontend
origins = [
    "http://localhost:3000",  # React frontend
    "https://circuitgenius-alexle135.onrender.com", # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Input Validation ---

# A model for the recursive structure of a mixed circuit
class MixedCircuit(BaseModel):
    type: str  # "series" or "parallel"
    components: List[Union['MixedCircuit', float, int]]

class CircuitPayload(BaseModel):
    circuit_type: str = Field(..., description="Type of circuit: 'series', 'parallel', or 'mixed'.")
    # The structure of the circuit. For 'mixed', it's a nested dict. For others, a flat list.
    circuit: Union[List[float], MixedCircuit]
    total_voltage: float = Field(..., gt=0, description="The total voltage applied to the circuit.")

@app.post("/api/solve", summary="Solve an Electrical Circuit")
def solve_circuit(payload: CircuitPayload) -> Dict[str, Any]:
    """
    Calculates the total resistance, current, power, and individual component
    values for a given electrical circuit.

    - **circuit_type**: "series", "parallel", or "mixed".
    - **circuit**:
        - For "series" or "parallel": A list of resistor values (e.g., `[10, 20, 50]`).
        - For "mixed": A nested dictionary describing the topology.
          Example: `{"type": "series", "components": [10, {"type": "parallel", "components": [20, 50]}]}`
    - **total_voltage**: The total voltage of the circuit.
    """
    circuit_type = payload.circuit_type.lower()
    
    if circuit_type == "series":
        if not isinstance(payload.circuit, list):
            return {"error": "For series circuits, 'circuit' must be a list of resistor values."}
        resistor_values = [float(r) for r in payload.circuit]
        return solve_series_circuit(resistor_values, payload.total_voltage)
        
    elif circuit_type == "parallel":
        if not isinstance(payload.circuit, list):
            return {"error": "For parallel circuits, 'circuit' must be a list of resistor values."}
        resistor_values = [float(r) for r in payload.circuit]
        return solve_parallel_circuit(resistor_values, payload.total_voltage)
        
    elif circuit_type == "mixed":
        if not isinstance(payload.circuit, MixedCircuit):
             return {"error": "For mixed circuits, 'circuit' must be a valid JSON object."}
        # Pydantic has already parsed it into MixedCircuit, we can convert it back to a dict for the solver
        circuit_dict = payload.circuit.model_dump()
        return solve_mixed_circuit(circuit_dict, payload.total_voltage)
        
    else:
        return {"error": f"Invalid circuit type '{payload.circuit_type}'. Use 'series', 'parallel', or 'mixed'."}

@app.get("/", summary="Root Endpoint")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"message": "Welcome to the CircuitSolver API. Send calculations to /api/solve."}

# To run this API locally: uvicorn main:app --reload --port 8000