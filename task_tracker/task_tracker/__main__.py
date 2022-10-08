def run_server():
    import uvicorn

    uvicorn.run("task_tracker.app:app", port=8000, host="0.0.0.0")


def run_consumer():
    import asyncio
    from task_tracker.consumer import run_consumer

    asyncio.run(run_consumer())


def main():
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    s_server = subparsers.add_parser("server")
    s_server.set_defaults(cmd="server")

    s_consumer = subparsers.add_parser("consumer")
    s_consumer.set_defaults(cmd="consumer")

    args = parser.parse_args()

    if args.cmd == "server":
        run_server()
    else:
        run_consumer()


if __name__ == "__main__":
    main()
