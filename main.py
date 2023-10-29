from fastapi import FastAPI, Query, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import api.top_subpages as api_top_subpages
import api.test_results as api_test_results
import api.crux_results as api_crux_results
import api.url_prefetches as api_url_prefetches
import urllib.parse
import logging

# Set up the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger instance
logger = logging.getLogger('main')
logger.info("Starting api server...")

app = FastAPI()
router = APIRouter()

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://prism-bi-ui.vercel.app"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

origins = [
    "https://prism-bi-ui.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.get("/top-subpages-lcp")
async def top_subpages(url: str = Query(..., title="Encoded URL"), n: int = Query(10, title="n")):
    decoded_url = urllib.parse.unquote(url)
    return api_top_subpages.run_lcp(decoded_url, n)

@router.get("/top-subpages")
async def top_subpages():
    return api_top_subpages.run_top_subpages()

@router.get("/test-results")
async def test_results():
    return api_test_results.run()

@router.get("/crux-results")
async def crux_results():
    return api_crux_results.run()

@router.get("/url-prefetches")
async def url_prefetches():
    return api_url_prefetches.run()

app.include_router(router, prefix="/v1")
