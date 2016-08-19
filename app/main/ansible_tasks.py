# coding:utf8


import re
import os
import stat
import json
import Queue
import hashlib
import ansible
import ansible.runner
import ansible.playbook
from ansible import callbacks
from ansible import utils
from flask import flash, redirect, url_for


def command_runner(user, command, inventory, view):
    if re.findall('rm', command) or re.findall('mv', command):
        flash(u'内容包含删除了移动命令')
        return redirect(url_for(view))

    res = ansible.runner.Runner(
        module_name='shell',  # 调用shell模块，这个代码是为了示例执行shell命令
        module_args=command,  # shell命令
        remote_user=user,
        host_list=inventory,
        pattern='all',
        private_key_file='/root/.ssh/id_rsa'
    ).run()
    return res



def playbook_runner(playbook, inventory):
    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

    res = ansible.playbook.PlayBook(
        playbook=playbook,
        stats=stats,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        host_list=inventory,
    ).run()

    return res


def task_runner(taskList, inventory):
    task_res = []
    for task in taskList:
        res = playbook_runner(task['path'], inventory)
        task_res.append({
            'name' : task['name'],
            'res' : res,
        })

    if not task_res:
        return False

    return task_res



def GenerateInventory(current_app, devices=None):
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

    json_devices = '''#!/usr/bin/env python\n# encoding: utf-8\nimport json\ndevices = json.dumps({0})\nprint devices\n'''.format(
        Inventory_devices)

    Inventory_devices_file = FLASK_TMP_HOME + '/tasks/{0}'.format(str(md5.hexdigest()))

    with open(Inventory_devices_file, 'w') as f:
        f.write(json_devices)
        os.chmod(Inventory_devices_file, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

    return Inventory_devices_file


