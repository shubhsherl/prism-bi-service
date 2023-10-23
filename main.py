from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import api.top_subpages as api_top_subpages
import api.test_results as api_test_results
import api.crux_results as api_crux_results
import api.url_prefetches as api_url_prefetches
import urllib.parse

app = FastAPI()

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://prism-bi-ui.vercel.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

origins = [
    "https://prism-bi-ui.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/top-subpages-lcp")
async def top_subpages(url: str = Query(..., title="Encoded URL"), n: int = Query(10, title="n")):
    # Decode the URL
    decoded_url = urllib.parse.unquote(url)
    return api_top_subpages.run_lcp(decoded_url, n)

@app.get("/top-subpages")
async def top_subpages():
    return api_top_subpages.run_top_subpages()

@app.get("/test-results")
async def test_results():
    return api_test_results.run()

@app.get("/crux-results")
async def crux_results():
    return api_crux_results.run()

@app.get("/url-prefetches")
async def url_prefetches():
    return api_url_prefetches.run()
