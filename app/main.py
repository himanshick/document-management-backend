from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- import CORS middleware

from app.api import user_routes, document_routes, ingestion_routes
from app.core.config import settings
from app.db.mongodb import connect_db, close_db
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from app.core.custom_exception_handler import add_exception_handlers

app = FastAPI(title="Document Management and Ingestion System")

add_exception_handlers(app)

origins = [
    "*"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],    # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],    # allow all headers
)

app.include_router(user_routes.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(document_routes.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(ingestion_routes.router, prefix="/api/v1/ingestion", tags=["Ingestion"])

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()

@app.get("/")
def root():
    return {"message": "Welcome to the Document Management API"}
