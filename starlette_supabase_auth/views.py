'''
starlette_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
from starlette_wtf import csrf_protect
from starlette.requests import Request

# local
from decorators import login_required
from forms import ColorForm
from settings import templates, flash
import db

templates = templates()


async def home(request: Request):
    template = 'index.jinja2'
    user = request['identity'] or None  # set by the middleware in the request

    fav_color = None

    if user is not None:
        try:
            fav_color = db.get_user_color(user.id)
        except Exception as e:
            print('home ERROR:', e)

    context = {
        'colors': db.colors,
        'colorsTable': db.get_all_users_colors(),
        'fav_color': fav_color,
        'request': request,  # TBD: Pyramid vs. Starlette
    }
    return templates.TemplateResponse(template, context=context)


@login_required(redirect_url='/login')
@csrf_protect
async def profile(request: Request):

    if request.method == 'POST':
        form = await ColorForm.from_formdata(request)
        if await form.validate_on_submit():
            data = db.set_user_color(request['identity'].id, form.color.data)
            fav_color = data[0]['favourite_color']
            flash(request, message='Your new Color is %s!' % fav_color, _type='success')
        else:
            flash(request, message='Form is not valid. Please provide a valid color.', _type='error')

        your_color = db.get_user_color(request['identity'].id)
        context = {'request': request, 'form': form, 'your_color': your_color}
        return templates.TemplateResponse('profile.jinja2', context=context)

    form = await ColorForm.from_formdata(request)
    your_color = db.get_user_color(request['identity'].id)
    context = {
        'request': request,
        'form': form,
        'your_color': your_color,
    }
    return templates.TemplateResponse('profile.jinja2', context=context)
