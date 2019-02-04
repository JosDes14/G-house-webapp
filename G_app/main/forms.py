from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextAreaField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange
from G_app.models import User


class VotingForm(FlaskForm):
    rating = IntegerField('Rating', validators=[DataRequired(), NumberRange(0,10)])
    clarification = TextAreaField('Optional clarification')


class WeeklyVotingForm(FlaskForm):
    voting_fields = FieldList(FormField(VotingForm), min_entries=4, max_entries=4)
    '''jos = IntegerField(User.query.get(1).username, validators=[DataRequired(), NumberRange(0,10)])
    jos_clarification = TextAreaField('Optional clarification')
    eash = IntegerField(User.query.get(2).username, validators=[DataRequired(), NumberRange(0,10)])
    eash_clarification = TextAreaField('Optional clarification')
    samy = IntegerField(User.query.get(5).username, validators=[DataRequired(), NumberRange(0,10)])
    samy_clarification = TextAreaField('Optional clarification')
    joe = IntegerField(User.query.get(4).username, validators=[DataRequired(), NumberRange(0,10)])
    joe_clarification = TextAreaField('Optional clarification')
    herb = IntegerField(User.query.get(3).username, validators=[DataRequired(), NumberRange(0,10)])
    herb_clarification = TextAreaField('Optional clarification')'''
    submit = SubmitField('Vote')
