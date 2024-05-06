from recommend import myrecommend

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
    return """
    <html>
    <head>
        <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Recommendation System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f8f8;
            margin: 0;
            padding: 0;
        }
        h1 {
            color: #333;
            text-align: center;
            margin: 20px;
        }
        form {
            text-align: center;
            margin-top: 20px;
        }
        input[type="text"] {
            padding: 10px;
            width: 300px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Book Recommendation System</h1>
    <form action="/recommend" method="get">
        <input type="text" name="book" placeholder="Enter the book name">
        <button type="submit">Search</button>
    </form>
</body>
</html>
"""

@app.get("/recommend", response_class=HTMLResponse)
async def recommend(request: Request, book: str):
    css_file = "/static/style.css" 
    notfound = "/static/download.png"
    icon = "/static/favicon.ico"
    books = myrecommend(book)
    if len(books) < 2:
        return f"{books}"
    
    # Google Custom Search API key and search engine ID
    google_api_key = "AIzaSyDSceE49rPjkOhwxTfmC5Vw0FegykrxOzw"
    search_engine_id = "d3d2c739e48a8428d"

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