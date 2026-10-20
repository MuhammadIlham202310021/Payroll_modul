from django.urls import path
from . import views 

app_name = 'pekerja'

urlpatterns = [
    path('', views.home, name='home'),
    path('kebun/', views.kebun, name='kebun'),
    
    path('pekerja/', views.pekerja_list, name='list'),
    path('pekerja/tambah/', views.pekerja_create, name='create'),
    path('pekerja/<int:pk>/edit/', views.pekerja_update, name='update'),
    path('pekerja/<int:pk>/hapus/', views.pekerja_delete, name='delete'),
    
    path('department/', views.department_list, name='department_list'),
    path('department/tambah/', views.department_create, name='department_create'),
    path('department/<int:pk>/edit/', views.department_update, name='department_update'),
    path('department/<int:pk>/hapus/', views.department_delete, name='department_delete'),
    
    path('division/', views.division_list, name='division_list'),
    path('division/tambah/', views.division_create, name='division_create'),
    path('division/<int:pk>/edit/', views.division_update, name='division_update'),
    path('division/<int:pk>/hapus/', views.division_delete, name='division_delete'),

    path('api/division/', views.division_by_department, name='division_by_department'),
    
    path('report/', views.report_biodata, name='report'),
    path('report/excel/', views.report_excel, name='report_excel'),
    path('report/pdf/', views.report_pdf, name='report_pdf'),
    
    path('jabatan/', views.jabatan_list, name='jabatan_list'),
    path('jabatan/tambah/', views.jabatan_create, name='jabatan_create'),
    path('jabatan/<int:pk>/edit/', views.jabatan_update, name='jabatan_update'),
    path('jabatan/<int:pk>/hapus/', views.jabatan_delete, name='jabatan_delete'),
    
]