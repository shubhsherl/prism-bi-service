from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import api.top_subpages as api_top_subpages
import urllib.parse

app = FastAPI()

@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "https://prism-bi-ui.vercel.app, http://localhost:3000", "http://127.0.0.1:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
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

@app.get("/top-subpages")
async def top_subpages(url: str = Query(..., title="Encoded URL"), n: int = Query(10, title="n")):
    # Decode the URL
    decoded_url = urllib.parse.unquote(url)
    
    # Your logic to use the decoded URL and 'n' goes here
    # For now, let's just return the decoded URL and 'n'
    # return {"decoded_url": decoded_url, "n": n}
    return api_top_subpages.run(decoded_url, n)
