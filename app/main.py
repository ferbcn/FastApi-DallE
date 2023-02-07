import json

import uvicorn

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Create application
app = FastAPI(title='FastAPI DalLE')

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

import requests
quote_url = 'https://zenquotes.io/api/quotes'

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/quote/", response_class=HTMLResponse)
def quote(request: Request):
    if request.method == 'POST':
        quote = request.form['quote']
        author = request.form['author']
        quote_author = {'quote': quote, 'author': author}
        # Generate Image on Dall-E
        """
        try:
            url = get_image_url(quote)
            response = requests.get(url, stream=True)
            data = response.content

            # make filename and upload file to S3
            filename = make_filename(author)
            create_s3_upload_thread(filename, data)

            render_file = render_picture(data)
            # add file to db
            new_file = FileContent(title=author, filename=filename, data=data, rendered_data=render_file)
            db.session.add(new_file)
            db.session.commit()
            image = {'title': author, 'url': url}
            return render_template('quote.html', quote=quote_author, image=image, user_auth=user_auth)

        except Exception as e:
            print(e)
            flash('Image creation error!', 'alert')
        """

    try:
        response = requests.get(quote_url)
        data_str = response.text
        data = json.loads(data_str)[0]
        quote = data.get("q")
        author = data.get("a")
        quote_author = {'quote': quote, 'author': author}

    except Exception as e:
        print(e)
        quote_author = None
    user_auth = False
    return templates.TemplateResponse("quote.html", {"request": request, "quote":quote_author, "user_auth":user_auth})


@app.get("/create/", response_class=HTMLResponse)
def create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.get("/edit/", response_class=HTMLResponse)
def edit(request: Request):
    return templates.TemplateResponse("edit.html", {"request": request})


@app.get("/about/", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/login/", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout/", response_class=HTMLResponse)
def logout(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup/", response_class=HTMLResponse)
def logout(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/socket", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("socket.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # send "Connection established" message to client
        await websocket.send_text("Connection established!")

        # await for messages and send messages
        while True:
            msg = await websocket.receive_text()
            if msg.lower() == "close":
                await websocket.close()
                break
            else:
                print(f'CLIENT says - {msg}')
                await websocket.send_text(f"Your message was: {msg}")

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