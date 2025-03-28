"""
API simplifiée pour le frontend Insyte.io Dashboard
"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(title="Insyte.io Dashboard API (Simplifiée)")

# Configuration CORS pour permettre l'accès depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Données mockées
MOCK_DASHBOARD_DATA = {"total_views": 25460, "total_clicks": 1035, "total_revenue": 21750}
MOCK_YOUTUBE_DATA = {"totalViews": 25460, "videos": [{"title": "Sample Video", "views": 8743}]}
MOCK_SALES_DATA = {"metrics": {"total_clicks": 1035, "revenue": 21750}}
MOCK_LINKS = [{"id": 1, "slug": "youtube-workshop", "title": "YouTube Workshop"}]

# Endpoints principaux
@app.get("/api/dashboard")
async def get_dashboard():
    return MOCK_DASHBOARD_DATA

@app.get("/api/youtube")
async def get_youtube_metrics(slug: Optional[str] = Query(None)):
    return MOCK_YOUTUBE_DATA

@app.get("/api/sales")
async def get_sales_metrics():
    return MOCK_SALES_DATA

@app.get("/api/links")
async def get_all_links():
    return MOCK_LINKS

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Insyte.io Dashboard API is running",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000) 