from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.widgets import PasswordInput
from wtforms.validators import DataRequired, URL, Email


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", widget=PasswordInput(hide_value=False), validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class AddBookForm(FlaskForm):
    title = StringField(label="Book Title", validators=[DataRequired()])
    submit = SubmitField(label="Find Book")


class EditForm(FlaskForm):
    rating = SelectField(label='Stars', choices=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done')
