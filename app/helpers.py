import json
import threading
import boto3
import openai
from datetime import datetime
import os

import requests

# Fetch quote of the day from here
quote_url = 'https://zenquotes.io/api/quotes'

S3_KEY = os.environ.get("S3_KEY")
S3_SECRET = os.environ.get("S3_SECRET")
S3_URL = os.environ.get("S3_URL")

linode_obj_config = {
    "aws_access_key_id": S3_KEY,
    "aws_secret_access_key": S3_SECRET,
    "endpoint_url": S3_URL,
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


def retrieve_quote():
    try:
        # Retrieve quote from API
        response = requests.get(quote_url)
        data_str = response.text
        data = json.loads(data_str)[0]
        quote = data.get("q")
        author = data.get("a")
        quote_author = {'quote': quote, 'author': author}

    except Exception as e:
        print(e)
        quote_author = None

    return quote_author