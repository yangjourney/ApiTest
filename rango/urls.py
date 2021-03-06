from django.conf.urls import url
from rango import views
from django.contrib.auth.views import login, logout


urlpatterns = [
    url(r'^auth',views.sign_in),
    url(r'^login',login),
    url(r'^logout',logout),
    url(r'^statistic',views.projects_statistic),
    url(r'^projects',views.projects_view),
    url(r'^reports',views.reports_view),
    url(r'^about',views.about_view),
    url(r'^project/create',views.project_create_view),
    url(r'^project/save',views.project_save),
    url(r'^project/edit',views.project_edit_view),
    url(r'^project/update',views.project_update),
    url(r'^project/active',views.project_active),
    url(r'^project/inactive',views.project_inactive),
    url(r'^project/setting_save',views.project_set),
    url(r'^project/setting',views.project_setting_view),
    url(r'^project_report',views.project_report),
    url(r'^module/create',views.module_create_view),
    url(r'^module/save',views.module_save),
    url(r'^api/create',views.api_create_view),
    url(r'^api/save',views.api_save),
    url(r'^project',views.project_view),
    url(r'^apis',views.apis_view),
    url(r'^api/edit',views.api_edit_view),
    url(r'^api/report',views.api_report_view),
    url(r'^all/report',views.all_report_view),
    url(r'^api/update',views.api_update),
    url(r'^cases/test',views.multi_case_test),
    url(r'^cases',views.cases_view),
    url(r'^case/create',views.case_create_view),
    url(r'^case/edit',views.case_edit_view),
    url(r'^case/update',views.case_update),
    url(r'^case/save',views.case_save),
    url(r'^module/active',views.module_active),
    url(r'^module/inactive',views.module_inactive),
    url(r'^api/active',views.api_active),
    url(r'^api/inactive',views.api_inactive),
    url(r'^case/active',views.case_active),
    url(r'^case/inactive',views.case_inactive),
    url(r'^case/report',views.case_report_view),
    url(r'^case/test',views.case_test),
    url(r'^all/test',views.all_test),
    url(r'',views.home),
]