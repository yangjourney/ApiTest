from __future__ import unicode_literals
# Create your models here.
# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.utils.translation import ugettext_lazy as _


class Project(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField()
    created_user = models.ForeignKey(User)
    created_time = models.DateTimeField(help_text=_('created date'),auto_now_add=True)
    updated_time = models.DateTimeField(help_text=_('updated date'), auto_now=True)
    def _unicode_(self):
        return self.name

class Module(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=255)
    status = models.BooleanField()
    created_user = models.ForeignKey(User)
    created_time = models.DateTimeField(help_text=_('created date'),
                                        auto_now_add = True)
    updated_time = models.DateTimeField(help_text=_('updated date'), auto_now =
    True)
    def _unicode_(self):
        return self.name

class Api(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    headers = models.TextField()
    module = models.ForeignKey(Module)
    status = models.BooleanField()
    created_user = models.ForeignKey(User)
    created_time = models.DateTimeField(help_text=_('created date'),auto_now_add = True)
    updated_time = models.DateTimeField(help_text=_('updated date'),auto_now = True)
    def _unicode_(self):
        return self.name

class Case(models.Model):
    api = models.ForeignKey(Api)
    body = models.TextField()
    check_sql = models.TextField()
    expected_status = models.IntegerField()
    expected = models.TextField()
    status = models.BooleanField()
    created_user = models.ForeignKey(User)
    created_time = models.DateTimeField(help_text=_('created date'), auto_now_add = True)
    updated_time = models.DateTimeField(help_text=_('updated date'), auto_now = True)
    def _unicode_(self):
        return self.name

class Report(models.Model):
    case = models.ForeignKey(Case)
    content = models.TextField()
    detail = models.TextField()
    error = models.TextField()
    dbresult = models.TextField()
    created_user = models.ForeignKey(User)
    status = models.BooleanField()
    created_time = models.DateTimeField(help_text=_('created date'), auto_now_add = True)
    def _unicode_(self):
        return self.content

class DbConfigure(models.Model):
    project = models.ForeignKey(Project)
    address = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    dbname = models.CharField(max_length=255)
    port = models.IntegerField(blank=True, null=True)
    sql = models.FileField(upload_to = './upload/')
    def _unicode_(self):
        return self.address