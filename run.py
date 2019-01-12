from G_app import app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# host='0.0.0.0'


'''
--- FORMS ---
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo
from flask_login import current_user
from G_app.models import User



--- ROUTES ---
import os
import sys
#import secrets
import random
import string
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from G_app.forms import LoginForm, UpdateForm, PostForm, PostFormGeneral, RequestResetForm, ResetPasswordForm
from G_app.models import User, Post, Chug, Groceries
from G_app import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

'''
