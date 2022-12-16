from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('Om mig'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Tilføj'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Venligst anvend et andet brugernavn.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Tilføj')


class PostForm(FlaskForm):
    post = TextAreaField(_l('Skriv noget!'), validators=[DataRequired()])
    submit = SubmitField(_l('Tilføj'))


class SearchForm(FlaskForm):
    q = StringField(_l('Søg'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    message = TextAreaField(_l('Meddelelse'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Tilføj'))
