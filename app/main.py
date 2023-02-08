import os
import json
from datetime import datetime

import openai as openai
import uvicorn

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import requests

from crud import *

from helpers import *

import models

from database import SessionLocal, engine

from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

# Fetch quote of the day from here
quote_url = 'https://zenquotes.io/api/quotes'

openai.api_key = os.environ.get("OPENAI_KEY")

# Create application
app = FastAPI(title='FastAPI DalLE')

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = get_users(db, skip=skip, limit=limit)
    return users


@app.get("/images/")
def get_images(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    images = get_images_from_db(db, skip=skip, limit=limit)
    return images


@app.post("/users/")
def create_user(username, password, db: Session = Depends(get_db)):
    #db_user = get_user_by_username(db, username=username)
    #if db_user:
    #    raise HTTPException(status_code=400, detail="Email already registered")
    return create_user_in_db(db, username, password)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    images = get_images_from_db(db, skip=skip, limit=limit)
    print(images)
    # return render_template('index.html', images=images, user_auth=user_auth)
    return templates.TemplateResponse("index.html", {"request": request, "images": images})


@app.get("/quote/", response_class=HTMLResponse)
def quote(request: Request):
    # GET Request
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

    return templates.TemplateResponse("quote.html", {"request": request, "quote":quote_author})


@app.get("/create/", response_class=HTMLResponse)
def create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.get("/edit/", response_class=HTMLResponse)
def edit(request: Request):
    return templates.TemplateResponse("edit.html", {"request": request})


@app.get("/about/", response_class=HTMLResponse)
def about(request: Request, db: Session = Depends(get_db)):
    # get total images
    # get images in db
    total_images, num_images = get_db_stats(db)
    return templates.TemplateResponse("about.html", {"request": request, "total_images":total_images, "num_images":num_images})


@app.get("/login/", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout/", response_class=HTMLResponse)
def logout(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.websocket("/q2i")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    try:
        # send "Connection established" message to client
        # await websocket.send_text("Connection established!")

        # await for messages and send messages
        while True:
            quote = await websocket.receive_text()
            if quote.lower() == "close":
                await websocket.close()
                break
            else:
                print(f'CLIENT says - {quote}')
                img_url = get_dalle_image_url(quote)
                #img_url = "https://oaidalleapiprodscus.blob.core.windows.net/private/org-OSSLxbVdVYcONWAYgACXE7BX/user-xe35vqrSPvSsPUEOnVK0Uwov/img-tpCOtVol5LsixwSZRrKvqnYN.png?st=2023-02-08T12%3A23%3A28Z&se=2023-02-08T14%3A23%3A28Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-02-07T21%3A30%3A10Z&ske=2023-02-08T21%3A30%3A10Z&sks=b&skv=2021-08-06&sig=QECDlgMyB6ThTSbTynoDk/uOe2z9866IHV6NlPrWWts%3D"
                print(img_url)

                # retrieve image make filename and upload file to S3 and DB
                filename = make_filename(quote)
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
                    save_image_in_db(db=db, title=quote, filename=filename, data=data)
                except Exception as e:
                    print('Could not save image to DB')
                    print(e)

                # dict = {"img_url": img_url}
                # json_object = json.dumps(dict)
                await websocket.send_text(img_url)

    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == '__main__':
    # run SSL server
    """
    uvicorn.run(
        'main:app', port=443, host='0.0.0.0',
        ssl_keyfile='app/key.pem',
        ssl_certfile='app/cert.pem',
    )
    """
    uvicorn.run(
        'main:app', port=8000, host='0.0.0.0',
        reload=True,
    )