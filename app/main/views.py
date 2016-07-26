# coding:utf8

from flask import render_template, redirect, url_for, flash, current_app, abort, request, make_response
from flask.ext.login import login_required, current_user
from ..decorators import admin_required, permission_required
from werkzeug import secure_filename
from . import main
from .forms import *
from .. import db
from ..models import *
from ..email import send_email
import requests
import os
import uuid


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    logs = Logger.query.order_by(Logger.logtime.desc()).all()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.position = form.position.data
        current_user.qq = form.qq.data
        current_user.phone = form.phone.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'提交成功!')
        return redirect(url_for('main.edit_profile', username=current_user.username, logs=logs))

    form.name.data = current_user.name
    form.username.data = current_user.username
    form.position.data = current_user.position
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    form.qq.data = current_user.qq
    form.phone.data = current_user.phone
    return render_template('edit_profile.html', form=form, username=current_user.username, logs=logs)


@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():

    json_device = get_api_json(current_app, postfix='/devices/')
    #if json_device:
    print json_device

    return render_template('index.html')



########################################################################

def get_api_token(app):
    app = app._get_current_object()

    API_URL = app.config['FLASK_USE_CMDB_API']
    API_USER = app.config['FLASK_USE_CMDB_USER']
    API_PASSWORD = app.config['FLASK_USE_CMDB_PASSWORD']


    if API_URL and API_USER and API_PASSWORD:
        print API_URL + '/token/'
        print API_USER, API_PASSWORD
        request = requests.get(API_URL + '/token', auth=requests.auth.HTTPBasicAuth(API_USER, API_PASSWORD))
        try:
            token = request.json()
            return token['token']
        except:
            return None


def get_api_json(app, postfix):

    if app and postfix:

        token = get_api_token(app)
        print token
        if not token:
            return None

        app = app._get_current_object()
        API_URL = app.config['FLASK_USE_CMDB_API']
        print API_URL
        request = requests.get(API_URL + postfix, auth=requests.auth.HTTPBasicAuth(token, ''))

        try:
            json = request.json()
            return json
        except:
            return None





