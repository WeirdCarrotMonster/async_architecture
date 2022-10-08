import uvicorn


def main():
    uvicorn.run("task_tracker.app:app", port=8000, host="0.0.0.0")


if __name__ == "__main__":
    main()
