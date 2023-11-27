from starlette.applications import Starlette
from starlette_wtf import CSRFProtectMiddleware
from middleware import NotFoundMiddleware, TokenCheckMiddleware
from routes import routes
from starlette_session import SessionMiddleware

app = Starlette(debug=True, routes=routes)
app.add_middleware(
    SessionMiddleware,
    secret_key='your_secret_key',
    cookie_name='session'
)
app.add_middleware(CSRFProtectMiddleware, csrf_secret='your_secret_key')

app.add_middleware(TokenCheckMiddleware)
app.add_middleware(NotFoundMiddleware)
