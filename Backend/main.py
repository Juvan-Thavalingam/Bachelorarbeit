from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from plugins.plugin_manager import get_all_plugins
from routes import scan, get, describe, auth

"""
Entry-Point der Anwendung – startet FastAPI, lädt Plugins, registriert Routen.
"""

app = FastAPI()


# 🌍 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 📦 Plugins laden
plugins = get_all_plugins()

# 💾 Setup-Phase
@app.on_event("startup")
async def startup():
    """
    Setup-Hook beim Start – initialisiert alle Plugins.
    """
    for plugin in plugins:
        plugin.setup()

for route in [scan.router, get.router, describe.router, auth.router]:
    app.include_router(route)

