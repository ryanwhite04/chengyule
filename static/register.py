from ast import Pass
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
class registration(FlaskForm):
    username = StringField(label= 'Username')
    email = StringField(label='Email Address')
    password = PasswordField(label="password")
    Confirm_password= PasswordField(label='Confrim_password') 