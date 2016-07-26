# -*- coding:utf-8 -*-

__author__ = 'eric'

import hashlib
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from flask import current_app, request, url_for
from . import db
from . import login_manager


class Permission:
    USER_EDIT = 0x001

    DEVICE_LOOK = 0x002
    DEVICE_EDIT = 0x004
    DEVICE_DEL = 0x008

    ADMINISTER = 0x2000


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, index=True, default=False)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def to_json(self):
        json_role = {
            'url' : self.id,
            'name' : self.name,
            'default' : self.default,
            'permissions' : self.permissions,
            'users' : self.users,
        }

        return json_role

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.DEVICE_LOOK, True),

            'manager': (Permission.USER_EDIT |
                        Permission.DEVICE_LOOK |
                        Permission.DEVICE_EDIT, False ),

            'Administrator': (Permission.USER_EDIT |
                              Permission.DEVICE_LOOK |
                              Permission.DEVICE_EDIT |
                              Permission.DEVICE_DEL  |
                              Permission.ADMINISTER, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)  # Email Address
    username = db.Column(db.String(64), unique=True, index=True)  # Username
    password_hash = db.Column(db.String(128))  # password Md5 Hash
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # Role 鍏宠仈 Role table
    name = db.Column(db.String(64))  # 鐪熷疄濮撳悕
    location = db.Column(db.String(64))  # 鍦板潃
    position = db.Column(db.String(64))  # 职位
    about_me = db.Column(db.Text())  # 鍏充簬鎴�
    phone = db.Column(db.String(11))  # 手机号码
    qq = db.Column(db.String(13))  # QQ号码
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 娉ㄥ唽鏃堕棿
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 鏈�鍚庣櫥褰曟椂闂�
    confirmed = db.Column(db.Boolean, default=False)  # 璐︽埛鐘舵��
    avatar_hash = db.Column(db.String(32))  # 澶村儚
    logs = db.relationship('Logger', backref='user', lazy='dynamic')


    def to_json(self):
        json_user = {
            'url' : self.id,
            'email' : self.email,
            'username' : self.username,
            'password_hash' : self.password_hash,
            'role' : self.role,
            'name' : self.name,
            'location' : self.location,
            'position' : self.position,
            'about_me' : self.about_me,
            'phone' : self.phone,
            'qq' : self.qq,
            'member_sine' : self.member_since,
            'last_seen' : self.last_seen,
        }

        return json_user

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        if self.role is None:
            if self.email == current_app.config.get('FLASK_ADMIN', None):
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('UTF-8')).hexdigest()


    @staticmethod
    def insert_admin_user():

        r = Role()
        r.insert_roles()
        adminRole = Role.query.all()[-1]

        u = User.query.filter_by(username='administrator').first()
        if u is None:
            u = User()
        u.name = 'Admin'
        u.email = 'kefatong@qq.com'
        u.username = 'administrator'
        u.password = '123456'
        u.confirmed = True
        u.role = adminRole

        db.session.add(u)
        db.session.commit()


    @staticmethod
    def generate_fake(count=1000):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     position=forgery_py.lorem_ipsum.sentence(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                print "db commit email : {0} Error".format(u.email)
                db.session.rollback()

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://secure.gravatar.com/avatar'

        hash = self.avatar_hash or hashlib.md5(self.email.encode('UTF-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default,
                                                                     rating=rating)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('confirm', None) != self.id:
            return False

        self.confirmed = True
        print self.confirmed
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('reset', None) != self.id:
            return False

        self.password = new_password
        db.session.add(self)
        return True

    def generate_change_email_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('change_email') != self.id:
            return False

        new_email = data.get('new_email', None)

        if new_email is None:
            return False

        if self.query.filter_by(email=new_email).first() is not None:
            return False

        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('UTF-8')).hexdigest()
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username




class DevicePower(db.Model):
    __tablename__ = 'devicePowers'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    enabled = db.Column(db.Boolean, default=False)
    ip = db.Column(db.String(64))  # 杩滄帶鍗P鍦板潃
    user = db.Column(db.String(64))
    password_hash = db.Column(db.String(256))
    powerid = db.Column(db.String(256))
    device_id = db.Column(db.ForeignKey('devices.id'))
    isdelete = db.Column(db.Boolean, default=False)  # 鏄惁鍒犻櫎
    remarks = db.Column(db.Text)  # 澶囨敞
    instaff = db.Column(db.String(64))  # 褰曞叆浜�
    inputtime = db.Column(db.DateTime, default=datetime.now)  # 褰曞叆鏃堕棿


    def generate_password_token(self, password):
        from itsdangerous import JSONWebSignatureSerializer as Serializer
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': password})

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = self.generate_password_token(password)


    def to_json(self):
        json_power = {
            'url' : self.id,
            'type' : self.type,
            'enabled' : self.enabled,
            'ip' : self.ip,
            'user' : self.user,
            'password': self.password_hash,
            'powerid': self.powerid,
            'device_id' : self.device_id,
        }

        return json_power

    def __repr__(self):
        return '<DevicePower %r>' %self.id




class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64))  # Hostname
    sn = db.Column(db.String(64), unique=True, index=True)  # SN 璁惧搴忓垪鍙�
    os = db.Column(db.String(64))  # os绫诲瀷
    cpumodel = db.Column(db.String(64))  # CPU 鍨嬪彿
    cpucount = db.Column(db.Integer)  # CPU 鏍告暟
    memsize = db.Column(db.Integer)  # 鍐呭瓨瀹归噺
    disksize = db.Column(db.String(64))
    business = db.Column(db.Integer)    #所属业务
    powerstatus = db.Column(db.Integer)  #电源状态
    onstatus = db.Column(db.Integer)  # 浣跨敤鐘舵��
    usedept = db.Column(db.String(64))  # 浣跨敤閮ㄩ棬
    usestaff = db.Column(db.String(64))  # 閮ㄩ棬浣跨敤浜�
    mainuses = db.Column(db.String(128))  # 涓昏鐢ㄩ��
    managedept = db.Column(db.String(64))  # 绠＄悊閮ㄩ棬
    managestaff = db.Column(db.String(64))  # 绠＄悊浜�
    isdelete = db.Column(db.Boolean)
    instaff = db.Column(db.String(64))  # 褰曞叆浜�
    inputtime = db.Column(db.DateTime, default=datetime.now)  # 褰曞叆鏃堕棿
    remarks = db.Column(db.Text)  # 澶囨敞

    def to_json(self):
        json_virtMachine = {
            'url' : self.id,
            'device' : self.device_id,
            'deviceType': self.deviceType,
            'virtType': self.virtType,
            'pool_id' : self.pool_id,
            'hostname' : self.hostname,
            'os' : self.os,
            'cpumodel' : self.cpumodel,
            'cpucount' : self.cpucount,
            'memsize' : self.memsize,
            'disksize' : self.disksize,
            'business' : self.business,
            'powerstatus' : self.powerstatus,
            'onstatus' : self.onstatus,
            'usedept' : self.usedept,
            'usestaff' : self.usestaff,
            'mainues' : self.mainuses,
            'managedept' : self.managestaff,
            'managestaff' : self.managestaff,
            'remarks' : self.remarks,
            'isdelete' : self.isdelete,
        }
        return json_virtMachine


    def __repr__(self):
        return '<VirtMachine %r>' % self.hostname




