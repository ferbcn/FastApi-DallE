import json
import threading
import boto3
import openai
from datetime import datetime
import os
import requests
from app.crud import save_image_in_db, get_last_image_id

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


# generate image from content
# save image in db
# save backup on s3 storage
def image_workflow(title, content, user, db):
    print(title, content)
    try:
        img_url = get_dalle_image_url(content)
        # img_url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-OSSLxbVdVYcONWAYgACXE7BX/user-xe35vqrSPvSsPUEOnVK0Uwov/img-tpCOtVol5LsixwSZRrKvqnYN.png?st=2023-02-08T12%3A23%3A28Z&se=2023-02-08T14%3A23%3A28Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-02-07T21%3A30%3A10Z&ske=2023-02-08T21%3A30%3A10Z&sks=b&skv=2021-08-06&sig=QECDlgMyB6ThTSbTynoDk/uOe2z9866IHV6NlPrWWts%3D"
        print(img_url)
    except Exception as e:
        print(f'Could not get image url for {content}')
        print(e)

    filename = make_filename(content)
    try:
        response = requests.get(img_url, stream=True)
        data = response.content
    except Exception as e:
        print(f'Could not retrieve image from url: {img_url}')
        print(e)
    try:
        create_s3_upload_thread(filename, data)
    except Exception as e:
        print('Could not save image to S3')
        print(e)
    # add file to db
    try:
        save_image_in_db(db=db, title=title, filename=filename, data=data, url=img_url, description=content, user_id=user.id)
        img_id = get_last_image_id(db)
    except Exception as e:
        print('Could not save image to DB')
        print(e)
        img_id = None

    return img_url, img_id

