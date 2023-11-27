'''
starlette_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from gotrue.errors import AuthApiError

# local
import settings
import db

templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


class NotFoundMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if response.status_code == 404:
            template = '404.jinja2'
            content = templates.TemplateResponse(template, {'request': request}).body
            return HTMLResponse(content, status_code=404)

        # response = await call_next(request)
        return response


class TokenCheckMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.cookies.get('access_token') is None:
            print('No auth')
            request.scope['identity'] = None
            response = await call_next(request)
            return response

        try:
            session = db.supabase.auth.get_user(request.cookies.get('access_token'))
            if session is not None:
                request.scope['identity'] = session.user
                response = await call_next(request)
                return response

        except AuthApiError as e:
            if request.cookies.get('refresh_token') is None:
                request.scope['identity'] = None
                return RedirectResponse(url=request.url_for('login')._url)

            refreshed_session = db.supabase.auth._refresh_access_token(request.cookies.get('refresh_token'))
            if refreshed_session:
                new_access_token = refreshed_session.session.access_token
                new_refresh_token = refreshed_session.session.refresh_token
                request.scope['identity'] = refreshed_session.user
                response = await call_next(request)
                response.set_cookie('access_token', new_access_token)
                response.set_cookie('refresh_token', new_refresh_token)
                return response
