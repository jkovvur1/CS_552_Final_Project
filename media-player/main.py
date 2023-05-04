import os
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import storage
from pymongo import MongoClient

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./keys.json"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Set up MongoDB connection
mongo_client = MongoClient(os.environ.get('MONGO_URL', "mongodb://localhost:27017"))
db = mongo_client['file_metadata']
collection = db['files']

#GCP Client
client = storage.Client()


# Define routes
@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse('home.html', {'request': request, 'title': 'Home'})

@app.get('/videos', response_class=HTMLResponse)
async def videos(request: Request):
    # Fetch video files from MongoDB
    files = collection.find({'content_type': {'$regex': '^video/.*'}})
    # files = collection.find({'content_type': 'video'})
    files = [file for file in files]
    return templates.TemplateResponse('content.html', {'request': request, 'title': 'Videos', 'files': files})

@app.get('/music', response_class=HTMLResponse)
async def music(request: Request):
    # Fetch audio files from MongoDB
    files = collection.find({'content_type': {'$regex': '^audio/.*'}})
    # files = collection.find({'content_type': 'audio'})
    files = [file for file in files]
    return templates.TemplateResponse('content.html', {'request': request, 'title': 'Music', 'files': files})

@app.get('/pictures', response_class=HTMLResponse)
async def pictures(request: Request):
# Fetch image files from MongoDB
    files = collection.find({'content_type': {'$regex': '^image/.*'}})
    # files = collection.find({'content_type': 'image'})
    files = [file for file in files]
    return templates.TemplateResponse('content.html', {'request': request, 'title': 'Pictures', 'files': files})

@app.get('/play/{name}', response_class=HTMLResponse)
async def play(request: Request, name: str):
# Fetch metadata for the selected file from MongoDB
    metadata = collection.find_one({'name': name})
    return templates.TemplateResponse('play.html', {'request': request, 'title': name, 'metadata': metadata})

#Uploader routes
@app.get("/uploader")
async def index():
    with open("templates/uploader.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Upload the file to GCS bucket
    bucket_name = os.environ.get('BUCKET', 'media-9162')
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file.file)

    return {"message": f"File '{file.filename}' uploaded to GCS bucket '{bucket_name}'"}