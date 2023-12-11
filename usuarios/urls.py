"""
URL configuration for usuarios project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from login import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.iniciar, name='iniciar'),
    path('registro/',views.registro, name='registro'),
    path('home/',views.home, name='home'),
    path('listado/',views.listado, name='listado'),
    path('home/guardar',views.guardar, name='guardar'),
    path('listado/detalle/<int:id>', views.detalle, name='detalle'),
    path('salir/',views.salir, name='salir'),
    path('listado/editar',views.editar, name='editar'),
    path('listado/eliminar/<int:id>',views.eliminar,name='eliminar'),
    path('inicio/',views.inicio,name='inicio'),
    path('verificar_rut/', views.verificar_rut, name='verificar_rut'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
