# coding:utf8

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
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
import stat
import os
import re
import uuid
import json
import hashlib
import random
import time

import difflib
import sys


import cobbler.api as capi

cobbler_handle = capi.BootAPI()


import ansible_tasks
import cobbler_tasks


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


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    json_device = get_api_json(current_app, postfix='/devices/')
    print json_device

    return redirect(url_for('main.show_devices'))


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


def get_api_json(app, postfix, id=None):
    if not app:
        return None

    token = get_api_token(app)
    print token

    if not token:
        return None

    app = app._get_current_object()
    API_URL = app.config['FLASK_USE_CMDB_API']
    print API_URL

    if postfix and not id:
        request = requests.get(API_URL + postfix, auth=requests.auth.HTTPBasicAuth(token, ''))

        try:
            json = request.json()
            return json
        except:
            return None

    else:
        request = requests.get(API_URL + postfix + str(id), auth=requests.auth.HTTPBasicAuth(token, ''))

        try:
            json = request.json()
            return json
        except:
            return None


def check_update(current_app, devices):
    if not devices:
        return None
    cmdb_devices = set([device['id'] for device in devices['devices']])
    ops_devices = set([device.device_id for device in Device.query.all()])

    print ops_devices.difference(cmdb_devices)
    if cmdb_devices.difference(ops_devices):
        for device_id in cmdb_devices.difference(ops_devices):
            api_json = get_api_json(current_app, postfix='/device/', id=device_id)

            if api_json is None:
                continue

            api_json = api_json['device']
            device = Device()
            device.device_id = device_id
            device.an = api_json['an']
            device.sn = api_json['sn']
            device.hostname = api_json['hostname']
            device.ip = api_json['ip']
            device.os = api_json['os']
            device.cpumodel = api_json['cpumodel']
            device.cpucount = api_json['cpucount']
            device.memsize = api_json['memsize']
            device.disksize = api_json['disksize']
            device.business = api_json['business']
            device.powerstatus = api_json['powerstatus']
            device.onstatus = api_json['onstatus']
            device.usedept = api_json['usedept']
            device.usestaff = api_json['usestaff']
            device.mainuses = api_json['mainuses']
            device.managedept = api_json['managedept']
            device.managestaff = api_json['managestaff']
            device.instaff = api_json['instaff']
            device.remarks = api_json['remarks']

            db.session.add(device)
            print device.hostname



            # print devices


def update_device():
    pass


