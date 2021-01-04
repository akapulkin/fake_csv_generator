"""Fake_csv_generator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from schemas.views import login_page, SchemaListView, logout_user, SchemaCreateView,\
    schema_delete, SchemaDatasetListView


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', login_page, name='login'),
    path('schemas/', SchemaListView.as_view(), name='schemas'),
    path('logout/', logout_user, name='logout'),
    path('schema/create/', SchemaCreateView.as_view(), name='schema_create'),
    path('schema/delete/<int:pk>', schema_delete, name='schema_delete'),
    path('schema/datasets/<int:pk>', SchemaDatasetListView.as_view(), name='schema_datasets')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
