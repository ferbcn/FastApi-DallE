import json
import threading
import uuid

import boto3
import openai
from datetime import datetime
import os
import requests
from app.crud import save_image_in_db, get_last_image_id
from urllib.parse import quote

# Fetch quote of the day from here
quote_url = 'https://zenquotes.io/api/quotes'

S3_KEY = os.environ.get("S3_KEY")
S3_SECRET = os.environ.get("S3_SECRET")
S3_URL = os.environ.get("S3_URL")

s3_obj_config = {
    "aws_access_key_id": S3_KEY,
    "aws_secret_access_key": S3_SECRET,
    "endpoint_url": S3_URL,
}

s3_extra_args = {
        'ContentType': 'image/png',
        'ACL': 'public-read'  # Set permissions to public-read
    }

def make_filename(title):
    #return title.replace(" ", "_").replace("'", "").replace(",", "") + "_" + str(datetime.utcnow()).replace(" ", "_").replace(":", ".") + ".png"
    return str(uuid.uuid4()) + ".png"


def get_dalle_image_url(prompt):
    """Get the image from the prompt."""
    response = openai.Image.create(prompt=prompt, n=1, size="512x512")
    image_url = response["data"][0]["url"]
    return image_url


def create_s3_upload_thread(filename, data):
    s3_upload_thread = threading.Thread(target=s3_upload_job(filename, data))
    s3_upload_thread.start()


def s3_upload_job(filename, data):
    # some long-running processing here
    try:
        filepath = "app/static/images/" + filename  # [len(filename)-30:]
        with open(filepath, 'wb') as f:
            f.write(data)
        client = boto3.client("s3", **s3_obj_config)
        client.upload_file(Filename=filepath, Bucket='DallE-Images', Key=filename, ExtraArgs=s3_extra_args)
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


# generate image from description
# save image metadat in db
# save backup on s3 storage
def image_workflow(title, description, user, db):
    print(title, description)
    try:
        img_url = get_dalle_image_url(description)
        print("DallE URL: " + img_url)
    except Exception as e:
        print(f'Could not get image url for {description}')
        print(e)

    filename = make_filename(description)
    try:
        response = requests.get(img_url, stream=True)
        img_data = response.content
    except Exception as e:
        print(f'Could not retrieve image from url: {img_url}')
        print(e)
    try:
        create_s3_upload_thread(filename, img_data)
    except Exception as e:
        print('Could not save image to S3')
        print(e)
    # add file to db
    try:
        save_image_in_db(db=db, title=title, filename=filename, data=img_data, url=img_url, description=description, user_id=user.id)
        img_id = get_last_image_id(db)
    except Exception as e:
        print('Could not save image to DB')
        print(e)
        img_id = None

    return img_url, img_id

