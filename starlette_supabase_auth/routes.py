'''
starlette_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

# local
import settings
from views import home, profile
from auth import login, logout, oauth_login, register, auth_, auth_recover, forgot_password, reset_password

static = StaticFiles(directory=str(settings.STATIC_DIR))

routes = [

    Mount('/static', static, name='static'),

    Route('/', home, name='home'),

    Route('/login', login, name='login', methods=['GET', 'POST']),
    Route('/register', register, name='register', methods=['GET', 'POST']),
    Route('/profile', profile, name='profile', methods=['GET', 'POST']),
    Route('/logout', logout, name='logout'),

    Route('/auth', auth_, name='auth_'),
    Route('/auth/recover', auth_recover, name='auth_recover'),
    Route('/oauth_login/{provider}', oauth_login, name='oauth_login'),

    Route('/forgot_password', forgot_password, name='forgot_password', methods=['GET', 'POST']),
    Route('/reset_password', reset_password, name='reset_password', methods=['GET', 'POST']),
]
