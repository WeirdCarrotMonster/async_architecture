from fastapi import FastAPI


def build_app() -> FastAPI:
    app = FastAPI()
    return app


app = build_app()
