from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import EmailField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class NewPostForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    subtitle = StringField('subtitle', validators=[DataRequired()])
    author = StringField("author", validators=[DataRequired()])
    img_url = StringField("img url", validators=[DataRequired()])
    body = CKEditorField('Body')
    submit = SubmitField('Create new post')

# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    email = EmailField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Register")

# TODO: Create a LoginForm to login existing users


# TODO: Create a CommentForm so users can leave comments below posts
