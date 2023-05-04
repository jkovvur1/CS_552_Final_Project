import os
from google.cloud import storage
from pymongo import MongoClient

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./keys.json"

# Set up MongoDB connection
mongo_client = MongoClient(os.environ.get('MONGO_URL', "mongodb://localhost:27017"))
db = mongo_client['file_metadata']
collection = db['files']

# Set up Google Cloud Storage client
storage_client = storage.Client()
bucket = storage_client.bucket(os.environ.get("BUCKET", "media-9162"))

def fetch_metadata():
    try:

        for blob in bucket.list_blobs():
            # Check if file already exists in MongoDB
            if collection.find_one({'name': blob.name}):
                continue
            
            # Get file metadata
            metadata = {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'url': f'{os.environ.get("CDN_URL", "http://34.149.205.56")}/{blob.name}'
            }

            # Store metadata in MongoDB
            collection.insert_one(metadata)
    except Exception as exp:
        print("Exception occured: " + str(exp))

if __name__ == "__main__":
    print("Started To fetch metadta from the Bucket")
    fetch_metadata()
    print("Finished fetching Metadata, Exiting....")