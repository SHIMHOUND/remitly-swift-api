from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import swift_code
from models.swift_code import Base
from db import engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SWIFT Codes API",
    description="API for managing SWIFT codes",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(swift_code.router)

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to the SWIFT Codes API. Use /docs for API documentation."}