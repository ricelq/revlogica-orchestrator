# =====================================
# This file is part of the CodeDev project
# Author: Ricel Quispe
# =====================================

# revlogica-orchestrator/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .infrastructure.config import settings
from .presentation.endpoints.manuscripts import manuscript
from .presentation.handlers.exceptions import register_exception_handlers

app = FastAPI(
    title="Verilogica Orchestrator API",
    description="The central brain of the Revlog system.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Define the list of origins that are allowed to make requests.
# Use ["*"] to allow all origins.
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",  # Frontend port
    # Add any other frontend origins here
]

# Add the CORS middleware to application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Register a custom exception handler for all application-level errors
register_exception_handlers(app)

# Include routers
app.include_router(manuscript.router, prefix="/manuscripts",
                   tags=["Manuscripts"])


@app.get("/")
def read_root():
    """
    Root endpoint for the VeriLogica Orchestrator.
    """
    return {"message": "VeriLogica Orchestrator is running."}
