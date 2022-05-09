from ast import Pass
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
class Registration(FlaskForm):
    username = StringField(label= 'Username')
    email = StringField(label='Email Address')
    password = PasswordField(label="Password")
    Confirm_password= PasswordField(label='Confirm Password') 
    submitbutton = SubmitField(label='Create Account')