@main.route('/show-device.devices', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_devices():

    devices = get_api_json(current_app, postfix='/devices/')
    if not devices:
        render_template('show_devices.html')
    return render_template('show_devices.html', is_json=True, devices=devices)

    #devices = Device.query.all()
    #return render_template('show_devices.html', devices=devices)


@main.route('/show-device.taskGroups', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceTaskGroups():
    deviceTaskGroup = DeviceTaskGroup.query.all()
    return render_template('show_deviceTaskGroups.html', deviceTaskGroup=deviceTaskGroup)


@main.route('/create-device.taskGroup', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceTaskGroup():
    form = EditDeviceTaskGroupForm(deviceTaskGroup=None)
    if form.validate_on_submit():
        deviceTaskGroup = DeviceTaskGroup()
        deviceTaskGroup.name = form.name.data
        print form.tasks.data
        for task in form.tasks.data:
            deviceTaskGroup.tasks.append(DeviceTasks.query.get(task))
        deviceTaskGroup.enabled = form.enabled.data
        deviceTaskGroup.remarks = form.remarks.data
        deviceTaskGroup.instaff = current_user.username

        db.session.add(deviceTaskGroup)
        db.session.commit()

        return redirect(url_for('main.show_deviceTaskGroups'))
    return render_template('create_deviceTaskGroup.html', form=form)


@main.route('/edit-device.taskGroup/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def edit_deviceTaskGroup(id):
    deviceTaskGroup = DeviceTaskGroup.query.get_or_404(id)
    form = EditDeviceTaskGroupForm(deviceTaskGroup)
    if form.validate_on_submit():
        deviceTaskGroup.name = form.name.data

        for task in deviceTaskGroup.tasks.all():
            deviceTaskGroup.tasks.remove(task)
            

        for task in form.tasks.data:
            deviceTaskGroup.tasks.append(DeviceTasks.query.get(task))

        deviceTaskGroup.enabled = form.enabled.data
        deviceTaskGroup.remarks = form.remarks.data
        deviceTaskGroup.instaff = current_user.username

        db.session.add(deviceTaskGroup)
        db.session.commit()

        return redirect(url_for('main.show_deviceTaskGroups'))

    form.name.data = deviceTaskGroup.name
    form.tasks.data = deviceTaskGroup.tasks
    form.enabled.data = deviceTaskGroup.enabled
    form.remarks.data = deviceTaskGroup.remarks

    return render_template('edit_deviceTaskGroup.html', form=form, deviceTaskGroup=deviceTaskGroup)


@main.route('/delete-device.taskGroup/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceTaskGroup(id):
    deviceTaskGroup = DeviceTaskGroup.query.get_or_404(id)
    db.session.delete(deviceTaskGroup)
    db.session.commit()
    return redirect(url_for('main.show_deviceTaskGroups'))



@main.route('/create-device.task', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceTask():
    form = EditDeviceTaskForm()
    if form.validate_on_submit():

        deviceTask = DeviceTasks()
        deviceTask.taskname = form.taskname.data
        deviceTask.type = form.type.data
        deviceTask.scriptname = secure_filename(form.scriptfile.data.filename)


        app = current_app._get_current_object()
        FLASK_UPLOAD_HOME = app.config['FLASK_UPLOAD_HOME']

        SCRIPT_DIRS = FLASK_UPLOAD_HOME + '/script_dirs/{0}'.format(form.type.data)
        if not os.path.exists(SCRIPT_DIRS):
            os.makedirs(SCRIPT_DIRS)

        UUID = str(uuid.uuid4())
        script_name = SCRIPT_DIRS + '/' + UUID
        form.scriptfile.data.save(script_name)

        with open(script_name) as script:
            md5 = hashlib.md5()
            md5.update(script.read())

        deviceTask.md5code = md5.hexdigest()

        import shutil
        new_script_name = SCRIPT_DIRS + '/' + deviceTask.md5code
        shutil.copy(script_name,new_script_name)
        os.remove(script_name)

        deviceTask.path    = new_script_name
        deviceTask.arch    = form.arch.data
        deviceTask.version = form.version.data
        deviceTask.enabled = form.enabled.data
        deviceTask.remarks = form.remarks.data
        deviceTask.instaff = current_user.username

        db.session.add(deviceTask)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('create_deviceTask.html', form=form)



@main.route('/show-device.taskScript/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceTaskScript(id):
    deviceTask = DeviceTasks.query.get_or_404(id)
    form = EditDeviceTaskForm()
    form.taskname.data = deviceTask.taskname
    form.type.data = deviceTask.type
    form.scriptname.data = deviceTask.scriptname
    form.path.data = deviceTask.path
    form.arch.data = deviceTask.arch
    form.version.data = deviceTask.version
    form.enabled.data = deviceTask.enabled
    form.remarks.data = deviceTask.remarks
    form.instaff.data = deviceTask.instaff

    return render_template('show_deviceTaskScript.html', form=form, deviceTask=deviceTask)



@main.route('/show-device.tasks', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceTasks():
    deviceTasks = DeviceTasks.query.all()
    return render_template('show_deviceTasks.html', deviceTasks=deviceTasks)


@main.route('/show-device.taskGroup/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceTaskGroup(id):
    deviceTaskGroup = DeviceTaskGroup.query.get_or_404(id)
    form = EditDeviceTaskGroupForm(None)
    form.name.data = deviceTaskGroup.name
    form.tasks.data = deviceTaskGroup.tasks
    form.enabled.data = deviceTaskGroup.enabled
    form.remarks.data = deviceTaskGroup.remarks
    return render_template('show_deviceTaskGroup.html', deviceTaskGroup=deviceTaskGroup, form=form)



@main.route('/delete-device.task/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceTask(id):
    deviceTask = DeviceTasks.query.get_or_404(id)
    db.session.delete(deviceTask)

    return redirect(url_for('main.show_deviceTasks'))



@main.route('/create-device.device', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_EDIT)
def create_device():
    form = EditDeviceForm()
    if form.validate_on_submit():
        device = Device()
        device.deviceType = form.deviceType.data
        device.onstatus = form.onstatus.data
        device.usedept = form.usedept.data
        device.usestaff = form.usestaff.data
        device.mainuses = form.mainuses.data
        device.managedept = form.managedept.data
        device.managestaff = form.managestaff.data
        device.hostname = form.hostname.data
        device.os = form.os.data
        device.cpumodel = form.cpumodel.data
        device.cpucount = form.cpucount.data
        device.memsize = form.memsize.data
        device.disksize = form.disksize.data
        device.business = form.business.data
        device.powerstatus = form.powerstatus.data
        device.remarks = form.remarks.data

        try:
            db.session.add(device)
            db.session.commit()
            flash(u'虚拟机添加完成!')
        except:
            db.session.rollback()
            flash(u'虚拟机添加失败!')

        return redirect(url_for('main.show_device'))

    return render_template('create_device.html', form=form)


@main.route('/edit-device.device/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_EDIT)
def edit_device(id):
    device = Device.query.get_or_404(id)
    form = EditDeviceForm()
    if form.validate_on_submit():
        device.deviceType = form.deviceType.data
        device.onstatus = form.onstatus.data
        device.usedept = form.usedept.data
        device.usestaff = form.usestaff.data
        device.mainuses = form.mainuses.data
        device.managedept = form.managedept.data
        device.managestaff = form.managestaff.data
        device.device_id = form.device_id.data
        device.hostname = form.hostname.data
        device.os = form.os.data
        device.cpumodel = form.cpumodel.data
        device.cpucount = form.cpucount.data
        device.memsize = form.memsize.data
        device.disksize = form.disksize.data
        device.business = form.business.data
        device.powerstatus = form.powerstatus.data
        device.remarks = form.remarks.data

        try:
            db.session.add(device)
            db.session.commit()
            flash(u'设备添加完成!')
        except:
            db.session.rollback()
            flash(u'设备添加失败!')

        return redirect(url_for('main.show_devices'))

    form.deviceType.data = device.deviceType
    form.onstatus.data = device.onstatus
    form.usedept.data = device.usedept
    form.usestaff.data = device.usestaff
    form.mainuses.data = device.mainuses
    form.managedept.data = device.managedept
    form.managestaff.data = device.managestaff
    form.device_id.data = device.device_id
    form.pool.data = device.pool
    form.hostname.data = device.hostname
    form.os.data = device.os
    form.cpumodel.data = device.cpumodel
    form.cpucount.data = device.cpucount
    form.memsize.data = device.memsize
    form.disksize.data = device.disksize
    form.business.data = device.business
    form.powerstatus.data = device.powerstatus
    form.remarks.data = device.remarks

    return render_template('edit_device.html', form=form, device=device)


@main.route('/delete-device.device/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_DEL)
def delete_device(id):
    device = Device.query.get_or_404(id)

    try:
        db.session.delete(device)
        db.session.commit()
        flash(u'虚拟机: {0} 已删除!'.format(device.hostname))
    except:
        db.session.rollback()
        flash(u'虚拟机: {0} 删除失败!'.format(device.hostname))

    return redirect(url_for('main.show_virtmachine'))

########################################################################



@main.route('/xxx')
def xxx():
    return render_template('xxx.html')


# @main.route('/test', methods=['GET', 'POST'])
# @login_required
# def test():
#     form = EditProfileForm()
#     if form.validate_on_submit():
#         current_user.name = form.name.data
#         current_user.username = form.username.data
#         current_user.qq = form.qq.data
#         current_user.phone = form.phone.data
#         current_user.location = form.location.data
#         current_user.about_me = form.about_me.data
#         db.session.add(current_user)
#         flash(u'提交成功!')
#         return redirect(url_for('main.test',username=current_user.username))
#
#     form.name.data = current_user.name
#     form.username.data = current_user.username
#     form.location.data = current_user.location
#     form.about_me.data = current_user.about_me
#     form.qq.data = current_user.qq
#     form.phone.data = current_user.phone
#     return render_template('test.html',form=form)
#

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'For Administrators!'


@main.route('/moderator')
@login_required
@permission_required(Permission.ADMINISTER)
def for_moderators_only():
    return 'For moderators!'


if __name__ == '__main__':
    manager.run()
