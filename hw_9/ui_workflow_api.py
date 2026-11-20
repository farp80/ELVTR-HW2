"""UI-serving adapter for an existing Homework 8 FastAPI application.

Copy this file as ui_workflow_api.py alongside your Homework 8 API module.
Keep your existing API module; do not replace it with this file.
"""

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# REPLACE: import the existing FastAPI app from your Homework 8 API module.
from YOUR_HOMEWORK8_API_MODULE import app


# Place the supplied ui/ directory beside ui_workflow_api.py in the image.
UI_DIRECTORY = Path(__file__).resolve().parent / "ui"


class FreshStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: dict):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-store"
        return response


@app.get("/", include_in_schema=False)
def serve_ui() -> FileResponse:
    return FileResponse(
        UI_DIRECTORY / "index.html",
        headers={"Cache-Control": "no-store"},
    )


app.mount(
    "/static",
    FreshStaticFiles(directory=UI_DIRECTORY),
    name="static",
)
