#coding:utf8

__author__ = 'eric'

from flask import Blueprint
main = Blueprint('main',__name__)
from . import views, errors
from ..import db
from ..models import *
from ..models import Permission


@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)

