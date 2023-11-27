from functools import wraps
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER


def login_required(redirect_url: str = '/login'):
    def decorator(view_func):
        async def wrapper(request: Request, *args, **kwargs):
            # Check if the user is already logged in
            access_token = request.cookies.get('access_token')
            if not access_token:
                return RedirectResponse(url=redirect_url, status_code=HTTP_303_SEE_OTHER)

            return await view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def redirect_if_logged_in(redirect_url: str = '/'):
    def decorator(view_func):
        async def wrapper(request: Request, *args, **kwargs):
            # Check if the user is already logged in
            access_token = request.cookies.get('access_token')
            if access_token:
                return RedirectResponse(url=redirect_url, status_code=HTTP_303_SEE_OTHER)

            return await view_func(request, *args, **kwargs)

        return wrapper

    return decorator
