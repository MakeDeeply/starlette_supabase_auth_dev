from starlette_wtf import StarletteForm
from wtforms import SelectField, StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

# local
from db import colors


class LoginRegisterForm(StarletteForm):
    css = {'class': 'form-control'}
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw=css)
    password = PasswordField('Password', validators=[DataRequired()], render_kw=css)


class PasswordForgotForm(StarletteForm):
    email = StringField('Email', validators=[DataRequired(), Email()])


class PasswordUpdateForm(StarletteForm):
    password = PasswordField('Password', validators=[DataRequired()])


class ColorForm(StarletteForm):
    color = SelectField('Color', choices=[(color, color.capitalize()) for color in colors], validators=[DataRequired()])
