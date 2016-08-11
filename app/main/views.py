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
import stat
import os
import re
import uuid

import ansible
import ansible.runner
import ansible.playbook
from ansible import callbacks
from ansible import utils
import json
import hashlib
import random
import time


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




def check_update(current_app,devices):
    if not  devices:
        return None
    cmdb_devices = set([ device['id'] for device in devices['devices']])
    ops_devices = set([device.device_id for device in Device.query.all()])

    print ops_devices.difference(cmdb_devices)
    if cmdb_devices.difference(ops_devices):
        for device_id in  cmdb_devices.difference(ops_devices):
            api_json = get_api_json(current_app, postfix='/device/', id=device_id)

            if api_json is None:
                continue

            api_json = api_json['device']
            device = Device()
            device.device_id = device_id
            device.an       = api_json['an']
            device.sn       = api_json['sn']
            device.hostname = api_json['hostname']
            device.ip       = api_json['ip']
            device.os       = api_json['os']
            device.cpumodel = api_json['cpumodel']
            device.cpucount = api_json['cpucount']
            device.memsize  = api_json['memsize']
            device.disksize = api_json['disksize']
            device.business = api_json['business']
            device.powerstatus = api_json['powerstatus']
            device.onstatus = api_json['onstatus']
            device.usedept  = api_json['usedept']
            device.usestaff = api_json['usestaff']
            device.mainuses = api_json['mainuses']
            device.managedept = api_json['managedept']
            device.managestaff = api_json['managestaff']
            device.instaff  = api_json['instaff']
            device.remarks  = api_json['remarks']

            db.session.add(device)
            print device.hostname



    #print devices

def update_device():
    pass




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
        taskClass.remarks = form.remarks.data
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
        taskClass.remarks = form.remarks.data
        db.session.add(taskClass)
        db.session.commit()
        flash(u'任务类型修改成功!')
        return redirect(url_for('main.show_deviceTaskClass'))
    form.name.data = taskClass.name
    form.remarks.data = taskClass.remarks
    return render_template('create_deviceTaskClass.html', form=form, taskClass=taskClass)


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
    form = EditDeviceGroupForm(None,True)
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
        redirect(url_for('main.show_deviceGroups'))
    return render_template('create_deviceGroup.html', form=form)




@main.route('/edit-device.deviceGroup/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def edit_deviceGroup(id):
    deviceGroup = DeviceGroup.query.get_or_404(id)
    form = EditDeviceGroupForm(deviceGroup,True)
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
        redirect(url_for('main.show_deviceGroups'))

    form.name.data = deviceGroup.name
    form.business.data = deviceGroup.business
    form.devices.data = deviceGroup.devices
    form.remarks.data = deviceGroup.remarks
    return render_template('create_deviceGroup.html', form=form)


@main.route('/delete-device.deviceGroup/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def delete_deviceGroup(id):
    deviceGroup = DeviceGroup.query.get_or_404(id)
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
        check_update(current_app,devices)

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

        #try:
        db.session.add(device)
        db.session.commit()
        flash(u'设备添加完成!')
        #except:
            #db.session.rollback()
            #flash(u'设备添加失败!')

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






@main.route('/show-device.running.tasks', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def show_deviceRunningTasks(id):
    pass


def generateInventory_hosts(current_app,devices=None):
    if not devices:
        return None

    app = current_app._get_current_object()
    FLASK_TMP_HOME = app.config['FLASK_TMP_HOME']
    print FLASK_TMP_HOME
    if not os.path.exists(FLASK_TMP_HOME):
        os.mkdir(FLASK_TMP_HOME)

    Inventory_devices = {
        "devices": {
            'hosts': [],
        },
    }

    print Inventory_devices

    for device in devices:
        if device.ip is None:
            flash(u'设备{0}IP地址未设置.'.format(device.hostname))
            return None
        Inventory_devices['devices']['hosts'].append(device.ip)

    if len(Inventory_devices['devices']['hosts']) < 1:
        return None


    Inventory_devices = json.dumps(Inventory_devices)
    print Inventory_devices
    md5 = hashlib.md5(Inventory_devices)
    print md5.hexdigest()

    json_devices = '''#!/usr/bin/env python\n# encoding: utf-8\nimport json\ndevices = json.dumps({0})\nprint devices\n'''.format(Inventory_devices)

    Inventory_devices_file = FLASK_TMP_HOME + '/tasks/{0}'.format(str(md5.hexdigest()))

    with open(Inventory_devices_file, 'w') as f:
        f.write(json_devices)
        os.chmod(Inventory_devices_file, stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)

    return Inventory_devices_file

def playbook_runner(playbook, inventory):
    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

    res = ansible.playbook.PlayBook(
        playbook=playbook,
        stats=stats,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        host_list = inventory,
    ).run()

    return res


@main.route('/push-tasksTo.devices', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def push_TasksTo_devices():
    form = EditPushTasksToDeviceForm()
    if form.validate_on_submit():

        Inventory_tasks = []

        devices = form.devices.data
        tasks = form.tasks.data
        if not devices and not tasks:
            flash(u'选择主机有误')
            return render_template('push_tasks.html', form=form)

        devices = [ Device.query.get_or_404(device) for device in devices ]
        Inventory_hosts_file = generateInventory_hosts(current_app,devices)

        for task in tasks:
            t = DeviceTasks.query.get_or_404(task)
            if not t.path:
                flash(u'脚本{0}上传文件有误,请重新上传。')
                redirect(url_for('main.index'))
            Inventory_tasks.append(t.path)

        print Inventory_tasks

        tasks_res = []
        for task in  Inventory_tasks:
            print task
            tasks_res.append(playbook_runner(task, Inventory_hosts_file))

        print tasks_res

        return render_template('push_tasks.html', form=form, tasks_res=tasks_res)


    return render_template('push_tasks.html', form=form)


def command_runner(user,command, inventory):
    res = ansible.runner.Runner(
                module_name='shell',  # 调用shell模块，这个代码是为了示例执行shell命令
                module_args= command,  # shell命令
                remote_user=user,
                host_list=inventory,
                pattern='all',
                private_key_file='/Users/kefatong/.ssh/id_rsa'
            ).run()
    return res



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
        if devices is None:
            return redirect(url_for('main.index'))

        devices = [Device.query.get_or_404(device) for device in devices]
        Inventory_hosts_file = generateInventory_hosts(current_app, devices)

        command = form.command.data
        if command:
            if re.findall('rm', command) or re.findall('mv', command):
                flash(u'内容包含删除了移动命令')
                return redirect(url_for('main.push_CommandsTo_device'))

            command_res = command_runner('kefatong',command, Inventory_hosts_file)
            print command_res
            return render_template('push_commands.html', form=form, command_res=command_res)

    return render_template('push_commands.html', form=form)


@main.route('/push-tasksTo.deviceGroups', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DEVICE_LOOK)
def push_TasksTo_deviceGroups(id):
    pass


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
