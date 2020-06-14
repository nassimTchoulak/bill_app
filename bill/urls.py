from django.urls import path, re_path, include
from bill import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^facture_detail/(?P<pk>\d+)/$', views.facture_detail_view, name='facture_detail')
]