registrations = db.Table('registrations',
    db.Column('deviceTaskGroup_id', db.Integer, db.ForeignKey('deviceTaskGroup.id')),
    db.Column('deviceTask_id', db.Integer, db.ForeignKey('deviceTasks.id')),

)

class DeviceTaskGroup(db.Model):
    __tablename__ = 'deviceTaskGroup'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    enabled = db.Column(db.Boolean)    #是否启用
    run_priority = db.Column(db.String(128))
    tasks = db.relationship('DeviceTasks', secondary=registrations, backref=db.backref('taskGroup', lazy='dynamic'), lazy='dynamic')
    isdelete = db.Column(db.Boolean)
    instaff = db.Column(db.String(64))  # 褰曞叆浜�
    inputtime = db.Column(db.DateTime, default=datetime.now)  # 褰曞叆鏃堕棿
    remarks = db.Column(db.Text)  # 澶囨敞

    def __repr__(self):
        return '<TaskScripts %r>' % self.name


class DeviceTasks(db.Model):
    __tablename__ = 'deviceTasks'
    id = db.Column(db.Integer, primary_key=True)
    taskname = db.Column(db.String(64))     #任务名称
    scriptname = db.Column(db.String(256))  #脚本名称
    type = db.Column(db.Integer)        #脚本类型   python  shell  playbook  perl
    arch = db.Column(db.Integer)        #系统架构   避免脚本运行出错
    md5code = db.Column(db.String(128))  #脚本md5码   防止被修改
    path = db.Column(db.String(256))     #脚本uuid
    version = db.Column(db.String(20))   #脚本版本
    enabled = db.Column(db.Boolean)   #启用
    isdelete = db.Column(db.Boolean)
    instaff = db.Column(db.String(64))   #录入人
    inputtime = db.Column(db.DateTime, default=datetime.now)  # 录入时间
    remarks = db.Column(db.Text)  # 备注

    def __repr__(self):
        return '<TaskScripts %r>' % self.taskname


class DeploySystem(db.Model):
    __tablename__ = 'DeploySystem'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer)       #设备id  通过cmdb读取设备
    uuid = db.Column(db.String(64))         #设备UUID  选择设备后自动获取设备UUID  在正式安装时判断是否与设备一致
    ip = db.Column(db.String(20))           #设备IP地址 选择设备后自动获取设备IP  在正式安装时判断是否与设备一致
    version = db.Column(db.Integer)         #系统版本
    tasks = db.Column(db.Integer)           #任务列表   安装系统后需要执行的
    is_deploy = db.Column(db.Integer)       #新创建任务后不直接安装, 需要手动确认安装信息


    def __repr__(self):
        return '<TaskScripts %r>' % self.hostname



class Logger(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    logtime = db.Column(db.DateTime, default=datetime.now())
    content = db.Column(db.String(256))
    # action  [ 1: add , 2: edit, 3: del ]
    action = db.Column(db.String(32))
    logobjtype = db.Column(db.String(64))
    logobj_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Logs %r>' % self.user_id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