@main.route('/show-module.class', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_moduleClass():
    moduleClass = ModuleClass.query.all()
    return render_template('show_moduleClass.html', moduleClass=moduleClass)


@main.route('/create-module.class', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_moduleClass():
    form = EditModuleClassForm(None)
    if form.validate_on_submit():
        moduleClass = ModuleClass()
        moduleClass.name = form.name.data
        moduleClass.remarks = form.remarks.data
        moduleClass.instaff = current_user.username
        db.session.add(moduleClass)
        db.session.commit()

        flash(u'任务类型添加成功!')
        return redirect(url_for('main.show_moduleClass'))

    return render_template('create_moduleClass.html', form=form)


@main.route('/edit-module.class/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def edit_moduleClass(id):
    moduleClass = ModuleClass.query.get_or_404(id)
    form = EditModuleClassForm(moduleClass)
    if form.validate_on_submit():
        moduleClass.name = form.name.data
        moduleClass.remarks = form.remarks.data
        moduleClass.instaff = current_user.username
        db.session.add(moduleClass)
        db.session.commit()

        flash(u'任务类型添加成功!')
        return redirect(url_for('main.show_moduleClass'))

    form.name.data = moduleClass.name
    form.remarks.data = moduleClass.remarks
    return render_template('edit_moduleClass.html', form=form, moduleClass=moduleClass)


@main.route('/delete-module.class/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_moduleClass(id):
    moduleClass = ModuleClass.query.get_or_404(id)
    db.session.delete(moduleClass)
    db.session.commit()
    flash(u'目录删除成功!')
    return redirect(url_for('main.show_moduleClass'))


@main.route('/show-device.TaskClass', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceTaskClass():
    taskClass = TaskClass.query.all()
    return render_template('show_deviceTaskClass.html', taskClass=taskClass)


@main.route('/create-device.TaskClass', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceTaskClass():
    form = EditDeviceTaskClassForm(None)
    if form.validate_on_submit():
        taskClass = TaskClass()
        taskClass.name = form.name.data
        taskClass.module_id = form.module_id.data
        taskClass.remarks = form.remarks.data
        taskClass.instaff = current_user.username
        db.session.add(taskClass)
        db.session.commit()

        flash(u'任务类型添加成功!')
        return redirect(url_for('main.show_deviceTaskClass'))

    return render_template('create_deviceTaskClass.html', form=form)


@main.route('/edit-device.TaskClass/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def edit_deviceTaskClass(id):
    taskClass = TaskClass.query.get_or_404(id)
    form = EditDeviceTaskClassForm(taskClass)
    if form.validate_on_submit():
        taskClass.name = form.name.data
        taskClass.module_id = form.module_id.data
        taskClass.remarks = form.remarks.data
        db.session.add(taskClass)
        db.session.commit()
        flash(u'任务类型修改成功!')
        return redirect(url_for('main.show_deviceTaskClass'))
    form.name.data = taskClass.name
    form.module_id.data = taskClass.module_id
    form.remarks.data = taskClass.remarks
    return render_template('edit_deviceTaskClass.html', form=form, taskClass=taskClass)


@main.route('/delete-device.TaskClass/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceTaskClass(id):
    taskClass = TaskClass.query.get_or_404(id)
    db.session.delete(taskClass)
    db.session.commit()
    flash(u'任务类型删除成功!')
    return redirect(url_for('main.show_deviceTaskClass'))


@main.route('/show-device.deviceGroup/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceGroup(id):
    deviceGroup = DeviceGroup.query.get_or_404(id)
    form = EditDeviceGroupForm(deviceGroup=deviceGroup, edit=None)
    form.name.data = deviceGroup.name
    form.business.data = deviceGroup.business
    form.devices.data = deviceGroup.devices
    form.remarks.data = deviceGroup.remarks
    return render_template('show_deviceGroup.html', form=form, deviceGroup=deviceGroup)


@main.route('/show-device.deviceGroups', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceGroups():
    deviceGroups = DeviceGroup.query.all()
    return render_template('show_deviceGroups.html', deviceGroups=deviceGroups)


@main.route('/create-device.deviceGroup', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceGroup():
    form = EditDeviceGroupForm(None, True)
    if form.validate_on_submit():
        deviceGroup = DeviceGroup()
        deviceGroup.name = form.name.data
        deviceGroup.business = form.business.data
        for device in form.devices.data:
            deviceGroup.devices.append(Device.query.get(device))
        deviceGroup.remarks = form.remarks.data
        deviceGroup.instaff = current_user.username

        db.session.add(deviceGroup)
        db.session.commit()
        return redirect(url_for('main.show_deviceGroups'))
    return render_template('create_deviceGroup.html', form=form)


@main.route('/edit-device.deviceGroup/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def edit_deviceGroup(id):
    deviceGroup = DeviceGroup.query.get_or_404(id)
    form = EditDeviceGroupForm(deviceGroup, True)
    if form.validate_on_submit():
        deviceGroup.name = form.name.data
        deviceGroup.business = form.business.data

        for device in form.devices.data:
            deviceGroup.devices.remove(device)

        for device in form.devices.data:
            deviceGroup.devices.append(Device.query.get(device))
        deviceGroup.remarks = form.remarks.data

        db.session.add(deviceGroup)
        db.session.commit()
        return redirect(url_for('main.show_deviceGroups'))

    form.name.data = deviceGroup.name
    form.business.data = deviceGroup.business
    form.devices.data = deviceGroup.devices
    form.remarks.data = deviceGroup.remarks
    return render_template('edit_deviceGroup.html', form=form, deviceGroup=deviceGroup)


@main.route('/delete-device.deviceGroup/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceGroup(id):
    deviceGroup = DeviceGroup.query.get_or_404(id)
    for device in deviceGroup.devices.all():
        deviceGroup.devices.remove(device)
    db.session.delete(deviceGroup)
    db.session.commit()
    return redirect(url_for('main.show_deviceGroups'))


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
    form = EditDeviceTaskGroupForm(deviceTaskGroup=None, edit=True)
    if form.validate_on_submit():
        deviceTaskGroup = DeviceTaskGroup()
        deviceTaskGroup.name = form.name.data
        for task in form.tasks.data:
            deviceTaskGroup.tasks.append(DeviceTasks.query.get(task))
        deviceTaskGroup.type = form.type.data
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
    form = EditDeviceTaskGroupForm(deviceTaskGroup, edit=True)
    if form.validate_on_submit():
        deviceTaskGroup.name = form.name.data

        for task in deviceTaskGroup.tasks.all():
            deviceTaskGroup.tasks.remove(task)

        for task in form.tasks.data:
            deviceTaskGroup.tasks.append(DeviceTasks.query.get(task))

        deviceTaskGroup.type = form.type.data
        deviceTaskGroup.enabled = form.enabled.data
        deviceTaskGroup.remarks = form.remarks.data
        deviceTaskGroup.instaff = current_user.username

        db.session.add(deviceTaskGroup)
        db.session.commit()

        return redirect(url_for('main.show_deviceTaskGroups'))

    form.name.data = deviceTaskGroup.name
    form.tasks.data = deviceTaskGroup.tasks
    form.type.data = deviceTaskGroup.type
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
        shutil.copy(script_name, new_script_name)
        os.remove(script_name)

        deviceTask.path = new_script_name
        deviceTask.arch = form.arch.data
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


@main.route('/show-device.task/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceTask(id):
    deviceTaskGroup = DeviceTaskGroup.query.get_or_404(id)
    return render_template('show_deviceTask.html', deviceTasks=deviceTaskGroup.tasks.all())


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
    form = EditDeviceTaskGroupForm(deviceTaskGroup, edit=False)
    form.name.data = deviceTaskGroup.name
    form.tasks.data = deviceTaskGroup.tasks.all()
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


@main.route('/show-device.device/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_device(id):
    deviceGroup = DeviceGroup.query.get_or_404(id)
    return render_template('show_device.html', devices=deviceGroup.devices.all())


@main.route('/show-device.devices', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_devices():
    devices = get_api_json(current_app, postfix='/devices/')
    print devices
    if devices:
        check_update(current_app, devices)

    devices = Device.query.all()
    return render_template('show_devices.html', is_json=True, devices=devices)


@main.route('/create-device.device', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_EDIT)
def create_device():
    form = EditDeviceForm()
    if form.validate_on_submit():
        device = Device()
        device.hostname = form.hostname.data
        device.ip = form.ip.data
        device.an = form.an.data
        device.sn = form.sn.data
        device.os = form.os.data
        device.manufacturer = form.manufacturer.data
        device.brand = form.brand.data
        device.model = form.model.data
        device.onstatus = form.onstatus.data
        device.usedept = form.usedept.data
        device.usestaff = form.usestaff.data
        device.mainuses = form.mainuses.data
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

        return redirect(url_for('main.show_devices'))
    return render_template('create_device.html', form=form)


@main.route('/edit-device.device/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_EDIT)
def edit_device(id):
    device = Device.query.get_or_404(id)
    form = EditDeviceForm()
    if form.validate_on_submit():
        device.hostname = form.hostname.data
        device.ip = form.ip.data
        device.an = form.an.data
        device.sn = form.sn.data
        device.os = form.os.data
        device.manufacturer = form.manufacturer.data
        device.brand = form.brand.data
        device.model = form.model.data
        device.onstatus = form.onstatus.data
        device.usedept = form.usedept.data
        device.usestaff = form.usestaff.data
        device.mainuses = form.mainuses.data
        device.cpumodel = form.cpumodel.data
        device.cpucount = form.cpucount.data
        device.memsize = form.memsize.data
        device.disksize = form.disksize.data
        device.business = form.business.data
        device.powerstatus = form.powerstatus.data
        device.remarks = form.remarks.data

        # try:
        db.session.add(device)
        db.session.commit()
        flash(u'设备添加完成!')
        # except:
        # db.session.rollback()
        # flash(u'设备添加失败!')

        return redirect(url_for('main.show_devices'))

    form.hostname.data = device.hostname
    form.ip.data = device.ip
    form.an.data = device.an
    form.sn.data = device.sn
    form.manufacturer.data = device.manufacturer
    form.brand.data = device.brand
    form.model.data = device.model
    form.onstatus.data = device.onstatus
    form.usedept.data = device.usedept
    form.usestaff.data = device.usestaff
    form.mainuses.data = device.mainuses
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

    return redirect(url_for('main.show_devices'))


########################################################################


# @main.route('/show-device.running.tasks', methods=['GET', 'POST'])
# @login_required
# @permission_required(Permission.DEVICE_LOOK)
# def show_deviceRunningTasks(id):
#     pass


def dump_json_device(current_app,devices):
    if not devices:
        return False
    deviceList = [Device.query.get_or_404(device) for device in devices]
    if not deviceList:
        return False

    dumpFile = ansible_tasks.GenerateInventory(current_app,deviceList)
    if not dumpFile:
        return False

    return dumpFile





def take_tasks(current_app, tasks):
    taskList = []
    if not tasks:
        return False

    for task in tasks:
        t = DeviceTasks.query.get_or_404(task)
        if not t.path:
            flash(u'任务{0}上传有误, 请检查脚本文件是否正确。')
            return redirect(url_for('main.push_TasksTo_devices'))
        taskList.append({
            'name' : t.taskname,
            'path' : t.path,
        })

    if not taskList:
        return False

    return taskList






@main.route('/push-tasksTo.devices', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def push_TasksTo_devices():
    form = EditPushTasksToDeviceForm()
    if form.validate_on_submit():


        devices = form.devices.data
        tasks = form.tasks.data

        dumpfile = dump_json_device(current_app,devices)
        if not dumpfile:
            flash(u'选择设备有误.')
            return redirect(url_for('main.push_TasksTo_devices'))

        taskList = take_tasks(current_app, tasks)
        if not taskList:
            flash(u'选择任务有误.')
            return redirect(url_for('main.push_TasksTo_devices'))

        tasks_res = ansible_tasks.task_runner(taskList, dumpfile)
        print tasks_res

        return render_template('push_tasks.html', form=form, tasks_res=tasks_res)

    return render_template('push_tasks.html', form=form)


def dump_json_deviceGroup(current_app, deviceGroup):
    if not deviceGroup:
        return False

    deviceList = []
    for group in deviceGroup:
        Group = DeviceGroup.query.get_or_404(group)
        if Group:
            deviceList.extend(Group.devices.all())

    dumpFile = ansible_tasks.GenerateInventory(current_app, deviceList)
    if not dumpFile:
        return False

    return dumpFile


def take_taskGroup(current_app, taskGroup):
    taskList = []
    if not taskGroup:
        return False

    for group in taskGroup:
        Group = DeviceTaskGroup.query.get_or_404(group).tasks.all()
        if Group:
            for task in Group:

                if not task.path:
                    flash(u'脚本{0}上传文件有误,请重新上传。'.format(task.taskname))
                    return redirect(url_for('main.push_TasksTo_deviceGroup'))
                taskList.append({
                    'name': task.taskname,
                    'path': task.path,
                })

    if not taskList:
        return False

    return taskList


@main.route('/push-tasksTo.deviceGroup', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def push_TasksTo_deviceGroup():
    form = EditPushTasksToDeviceGroupForm()
    if form.validate_on_submit():

        deviceGroup = form.deviceGroup.data
        taskGroup = form.taskGroup.data

        dumpfile = dump_json_deviceGroup(current_app, deviceGroup)
        if not dumpfile:
            flash(u'选择设备有误.')
            return redirect(url_for('main.push_TasksTo_deviceGroup'))

        taskList = take_taskGroup(current_app, taskGroup)
        if not taskList:
            flash(u'选择任务有误.')
            return redirect(url_for('main.push_TasksTo_deviceGroup'))

        tasks_res = ansible_tasks.task_runner(taskList, dumpfile)
        print tasks_res

        return render_template('push_taskGroup.html', form=form, tasks_res=tasks_res)

    return render_template('push_taskGroup.html', form=form)




@main.route('/push-command-to.device', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def push_CommandsTo_device():
    form = EditRunningCommandForm()
    if form.validate_on_submit():

        if form.saved.data:
            histroy = histroyCommands()
            histroy.command = form.command.data
            histroy.remarks = form.remarks.data
            histroy.user_id = current_user.id
            db.session.add(histroy)
            db.session.commit()

        devices = form.devices.data
        dumpfile = dump_json_device(current_app, devices)
        if not dumpfile:
            flash(u'选择设备有误')
            return redirect(url_for('main.push_CommandsTo_device'))

        command = form.command.data
        if not command:
            flash(u'请输入要执行的命令')
            return redirect(url_for('main.push_CommandsTo_device'))

        command_res = ansible_tasks.command_runner('eric', command, dumpfile, view='main.push_CommandsTo_device')
        print command_res
        return render_template('push_commands.html', form=form, command_res=command_res)

    return render_template('push_commands.html', form=form)



@main.route('/show-device.system', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceSystems():
    systems = System.query.all()
    return render_template('show_deviceSystems.html', systems=systems)



@main.route('/create-device.system', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceSystem():
    form = EditSystemForm()
    if form.validate_on_submit():
        system = System()
        system.device_id = form.device_id.data
        system.os_version = form.os_version.data
        system.type = form.type.data
        system.an = form.an.data
        system.sn = form.sn.data
        system.hostname = form.hostname.data
        system.power_ip = form.power_ip.data
        system.post = form.post.data
        system.ip = form.ip.data
        system.status = 1
        system.instaff = current_user.username

        db.session.add(system)
        db.session.commit()

        interfaces = {
            'eth0': {
                'bonding': u'',
                'bonding_master': u'',
                'bonding_opts': u'',
                'bridge_opts': u'',
                'cnames': [],
                'connected_mode': False,
                'dhcp_tag': u'',
                'dns_name': u'114.114.114.114',
                'if_gateway': u'172.16.46.2',
                'interface_master': u'',
                'interface_type': u'',
                'ip_address': '',
                'ipv6_address': u'',
                'ipv6_default_gateway': u'',
                'ipv6_mtu': u'',
                'ipv6_prefix': u'',
                'ipv6_secondaries': [],
                'ipv6_static_routes': [],
                'mac_address': '00:0C:29:F1:BC:31',
                'management': False,
                'mtu': u'',
                'netmask': '255.255.255.0',
                'static': True,
                'static_routes': [],
                'subnet': u'',
                'virt_bridge': 'xenbr0'
            }
        }

        new_system = cobbler_handle.new_system()
        new_system.name = system.hostname
        new_system.profile = system.os_version
        new_system.hostname = system.hostname
        new_system.set_hostname = system.hostname
        interfaces['eth0']['ip_address'] = system.ip
        new_system.interfaces = interfaces
        new_system.set_netboot_enabled = True
        cobbler_handle.add_system(new_system)
        cobbler_handle.sync()
        os.system('service cobblerd restart')

        return redirect(url_for('main.show_deviceSystems'))

    return render_template('create_system.html', form=form)


@main.route('/delete-device.system/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceSystem(id):
    system = System.query.get_or_404(id)
    cobbler_system = cobbler_handle.find_system(system.hostname)
    if cobbler_system:
        cobbler_handle.remove_system(cobbler_system)
        cobbler_handle.sync()
        os.system('service cobblerd restart')
    db.session.delete(system)
    return redirect(url_for('main.show_deviceSystems'))


@main.route('/deploy-device.system/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def deploy_deviceSystem(id):

    def password_undo(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        password = data.get('password', None)

        if not password:
            return False
        return password

    system = System.query.get_or_404(id)
    devicePower = DevicePower.query.filter(DevicePower.device_id == system.id)



    if not devicePower.all() and devicePower.all() > 1:
        flash(u'请检查资产电源管理口配置是否正确')
        return redirect(url_for('main.show_deviceSystems'))

    devicePower = devicePower.first()
    if not devicePower:
        flash(u'电源管理卡未配置.')
        return redirect(url_for('main.show_deviceSystems'))

    if not devicePower.ip and not devicePower.user and not devicePower.password_hash:
        flash(u'电源管理卡设置有误, 请检查电源管理卡IP, User, Password 是否配置正确.')
        return redirect(url_for('main.show_deviceSystems'))

    if not password_undo(devicePower.password_hash):
        flash(u'密码Token解密失败, 请检查密码')
        return redirect(url_for('main.show_deviceSystems'))


    cobbler_system = cobbler_handle.find_system(system.hostname)
    cobbler_system.power_address = devicePower.ip
    cobbler_system.power_user = devicePower.user
    cobbler_system.power_type = 'ipmitlan'
    cobbler_system.power_pass = password_undo(devicePower.password_hash)
    cobbler_system.reboot(cobbler_system)




@main.route('/show-device.compliance', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceCompliance():
    compliances = ComplianceTasks.query.all()
    return render_template('show_deviceCompliance.html', compliances=compliances)



@main.route('/create-device.compliance', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceCompliance():
    form = EditComplianceTasksForm()
    if form.validate_on_submit():
        compliance = ComplianceTasks()
        compliance.name = form.name.data
        compliance.deviceGroup = form.deviceGroup.data
        compliance.taskGroup = form.taskGroup.data
        compliance.enabled = form.enabled.data
        compliance.remarks = form.remarks.data
        compliance.instaff = current_user.username

        db.session.add(compliance)
        db.session.commit()
        return redirect(url_for('main.show_deviceCompliance'))


    return render_template('create_deviceCompliance.html', form=form)
    #return render_template('create_deviceCompliance.html')



@main.route('/edit-device.compliance/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def edit_deviceCompliance(id):

    compliance = ComplianceTasks.query.get_or_404(id)
    form = EditComplianceTasksForm()
    if form.validate_on_submit():
        compliance.name = form.name.data
        compliance.deviceGroup = form.deviceGroup.data
        compliance.taskGroup = form.taskGroup.data
        compliance.enabled = form.enabled.data
        compliance.remarks = form.remarks.data

        db.session.add(compliance)
        db.session.commit()
        return redirect(url_for('main.show_deviceCompliance'))

    form.name.data = compliance.name
    #form.deviceGroup.data = compliance.deviceGroup
    #form.taskGroup.data = compliance.taskGroup
    form.enabled.data = compliance.enabled
    form.remarks.data = compliance.remarks
    return render_template('edit_deviceCompliance.html', form=form, compliance=compliance)
    #return render_template('create_deviceCompliance.html')


@main.route('/deploy-device.compliance/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def deploy_deviceCompliance(id):
    compliance = ComplianceTasks.query.get_or_404(id)
    compliance.status = 2
    db.session.add(compliance)
    db.session.commit()
    return redirect(url_for('main.show_deviceCompliance'))



@main.route('/delete-device.compliance/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceCompliance(id):
    compliances = ComplianceTasks.query.get_or_404(id)
    db.session.delete(compliances)
    db.session.commit()
    return redirect(url_for('main.show_deviceCompliance'))


@main.route('/show-device.SoftwareDistribution', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceSoftwareDistribution():
    softwareDistribution = SoftwareDistribution.query.all()
    return render_template('show_softwareDistribution.html', softwareDistribution=softwareDistribution)



@main.route('/create-device.SoftwareDistribution', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceSoftwareDistribution():
    form = EditSoftwareDistributionForm()
    if form.validate_on_submit():
        softwareDistribution = SoftwareDistribution()
        softwareDistribution.name = form.name.data
        if form.devices.data:
            for device in form.devices.data:
                softwareDistribution.devices.append(Device.query.get_or_404(device))
        softwareDistribution.taskGroup = form.taskGroup.data
        softwareDistribution.type = form.type.data
        softwareDistribution.status = 1
        softwareDistribution.remarks = form.remarks.data

        db.session.add(softwareDistribution)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('create_softwareDistribution.html', form=form)


@main.route('/delete-device.SoftwareDistribution/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceSoftwareDistribution(id):
    softwareDistribution = SoftwareDistribution.query.get_or_404(id)
    for device in softwareDistribution.devices.all():
        softwareDistribution.devices.remove(device)
    db.session.delete(softwareDistribution)
    db.session.commit()
    flash(u'删除任务{0}成功'.format(softwareDistribution.name))
    return redirect(url_for('main.show_deviceSoftwareDistribution'))



@main.route('/deploy-device.SoftwareDistribution/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def deploy_deviceSoftwareDistribution(id):
    softwareDistribution = SoftwareDistribution.query.get_or_404(id)
    softwareDistribution.status =2
    db.session.add(softwareDistribution)
    db.session.commit()
    flash(u'任务{0}执行'.format(softwareDistribution.name))
    return redirect(url_for('main.show_deviceSoftwareDistribution'))




@main.route('/deploy-device.ContrastTask/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def deploy_deviceContrastTask(id):
    contrastTasks = ContrastTasks.query.get_or_404(id)
    contrastTasks.status = 2

    files = []

    for task in contrastTasks.fileOrDirectory.all():
        device = Device.query.get_or_404(task.device_id)
        files.append({
            'filePath' : task.path,
            'device' : device.ip,
        })


    db.session.add(contrastTasks)
    db.session.commit()
    return redirect(url_for('main.show_deviceContrastTask'))


@main.route('/show-device.ContrastTask', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceContrastTask():
    contrastTask = ContrastTasks.query.all()
    return render_template('show_deviceContrastTask.html', contrastTask=contrastTask)



@main.route('/create-device.ContrastTask', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceContrastTask():
    form = EditContrastTasksForm()
    if form.validate_on_submit():
        contrastTask = ContrastTasks()
        contrastTask.name = form.name.data
        contrastTask.type = form.type.data
        for file in form.fileOrDirectory.data:
            contrastTask.fileOrDirectory.append(ContrastFilesOrDirectory.query.get_or_404(file))
        contrastTask.remarks = form.remarks.data
        contrastTask.instaff = current_user.username

        db.session.add(contrastTask)
        db.session.commit()
        flash(u'创建{0}成功'.format(contrastTask.name))
        return redirect(url_for('main.index'))

    return render_template('create_deviceConstratTask.html', form=form)


@main.route('/edit-device.ContrastTask/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def edit_deviceContrastTask(id):
    contrastTask = ContrastTasks.query.get_or_404(id)
    form = EditContrastTasksForm()
    if form.validate_on_submit():
        contrastTask.name = form.name.data
        contrastTask.type = form.type.data

        for file in contrastTask.fileOrDirectory.all():
            contrastTask.fileOrDirectory.remove(file)

        for file in form.fileOrDirectory.data:
            contrastTask.fileOrDirectory.append(ContrastFilesOrDirectory.query.get_or_404(file))
        contrastTask.remarks = form.remarks.data
        contrastTask.instaff = current_user.username

        db.session.add(contrastTask)
        db.session.commit()
        flash(u'修改{0}成功'.format(contrastTask.name))
        return redirect(url_for('main.index'))

    form.name.data = contrastTask.name
    form.type.data = contrastTask.type
    form.fileOrDirectory.data = []

    for file in contrastTask.fileOrDirectory.all():
        form.fileOrDirectory.data.append(file)

    form.enabled.data = contrastTask.enabled
    form.remarks.data = contrastTask.remarks
    return render_template('edit_deviceConstratTask.html', form=form, contrastTask=contrastTask)


@main.route('/delete-device.ContrastTask/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceContrastTask(id):
    contrastTask = ContrastTasks.query.get_or_404(id)
    for file in contrastTask.fileOrDirectory.all():
        contrastTask.fileOrDirectory.remove(file)
    db.session.delete(contrastTask)
    db.session.commit()
    flash(u'删除{0}成功!'.format(contrastTask.name))
    return redirect(url_for('main.index'))



@main.route('/show-device.ContrastFileOrDirectory', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceContrastFileOrDirectory():
    contrastFileOrDirectory = ContrastFilesOrDirectory.query.all()
    return render_template('show_ContrastFileOrDirectory.html', contrastFileOrDirectory=contrastFileOrDirectory)



@main.route('/create-device.ContrastFileOrDirectory', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def create_deviceContrastFileOrDirectory():
    form = EditConttastFileOrDirectoryForm()
    if form.validate_on_submit():
        contrastFileOrDirectory = ContrastFilesOrDirectory()
        contrastFileOrDirectory.name = form.name.data
        contrastFileOrDirectory.type = form.type.data
        contrastFileOrDirectory.device_id = form.device_id.data
        contrastFileOrDirectory.path = form.path.data
        contrastFileOrDirectory.enabled = form.enabled.data
        contrastFileOrDirectory.remarks = form.remarks.data
        contrastFileOrDirectory.instaff = current_user.username

        db.session.add(contrastFileOrDirectory)
        db.session.commit()

        flash(u'创建{0}成功'.format(contrastFileOrDirectory.name))
        return redirect(url_for('main.index'))

    return render_template('create_deviceConstratFileOrDirectory.html', form=form)



@main.route('/edit-device.ContrastFileOrDirectory/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def edit_deviceContrastFileOrDirectory(id):
    contrastFileOrDirectory = ContrastFilesOrDirectory.query.get_or_404(id)
    form = EditConttastFileOrDirectoryForm()
    if form.validate_on_submit():
        contrastFileOrDirectory.name = form.name.data
        contrastFileOrDirectory.type = form.type.data
        contrastFileOrDirectory.device_id = form.device_id.data
        contrastFileOrDirectory.path = form.path.data
        contrastFileOrDirectory.enabled = form.enabled.data
        contrastFileOrDirectory.remarks = form.remarks.data
        contrastFileOrDirectory.instaff = current_user.username

        db.session.add(contrastFileOrDirectory)
        db.session.commit()

        flash(u'创建{0}成功'.format(contrastFileOrDirectory.name))
        return redirect(url_for('main.index'))


    form.name.data = contrastFileOrDirectory.name
    form.type.data = contrastFileOrDirectory.type
    form.device_id.data = contrastFileOrDirectory.device_id
    form.path.data = contrastFileOrDirectory.path
    form.enabled.data = contrastFileOrDirectory.enabled
    form.remarks.data = contrastFileOrDirectory.remarks
    return render_template('edit_deviceConstratFileOrDirectory.html', form=form, contrastFileOrDirectory=contrastFileOrDirectory)


@main.route('/delete-device.ContrastFileOrDirectory/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceContrastFileOrDirectory(id):
    contrastFileOrDirectory = ContrastFilesOrDirectory.query.get_or_404(id)
    db.session.delete(contrastFileOrDirectory)
    db.session.commit()
    return redirect(url_for('main.index'))





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
