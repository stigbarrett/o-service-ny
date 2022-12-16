from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, email_validator
from wtforms import validators
from wtforms.fields.html5 import EmailField
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l('Brugernavn'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Husk mig'))
    submit = SubmitField(_l('Log Ind'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Brugernavn'), validators=[DataRequired()])
    email = EmailField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Gentag Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Registrer'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Venligst vælg et andet brugernavn.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Venligst vælg en anden email adresse.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Anmod om nulstilling af Password'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Gentag Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Anmod om nulstilling af Password'))
