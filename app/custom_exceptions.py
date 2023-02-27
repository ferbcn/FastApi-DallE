from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="app/templates")

class NotAuthenticatedException(Exception):
    pass

    # these two argument are mandatory
    def exc_handler(request, exc, message="Not authorized, please log in first!"):
        return templates.TemplateResponse("login.html", {"request": request, "alert_message": message})
        #return RedirectResponse(url='/loginform/')
