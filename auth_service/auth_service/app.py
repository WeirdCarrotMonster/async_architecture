from fastapi import FastAPI

from auth_service.views import router


def build_app() -> FastAPI:
    app = FastAPI()

    app.include_router(router)

    return app


app = build_app()
