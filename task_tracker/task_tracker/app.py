from fastapi import FastAPI

from task_tracker.views import router


def build_app() -> FastAPI:
    app = FastAPI()

    app.include_router(router)

    return app


app = build_app()
