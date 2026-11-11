from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.core.config import APP_NAME, FRONTEND_ORIGINS
from app.routers import auth, books, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    description="Backend API for Nangarhar University Digital Library (NUDL)",
    version="1.0.0",
)

origins = ["*"] if FRONTEND_ORIGINS == ["*"] else FRONTEND_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "NUDL API is running", "docs": "/docs", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
