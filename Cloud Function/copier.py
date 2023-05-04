'''
@Author: Jitendra Vikram Reddy K
@B#: B00929337
'''

import os
import time
from google.cloud import storage

def copy_object(data, context):
    """Triggered by a change to a Cloud Storage bucket.
        This Function backup uploaded data to Nearline Storage
    """

    # Get the source bucket and object name from the event data
    source_bucket_name = data['bucket']
    source_blob_name = data['name']
    
    # Get the destination bucket name from the environment variable
    destination_bucket_name = 'uploader9168'
    
    # Create a client object to interact with the Cloud Storage service
    client = storage.Client()
    destination_bucket = client.get_bucket(destination_bucket_name)

    # Copy the object from source to destination bucket
    source_bucket = client.bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_blob_name)

    # Loop until the source object exists
    while not source_bucket.blob(source_blob_name).exists():
        time.sleep(1)
    
    try:
        destination_blob_name = source_blob_name
        destination_blob = destination_bucket.blob(destination_blob_name)
        source_blob.download_to_filename('/tmp/temporary_file')
        with open('/tmp/temporary_file', 'rb') as file_obj:
            destination_blob.upload_from_file(
                file_obj,
                content_type=source_blob.content_type,
                predefined_acl='bucketOwnerFullControl'
            )
        print(f'File {source_blob_name} backedup to {destination_blob_name} in {destination_bucket_name}')
        os.remove('/tmp/temporary_file')
    except Exception as e:
        # Handle errors with the upload process
        print(f"Error uploading {destination_blob_name}: {e}")
