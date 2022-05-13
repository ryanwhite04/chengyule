from ast import Pass
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, EqualTo, Length

class Registration(FlaskForm):
    username = StringField(label='Username', validators=[Length(min = 1, max = 40)])
    email = StringField(label='Email Address', validators=[Email()])
    password = PasswordField(label="Password", validators=[Length(min = 1)])
    confirm = PasswordField(label='Confirm Password', validators=[EqualTo("password")])
    submit = SubmitField(label='Register')
