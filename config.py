__author__ = 'eric'


import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = 'fdsakjfdoufweonflka'

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    FLASK_MAIL_SUBJECT_PREFIX = '[CMDB]'
    FLASK_MAIL_SENDER = 'CMDB Admin <kefatong@163.com>'
    FLASK_ADMIN = 'Eric.Ke@hpe-project.com'

    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:123456@localhost/ops?charset=utf8'
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    FLASK_POSTS_PER_PAGE = 30
    FLASK_FOLLOWERS_PER_PAGE = 20

    FLASK_USE_CMDB_API = 'http://localhost:5000/api/v1.0'
    FLASK_USE_CMDB_USER = 'kefatong@qq.com'
    FLASK_USE_CMDB_PASSWORD = '123456'

    FLASK_UPLOAD_HOME = './upload'
    FLASK_TMP_HOME = './tmp'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:123456@localhost/ServerAutomation?charset=utf8'


class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.test.sqlite')

config = {
    'development': DevelopmentConfig,
    'production' : ProductionConfig,
    'testing'    : TestingConfig,
    'default'    : DevelopmentConfig,
}


