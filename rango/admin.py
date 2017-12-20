# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Project,Module,Api,Case,Report,DbConfigure


admin.site.register(Project)
admin.site.register(Module)
admin.site.register(Api)
admin.site.register(Case)
admin.site.register(Report)
admin.site.register(DbConfigure)