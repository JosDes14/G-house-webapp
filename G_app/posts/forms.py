from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, RadioField, IntegerField
from wtforms.validators import DataRequired
from G_app.models import User
from G_app.posts.utils import get_choices



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


class ChallengeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    target = RadioField('Choose Target', choices=get_choices())
    submit = SubmitField('Challenge')


class EditChallengeForm(FlaskForm):
    description = TextAreaField('Edit description', validators=[DataRequired()])
    amount = IntegerField('Edit Amount', validators=[DataRequired()])
    submit = SubmitField('Accept')
