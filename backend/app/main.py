"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import articles, auth, feeds, preferences
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(feeds.router, prefix=f"{settings.API_V1_STR}/feeds", tags=["feeds"])
app.include_router(articles.router, prefix=f"{settings.API_V1_STR}/articles", tags=["articles"])
app.include_router(
    preferences.router, prefix=f"{settings.API_V1_STR}/preferences", tags=["preferences"]
)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "News Reader API", "version": settings.VERSION}


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
