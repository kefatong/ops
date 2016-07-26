#coding:utf-8

__author__ = 'eric'

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('keep me logged in')
    submit = SubmitField('Log In')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old Password', validators=[Required()])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField(u'确定')


class ResetPasswordRequestForm(Form):
    email = StringField('Email', validators=[Required(),Length(1,64), Email()])
    submit = SubmitField(u'确定')

    def validate_email(self,field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Unknown Email.')


class ResetPasswordForm(Form):
    email = StringField('Email', validators=[Required(),Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField(u'确认')

    def validate_email(self,field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('Unknown Email')

class ChangeEmailRequestForm(Form):
    email = StringField('Email', validators=[Required(),Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField(u'确认')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')
