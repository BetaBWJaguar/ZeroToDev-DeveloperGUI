import uvicorn
from fastapi import FastAPI
from usermanager.verfiy_manager.VerifyController import router as verify_router
from updater.local_update_server import router as local_router

app = FastAPI()
app.include_router(verify_router, prefix="/verify", tags=["verify"])
app.include_router(local_router, prefix="/api", tags=["updates"])

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=9090, reload=True)