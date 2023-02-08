import threading
import boto3
import openai
from datetime import datetime
import os

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
    print('S3 upload job scheduled.')


def s3_upload_job(filename, data):
    # some long running processing here
    try:
        filepath = "static/images/" + filename
        with open(filepath, 'wb') as f:
            f.write(data)
        client = boto3.client("s3", **linode_obj_config)
        client.upload_file(Filename=filepath, Bucket='DallE-Images', Key=filename)
        os.remove(filepath)
        print('S3 upload done!')
    except Exception as e:
        print(e)

