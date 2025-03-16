
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
# from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(
    title="Assigment",
    # openapi_url=f"Assigment",
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router, prefix="/v1")