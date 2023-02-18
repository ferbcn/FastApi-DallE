from fastapi.responses import HTMLResponse, RedirectResponse

class NotAuthenticatedException(Exception):
    pass

    # these two argument are mandatory
    def exc_handler(request, exc):
        return RedirectResponse(url='/')
