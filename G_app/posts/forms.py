from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Length, ValidationError
from G_app.models import User
from G_app.posts.utils import get_choices
from datetime import datetime



class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')


class PostFormGeneral(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')


class ChallengeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=300)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    time_limit = DateTimeField('Time Limit', format='%d-%m-%Y %H:%M:%S',  validators=[DataRequired()])
    submit = SubmitField('Challenge')

    def validate_time_limit(self, time_limit):
        if time_limit.data < datetime.today():
            raise ValidationError("Please choose a date that is in the future.")



class EditChallengeForm(FlaskForm):
    description = TextAreaField('Edit description', validators=[DataRequired()])
    amount = IntegerField('Edit Amount', validators=[DataRequired()])
    time_limit = DateTimeField('Time Limit', format='%d-%m-%Y %H:%M:%S',  validators=[DataRequired()])
    submit = SubmitField('Accept')

    def validate_time_limit(self, time_limit):
        if time_limit.data < datetime.today():
            raise ValidationError("You took too long negotiating, this date is no longer in the future.")


class BetForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=300)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    odds = FloatField('Odds', validators=[DataRequired()])
    submit = SubmitField('Create bet')


class EditBetForm(FlaskForm):
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=300)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    odds = FloatField('Odds', validators=[DataRequired()])
    submit = SubmitField('Accept')
