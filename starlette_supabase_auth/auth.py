'''
starlette_supabase_auth sample - Color Chooser

Copyright 2023 by Make Deeply - released under MIT License
'''
from decorators import login_required, redirect_if_logged_in
from forms import PasswordUpdateForm, PasswordForgotForm, LoginRegisterForm

from gotrue.errors import AuthApiError
from gotrue import (
    SignInWithEmailAndPasswordCredentials,
    SignUpWithEmailAndPasswordCredentials,
    Options,
)

from starlette_wtf import csrf_protect
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

# local
from db import supabase
from settings import templates, flash

templates = templates()


@redirect_if_logged_in(redirect_url='/')
async def login(request: Request):

    if request.method == 'POST':
        form = await LoginRegisterForm.from_formdata(request)

        if await form.validate_on_submit():
            signInCred = SignInWithEmailAndPasswordCredentials(
                email=str(form.email.data), password=str(form.password.data)
            )

            try:
                sess = supabase.auth.sign_in_with_password(signInCred).session
                response = RedirectResponse(url='/profile', status_code=HTTP_303_SEE_OTHER)

                response.set_cookie('access_token', sess.access_token)
                response.set_cookie('refresh_token', sess.refresh_token)

                flash(request, message='Login Successful!', _type='success')
                return response
            except Exception as e:
                print(e)
                flash(request, message='Failed to Login. Please try again', _type='error')
                context = {'request':request, 'form': form, 'error': 'Wrong Email Or Password'}
                return templates.TemplateResponse('login.jinja2', context=context)

        context = {
            'request': request,
            'form': form
        }
        return templates.TemplateResponse('login.jinja2', context=context)

    form = await LoginRegisterForm.from_formdata(request)
    context = {'request': request, 'form': form}
    return templates.TemplateResponse('login.jinja2', context=context)


@login_required()
async def logout(request: Request):
    try:
        supabase.auth.sign_out()
        response = RedirectResponse('/login')
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        flash(request, message='You are now logged out.', _type='warning')

        return response
    except Exception as e:
        print(e)
        flash(request, message='Failed to Logout. Please try again', _type='danger')
        return RedirectResponse(request.url_for('home')._url)


@redirect_if_logged_in(redirect_url='/')
async def oauth_login(request: Request):
    provider = request.path_params['provider']
    sign_in_with_oauth = supabase.auth.sign_in_with_oauth({'provider':provider, 'options':{'redirect_to':request.url_for('auth_')._url}})
    url = sign_in_with_oauth.url
    return RedirectResponse(url=url)


@redirect_if_logged_in(redirect_url='/')
async def auth_(request: Request):
    code = request.query_params.get('code')

    if code is not None:
        try:
            session = supabase.auth.exchange_code_for_session({'auth_code':code})
            response = RedirectResponse(url=request.url_for('profile')._url, status_code=HTTP_303_SEE_OTHER)
            response.set_cookie('access_token', session.session.access_token)
            response.set_cookie('refresh_token', session.session.refresh_token)
            flash(request, message='Successfully logged in!', _type='success')
            return response
        except Exception as e:
            print(e)
            flash(request, message=str(e), _type='error')
            return RedirectResponse(request.url_for('login')._url, status_code=HTTP_303_SEE_OTHER)
    else:
        flash(request, message='Failed to Login. Please try again.', _type='danger')
        return RedirectResponse(request.url_for('login')._url, status_code=HTTP_303_SEE_OTHER)


@login_required()
@csrf_protect
async def reset_password(request: Request):

    if request.method == 'POST':
        form = await PasswordUpdateForm.from_formdata(request)
        if await form.validate_on_submit():
            try:
                supabase.auth.update_user(attributes={'password': form.password.data})
                flash(request, message='Password successfully changed!', _type='success')
            except Exception as e:
                flash(request, message=str(e), _type='error')
                context = {'request': request, 'form':form, 'error': 'Your Password Must Be different From Your Previous One And More Than 6 Characters Long'}
                return templates.TemplateResponse('reset_password.jinja2', context=context)

        else:
            flash(request, message='Form is not valid', _type='error')

        return templates.TemplateResponse('reset_password.jinja2', {'request': request, 'form': form})

    form = await PasswordUpdateForm.from_formdata(request)
    return templates.TemplateResponse('reset_password.jinja2', {'request': request, 'form': form})


@csrf_protect
async def forgot_password(request: Request):
    if request.method == 'POST':
        form = await PasswordForgotForm.from_formdata(request)

        if await form.validate_on_submit():
            try:
                opts = Options(redirect_to=request.url_for('home')._url)
                supabase.auth.reset_password_email(form.email.data, options=opts)

                flash(request, message='Please check your email and reset your password.', _type='warning')
                return RedirectResponse(url=request.url_for('home')._url, status_code=HTTP_303_SEE_OTHER)

            except AuthApiError as e:
                print(e)
                flash(request,message='Failed to send reset link please try again.' , _type='error')
                context = {'request': request, 'form': form, 'error': 'Make sure you provided the correct email'}
                return templates.TemplateResponse('forgot_password.jinja2', context=context)

    form = await PasswordForgotForm.from_formdata(request)
    return templates.TemplateResponse('forgot_password.jinja2', {'request': request, 'form': form})


@csrf_protect
@redirect_if_logged_in(redirect_url='/')
async def register(request: Request):

    if request.method == 'POST':
        form = await LoginRegisterForm.from_formdata(request)

        if await form.validate_on_submit():
            creds = SignUpWithEmailAndPasswordCredentials(email=str(form.email.data), password=str(form.password.data))
            try:
                supabase.auth.sign_up(creds)
                return RedirectResponse(url='/login', status_code=HTTP_303_SEE_OTHER)
            except Exception as e:
                flash(request, message=str(e), _type='error')
                context = {'request': request, 'form': form, 'error':'Failed to register. Make sure this email is not already being used and the password length is 6 or more characters.' }
                return templates.TemplateResponse('register.jinja2', context=context)

        context = {'request': request, 'form': form}
        return templates.TemplateResponse('register.jinja2', context=context)

    form = await LoginRegisterForm.from_formdata(request)
    context = {'request': request, 'form': form}
    return templates.TemplateResponse('register.jinja2', context=context)


async def auth_recover(request: Request):
    token_hash = request.query_params.get('token_hash')
    auth_type = request.query_params.get('type')

    if token_hash and auth_type:
        try:
            supabase.auth.verify_otp(params={'token_hash': token_hash, 'type': auth_type})

            sess = supabase.auth.get_session()
            access_token = sess.access_token
            refresh_token = sess.refresh_token

            response = RedirectResponse(url=request.url_for('reset_password')._url, status_code=HTTP_303_SEE_OTHER)
            response.set_cookie('access_token', access_token)
            response.set_cookie('refresh_token', refresh_token)
            flash(request, message='Please set a new password', _type='warning')
            return response
        except Exception as e:
            print(e)
            flash(request, message='Error, Please try again.', _type='danger')
            return RedirectResponse(url = request.url_for('forgot_password'))

    flash(request, message='Error, Please try again.', _type='danger')
    return RedirectResponse(url = request.url_for('login'))
