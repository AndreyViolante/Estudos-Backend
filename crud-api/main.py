from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import products


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Products API",
    description="API REST para gerenciamento de produtos",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(products.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}
