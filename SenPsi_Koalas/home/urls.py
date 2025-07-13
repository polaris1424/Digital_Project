from django.urls import path
from django.shortcuts import redirect
from . import views

from . import views

urlpatterns = [
    path('call_duration_time/<int:id>', views.get_call_duration_time, name='call_duration_time'),
    path('call_counts_time/<int:id>', views.get_call_counts_time, name='call_counts_time'),
    path('call_duration_trace/<int:id>', views.get_call_duration_trace, name='call_duration_trace'),
    path('call_counts_trace/<int:id>', views.get_call_counts_trace, name='call_counts_trace'),
    path('sms_counts_time/<int:id>', views.get_sms_counts_time, name='sms_counts_time'),
    path('sms_counts_trace/<int:id>', views.get_sms_counts_trace, name='sms_counts_trace'),

    path('clinician/<int:clinician_id>/get_all_clients', views.get_all_clients, name='get_all_clients'),
    path('get_client_by_id/<int:client_id>', views.get_client_by_id, name='get_client_by_id'),
    path('get_client_by_name/<int:clinician_id>/<str:client_name>', views.get_client_by_name, name='get_client_by_name'),
    path('add_client/<int:clinician_id>', views.add_client, name='add_client'),
    path('update_client/<int:client_id>', views.update_client, name='update_client'),
    path('delete_client/<int:client_id>', views.delete_client, name='delete_client'),


    path('', lambda request: redirect('/login', permanent=False)),
    path('login', views.view_login, name='view_login'),
    path('logout', views.view_logout, name='view_logout'),

    path('homePage', views.homePage, name='homePage'),
    path('viewClient', views.viewClient, name='viewClient'),
    path('addClient', views.addClient, name='addClient'),

    path('dataAnalysis', views.dataAnalysis, name='dataAnalysis'),
    path('dataAnalysis/call_data', views.call_data, name='call_data'),
    path('dataAnalysis/sms_data', views.sms_data, name='sms_data')
]
