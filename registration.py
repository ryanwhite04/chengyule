from ast import Pass
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, EqualTo, Length

class Registration(FlaskForm):
    username = StringField(label='Username', validators=[Length(min = 3, max = 40)])
    email = StringField(label='Email Address', validators=[Email()])
    password = PasswordField(label="Password", validators=[Length(min = 10)])
    confirm_password = PasswordField(label='Confirm Password', validators=[EqualTo("password")]) 
    submitbutton = SubmitField(label='Register Now!')
