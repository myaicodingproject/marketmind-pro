#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Serve static assets with cache busting
@app.get("/assets/{filename}")
async def serve_assets(filename: str):
    file_path = f"frontend/react-app/dist/assets/{filename}"
    if os.path.exists(file_path):
        response = FileResponse(file_path)
        # Add cache busting headers
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

@app.get("/vite.svg")
async def serve_vite_svg():
    return FileResponse("frontend/react-app/dist/vite.svg")

@app.get("/favicon.ico")
async def serve_favicon():
    return FileResponse("frontend/react-app/dist/vite.svg")

@app.get("/")
async def serve_react():
    response = FileResponse("frontend/react-app/dist/index.html")
    # Add cache busting headers
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/{path:path}")
async def serve_react_routes(path: str):
    # For React Router - serve index.html for all routes except API
    if not path.startswith("api/") and not path.startswith("assets/"):
        response = FileResponse("frontend/react-app/dist/index.html")
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    # For other files, try to serve them directly
    file_path = f"frontend/react-app/dist/{path}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse("frontend/react-app/dist/index.html")

if __name__ == "__main__":
    uvicorn.run("react_server:app", host="0.0.0.0", port=3000, log_level="info")
