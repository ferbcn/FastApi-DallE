import random

import uvicorn
from starlette.exceptions import HTTPException
from starlette.responses import Response

from app.helpers import *
from app.crud import *
from app.database import engine, SessionLocal, Base

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

# Create application
app = FastAPI(title='FastAPI DalLE')

openai.api_key = os.environ.get("OPENAI_KEY")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)

from fastapi_login import LoginManager

SECRET_KEY = os.environ.get("SECRET_KEY")

manager = LoginManager(SECRET_KEY, token_url='/login', use_cookie=True)

favicon_path = 'app/static/images/favicon.ico'


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@manager.user_loader()
def load_user(username: str):  # could also be an asynchronous function
    db = SessionLocal()     # No dependenca injection on non route functions, is this a hack?
    user = get_user_by_username(db, username=username)
    return user


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get("/users/")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), user=Depends(manager)):
    print(user)
    users = get_users(db, skip=skip, limit=limit)
    return users


@app.post("/users/")
def create_user(username, password, db: Session = Depends(get_db), user=Depends(manager)):
    newuser = get_user_by_username(db, username=username)
    if newuser:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user_in_db(db, username, password)


@app.get("/login/", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# the python-multipart package is required to use the OAuth2PasswordRequestForm
@app.post('/login')
def login(response: Response, data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = data.username
    password = data.password

    if not check_user_pass(db, username, password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=username)
    )
    manager.set_cookie(response, access_token)
    # return {'access_token': access_token, 'token_type': 'bearer', }
    # resp = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    # manager.set_cookie(resp, access_token)
    # return resp
    return JSONResponse({"status": "success"})


@app.get("/logout/", response_class=HTMLResponse)
def logout(response: Response):
    # manager.set_cookie(response, None)
    # response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    # clear cookie in some way
    response.delete_cookie("access_token")
    # This does not logout
    # return response
    return JSONResponse({"status": "success"})


@app.get("/", response_class=HTMLResponse)
# @app.post("/", response_class=HTMLResponse)     # Needed for redirect from post methods
def index(request: Request, skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    images = get_images_from_db(db, skip=skip, limit=limit)
    return templates.TemplateResponse("index.html", {"request": request, "images": images})


@app.get("/quote/", response_class=HTMLResponse)
def quote(request: Request):
    # GET Request
    quote_author = retrieve_quote()
    return templates.TemplateResponse("quote.html", {"request": request, "quote": quote_author})


@app.post("/quote/", response_class=HTMLResponse)
def quote(request: Request, title: str = Form(), content: str = Form(), db: Session = Depends(get_db), user=Depends(manager)):
    img_url, img_id = image_workflow(title, content, db)
    json_object = {"img_title": title, "img_url": img_url, "img_text": content, "img_id": img_id}
    quote_author = {"quote": content, "author": title}
    return templates.TemplateResponse("quote.html", {"request": request, "quote": quote_author, "img_object": json_object})


@app.get("/create/", response_class=HTMLResponse)
def create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.post("/create/", response_class=HTMLResponse)
def create(request: Request, title: str = Form(), content: str = Form(), db: Session = Depends(get_db), user=Depends(manager)):
    img_url, img_id = image_workflow(title, content, db)
    json_object = {"img_title": title, "img_url": img_url, "img_text": content, "img_id": img_id}
    return templates.TemplateResponse("create.html", {"request": request, "img_object": json_object})


@app.get("/about/", response_class=HTMLResponse)
def about(request: Request, db: Session = Depends(get_db), user=Depends(manager)):
    # get total images
    # get images in db
    total_images, num_images = get_db_stats(db)
    return templates.TemplateResponse("about.html", {"request": request, "total_images": total_images, "num_images": num_images})


@app.get("/signup/", response_class=HTMLResponse)
def signup(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/delete/")
def delete_image_by_id(image_id, request: Request, db: Session = Depends(get_db), user=Depends(manager)):
    print(user)
    print(image_id)
    delete_db_image_by_id(db, image_id)
    return {'user': user}


# Websocket endpoint MORE IMAGES FOR FEED
@app.websocket("/moreImages")
async def websocket_moreImages(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    try:
        # await for messages and send messages
        while True:
            current_image_offset = await websocket.receive_text()
            if current_image_offset.lower() == "close":
                await websocket.close()
                break
            else:
                # print(f'CLIENT says - {current_image_offset}')
                db_img_count = get_db_image_count(db)
                # check for end of image feed and then return a random image from the db
                if int(current_image_offset) >= db_img_count:
                    current_image_offset = random.randint(0, db_img_count)
                images = get_images_from_db(db, skip=current_image_offset, limit=5)
                for image in images:
                    json_object = {"title": image.title, "rendered_data": image.rendered_data, "id": image.id}
                    # print(f'Sending {image} to client websocket.')
                    await websocket.send_json(json_object)

    except WebSocketDisconnect:
        print("Client disconnected")


if __name__ == '__main__':
    # run SSL server
    """
    uvicorn.run(
        'main:app', port=443, host='192.168.1.111',
        ssl_keyfile='cert/key.pem',
        ssl_certfile='cert/cert.pem',
    )
    """
    uvicorn.run(
        'main:app', port=8000, host='192.168.1.111',
        reload=True,
    )

