__author__ = 'eric'


from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views

