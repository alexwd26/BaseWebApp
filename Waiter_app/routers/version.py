from fastapi import FastAPI

app = FastAPI()
APP_VERSION = "1.0.0"
@app.get("/api/version")
def get_version():
    return {"version": APP_VERSION}
