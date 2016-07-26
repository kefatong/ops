#coding:utf-8

__author__ = 'eric'

from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import login_required
from flask.ext.login import current_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm, ChangeEmailRequestForm




@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('the confirmation link is invaild or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash(u'修改密码成功!')
            return redirect(url_for('main.index'))
        else:
            flash(u'输入密码错误!')

    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect('main.index')
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))

        token = user.generate_reset_token()
        send_email(user.email, 'Reset Your Password',
                'auth/email/reset_password', user=user, token=token)
        flash(u'请登录你的邮箱确认重置密码邮件')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET','POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token,form.password.data):
            flash(u'重置密码成功, 请重新登陆!')
            return redirect(url_for('auth.login'))
        else:
            flash(u'重置密码失败, 请确认token是否过期!')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)


@auth.route('/change-email', methods=['GET','POST'])
@login_required
def change_email_request():
    if current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = ChangeEmailRequestForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_change_email_token(new_email)
            send_email(new_email,'Change-Email','auth/email/change_email', user=current_user, token=token)
            flash(u'请登录你的邮箱确认修改邮件!')
            return redirect(url_for('main.index'))
        else:
            flash(u'输入密码错误,请重新输入!')

    return render_template('auth/change_email.html', form=form)

@auth.route('/change-email/<token>')
def change_email(token):
    if current_user.change_email(token):
        flash(u'修改邮箱地址成功!')
    else:
        flash(u'修改邮箱失败! 请尝试重新修改!')

    return redirect(url_for('main.index'))

