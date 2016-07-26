#coding:utf8

_author__ = 'eric'


from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField, IntegerField, DateTimeField, FileField, SelectMultipleField
from wtforms.validators import Email, Length, Regexp, EqualTo, InputRequired, IPAddress, HostnameValidation, MacAddress, NumberRange
from ..models import *
from .. import db
from wtforms import ValidationError


class EditProfileForm(Form):
    username = StringField('Username', validators=[InputRequired(), Length(0,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must have only letters, number, dots or underscores')])
    name = StringField(u'真实姓名', validators=[InputRequired(), Length(0,64)])
    position = StringField(u'工作职位', validators=[InputRequired(), Length(0,64)])
    qq = StringField(u'QQ号码')
    phone = StringField(u'手机号码')
    location = StringField(u'位置', validators=[Length(0,64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')


class EditProfileAdminForm(Form):
    email = StringField('Email',validators=[InputRequired(), Length(1,64), Email()])
    username = StringField('Username', validators=[InputRequired(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must have only letters, number, dots or underscores')])
    confirmed = BooleanField(u'confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real Name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
                raise ValidationError('Username already registered')


class EditDeviceForm(Form):
    deviceType = SelectField(u'设备类型', coerce=int)   # 资产类别   关联ClassType table
    onstatus = SelectField(u'使用状态', coerce=int)                        # 使用状态
    usedept = StringField(u'使用部门', validators=[Length(1,64)])                       # 使用部门
    usestaff = StringField(u'部门使用人', validators=[Length(1,64)])                     # 部门使用人
    mainuses = StringField(u'主要用途', validators=[Length(1,128)])                    # 主要用途
    managedept = StringField(u'管理部门', validators=[Length(1,64)])                   # 管理部门
    managestaff = StringField(u'管理人', validators=[Length(1,64)])                  # 管理人
    device_id = SelectField(u'运行主机', coerce=int)
    pool = SelectField(u'资源池', coerce=int)
    hostname = StringField(u'主机名', validators=[HostnameValidation, Length(0,64)])
    os = StringField(u'操作系统')
    cpumodel = StringField(u'CPU型号', validators=[Length(0,64)])                     # CPU 型号
    cpucount = IntegerField(u'CPU内核(个)')                        # CPU 核数
    memsize = IntegerField(u'内存大小(GB)')                      # 内存容量
    disksize = IntegerField(u'磁盘大小(GB)')                        # 磁盘容量
    business = SelectField(u'所属业务', coerce=int)
    powerstatus = SelectField(u'电源状态', coerce=int)
    remarks = TextAreaField(u'备注')                          # 备注
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(EditDeviceForm, self).__init__(*args, **kwargs)

        self.deviceType.choices = [(1, u'OpenStack'), (2, u'VMware')]

        self.onstatus.choices = [(1, u'已用'), (2, u'空闲'), (3, u'下线'), (3, u'待回收')]

        self.device_id.choices = [(device.id, device.hostname)
                             for device in Device.query.order_by(Device.hostname).all()]

        self.pool.choices = [(pool.id, pool.name)
                             for pool in DevicePools.query.order_by(DevicePools.name).all()]

        self.business.choices = [(1, u'云计算',),(2, u'大数据')]

        self.powerstatus.choices = [(1, u'开机'), (2, u'关机')]



class EditDevicePowerForm(Form):
    type = SelectField(u'电源模块类型', coerce=int)                      # 网络类型
    enabled = BooleanField(u'启用电源管理')
    ip = StringField(u'IP地址', validators=[Length(0,15)])                 # 远控卡IP地址
    user = StringField(u'用户', validators=[Length(0,64)])
    password = PasswordField(u'密码', validators=[InputRequired(), EqualTo('password2', message=u'密码不匹配')])
    password2 = PasswordField(u'确认密码', validators=[InputRequired()])
    powerid = StringField(u'设备ID', validators=[Length(0,64)])          # 缃戝崱绔彛鏁伴噺
    remarks = TextAreaField(u'备注')                          # 备注
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(EditDevicePowerForm, self).__init__(*args, **kwargs)

        self.type.choices = [(1, u'IPMI'), (1, u'iLO')]

#    def validate_powermanage_ip(self, field):
#        if DevicePowerManage.query.filter_by(powermanage_ip=field.data).first():
#            raise ValidationError(u'远控卡IP: {0}已经用了'.format(field.data))


class EditDeviceTaskForm(Form):
    taskname = StringField(u'任务名称', validators=[InputRequired()])
    scriptfile = FileField(u'脚本名称', validators=[InputRequired()])
    scriptname = StringField(u'脚本名称')
    type = SelectField(u'脚本类型', coerce=int)
    arch = SelectField(u'系统架构', coerce=int)
    path = StringField(u'文件路径')
    version = StringField(u'版本')
    enabled = BooleanField(u'启用')
    remarks = TextAreaField(u'备注')  # 备注
    instaff = StringField(u'上传者')
    submit = SubmitField(u'提交')


    def __init__(self, *args, **kwargs):
        super(EditDeviceTaskForm, self).__init__(*args, **kwargs)

        self.type.choices = [(1, u'Shell'), (2, u'Playbook'), (3, u'Python'), (4, u'Perl')]
        self.arch.choices = [(1, u'RHEL6'), (2, u'RHEL7'), (3, u'AIX5'), (4, u'AIX6'), (5, u'Ubuntu')]


    def validate_name(self, field):
        if DeviceTasks.query.filter_by(name=field.data).first():
            raise ValidationError(u'任务名称{0}已经存在.'.format(field.data))


    def validate_script(self, field):
        if not field.data:
            raise ValidationError(u'请确认上传文件是否正确.'.format(field.data))


class EditDeviceTaskGroupForm(Form):
    name = StringField(u'任务组名称', validators=[InputRequired()])
    tasks = SelectMultipleField(u'任务脚本', coerce=int)
    enabled = BooleanField(u'启用')
    remarks = TextAreaField(u'备注')  # 备注
    submit = SubmitField(u'提交')

    def __init__(self, deviceTaskGroup, *args, **kwargs):
        super(EditDeviceTaskGroupForm, self).__init__(*args, **kwargs)
        self.deviceTaskGroup = deviceTaskGroup
        self.tasks.choices = [ (task.id, task.taskname)
                              for task in DeviceTasks.query.all()]

    def validate_name(self,field):
        if not self.deviceTaskGroup:
            if DeviceTaskGroup.query.filter_by(name=field.data).first():
                raise ValidationError(u'任务组名称{0}已经存在.'.format(field.data))
        else:
            if field.data != self.deviceTaskGroup.name and DeviceTaskGroup.query.filter_by(name=field.data).first():
                raise ValidationError(u'任务组名称{0}已经存在.'.format(field.data))