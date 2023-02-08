import threading
import boto3
import openai
from datetime import datetime
import os
import requests

from crud import save_image_in_db

linode_obj_config = {
    "aws_access_key_id": "JMUZU4LBJM1GITDW7ZII",
    "aws_secret_access_key": "bn0hxe2QhBIDi9WJue3T8p80IU3W2Cpt5hA9vaoM",
    "endpoint_url": "https://art-intel.eu-central-1.linodeobjects.com",
}

def make_filename(title):
    return title.replace(" ", "_") + "_" + str(datetime.utcnow()).replace(" ", "_") + ".png"


def get_dalle_image_url(prompt):
    """Get the image from the prompt."""
    response = openai.Image.create(prompt=prompt, n=1, size="512x512")
    image_url = response["data"][0]["url"]
    return image_url


def create_s3_upload_thread(filename, data):
    s3_upload_thread = threading.Thread(target=s3_upload_job(filename, data))
    s3_upload_thread.start()


def s3_upload_job(filename, data):
    # some long running processing here
    try:
        filepath = "app/static/images/" + filename  # [len(filename)-30:]
        with open(filepath, 'wb') as f:
            f.write(data)
        client = boto3.client("s3", **linode_obj_config)
        client.upload_file(Filename=filepath, Bucket='DallE-Images', Key=filename)
        os.remove(filepath)
        print('S3 upload done!')
    except Exception as e:
        print('S3 upload failed!')
        print(e)
