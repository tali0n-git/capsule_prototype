import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import engine, Base
from routers import auth, notes, summary

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration for allowing requests from an authorized origin
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],    # if want to block certain methods, specify them here
    allow_headers=["*"],    # if want to block certain headers, specify them here
)

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(summary.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
