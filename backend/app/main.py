from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, occurrences, species, studies, tiles
from app.core.config import settings

app = FastAPI(title="Lorenzini Track API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(tiles.router)
app.include_router(occurrences.router)
app.include_router(studies.router)
app.include_router(species.router)
