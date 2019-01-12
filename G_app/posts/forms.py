from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired
from flask_login import current_user
from G_app.models import User


def get_choices():
    choices = []
    users = User.query.all()
    for user in users:
        username = user.username
        if username != 'admin':
            choices.append((username, username))
    return choices


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png'])])
    target = RadioField('Choose Target', choices=get_choices())
    submit = SubmitField('Post')


class PostFormGeneral(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')
