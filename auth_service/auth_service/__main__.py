import uvicorn


def main():
    uvicorn.run("auth_service.app:app", port=8000, host="0.0.0.0")


if __name__ == "__main__":
    main()
