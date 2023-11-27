from pathlib import Path
from starlette.config import Config
from starlette.templating import Jinja2Templates
from starlette.requests import Request

BASE_DIR = Path(__file__).parent

TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

def flash(request: Request, message, _type='info'):
    if '_flashes' not in request.session:
        request.session['_flashes'] = []
    request.session['_flashes'].append((_type, message))


def get_flashed_messages(request):
    flashes = request.session.pop('_flashes') if '_flashes' in request.session else []
    return flashes


def context_processor():
    return {
        'get_flash': lambda r: get_flashed_messages(r)
    }


def templates():
    templates_ = Jinja2Templates(directory=str(TEMPLATES_DIR))
    templates_.env.globals.update(context_processor())
    return templates_


config = Config('.env')

DEBUG = config('DEBUG', cast=bool, default=False)
