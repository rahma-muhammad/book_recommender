from recommend import myrecommend

from dotenv import load_dotenv
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="templates")

import requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/recommend", response_class=HTMLResponse)
async def recommend(request: Request, book: str):
    css_file = "/static/style.css" 
    notfound = "/static/download.png"
    icon = "/static/favicon.ico"
    books = myrecommend(book)
    if len(books) < 2:
        return f"{books}"
    
    # Load environment variables from .env file
    load_dotenv()

    # Google Custom Search API key and search engine ID
    google_api_key = os.getenv("google_api_key")

    search_engine_id = os.getenv("search_engine_id")


    image_urls = {}
    for b in books:
        url = f"https://www.googleapis.com/customsearch/v1?q={b}&cx={search_engine_id}&searchType=image&key={google_api_key}"
        response = requests.get(url)
        data = response.json()
        print(f"first", data)
        if len(data) == 0 or data.get('items') is None:
            print(f"No image found for book: {b}")
            image_urls[b] ='XXXX'
            continue  # Skip to the next book

        image_url = data['items'][0].get('link')
        if image_url is None:
            print(f"No image found for book: {b}")
            image_urls[b] = 'XXXX'
            continue  # Skip to the next book

        image_urls[b] = image_url

    # Get the URLs of the images found (up to 9 images)
    #image_urls = [result['urls']['regular'] for result in data['results'][:9]]
    # Render the HTML template with the image URLs
    return templates.TemplateResponse("image_results.html", {"request": request, "book": book, "image_urls": image_urls, "css_file": css_file, 'notfound':notfound, 'icon': icon})