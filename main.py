from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import api.top_subpages as api_top_subpages
import urllib.parse

app = FastAPI()

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
