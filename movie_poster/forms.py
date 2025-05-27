from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    name = StringField('Họ và tên', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Tiêu đề', validators=[DataRequired(), Length(min=2, max=100)])
    message = TextAreaField('Nội dung', validators=[DataRequired(), Length(min=10, max=1000)])
    recaptcha = RecaptchaField()
    submit = SubmitField('Gửi tin nhắn')
