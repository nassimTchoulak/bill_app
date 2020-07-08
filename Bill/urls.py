from django.urls import  path, re_path, include
from bill import views

urlpatterns = [
    re_path(r'^facture_detail/(?P<pk>\d+)/$', views.facture_detail_view, name='facture_detail'),
    re_path(r'^facture_table_detail/(?P<pk>\d+)/$', views.FactureDetailView.as_view(), name='facture_table_detail'),
    re_path(r'^facture_table_create/(?P<facture_pk>\d+)/$', views.LigneFactureCreateView.as_view(), name='facture_table_create'),
    re_path(r'^lignefacture_delete/(?P<pk>\d+)/(?P<facture_pk>\d+)/$', views.LigneFactureDeleteView.as_view(), name='lignefacture_delete'),
    re_path(r'^lignefacture_update/(?P<pk>\d+)/(?P<facture_pk>\d+)/$', views.LigneFactureUpdateView.as_view(), name='lignefacture_update'),
    re_path(r'^facture_update/(?P<pk>\d+)/$', views.FactureUpdate.as_view(), name='facture_update'),
]