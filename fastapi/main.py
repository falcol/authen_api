import uvicorn

if __name__ == "__main__":
    options = {
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "debug",
        "reload": True,
        # "root_path": "/api"
    }
    uvicorn.run("src.app:app", **options)
