from ast import Pass
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, EqualTo, Length, DataRequired

class Registration(FlaskForm):
    username = StringField(label='Username', validators=[Length(min = 1, max = 40),  DataRequired()])
    email = StringField(label='Email Address', validators=[Email(),  DataRequired()])
    password = PasswordField(label="Password", validators=[Length(min = 1),  DataRequired()])
    confirm = PasswordField(label='Confirm Password', validators=[EqualTo("password"),  DataRequired()])
    submit = SubmitField(label='Register')

    
class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')
