if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs="app",
        access_log=False,
    )
