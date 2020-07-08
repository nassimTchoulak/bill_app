from django.conf.urls.static import static
from django.urls import path, re_path, include

from bill import settings
from bill.all_views.clientviews import *
from bill.all_views.ligne_facture_views import *
from bill.all_views.factureviews import *
from bill.all_views.fournisseurviews import *
from bill.all_views.mainview import *
from bill.all_views.produitviews import *
from django.contrib import admin

urlpatterns = [

    path('admin/', admin.site.urls),
    re_path(r'^facture_detail/(?P<pk>\d+)/$', facture_detail_view, name='facture_detail'),
    re_path(r'^facture_table_detail/(?P<pk>\d+)/$', FactureDetailView.as_view(), name='facture_table_detail'),
    re_path(r'^facture_table_create/(?P<facture_pk>\d+)/$', LigneFactureCreateView.as_view(),
            name='facture_table_create'),
    re_path(r'^lignefacture_delete/(?P<pk>\d+)/(?P<facture_pk>\d+)/$', LigneFactureDeleteView.as_view(),
            name='lignefacture_delete'),
    re_path(r'^lignefacture_update/(?P<pk>\d+)/(?P<facture_pk>\d+)/$', LigneFactureUpdateView.as_view(),
            name='lignefacture_update'),

    re_path(r'^all_clients/$', AllClients.as_view(), name='all_clients'),
    re_path(r'^client_detail/(?P<pk>\d+)/$', AllFacturesClient.as_view(), name='client_detail'),
    re_path(r'^add_client/$', AddClient.as_view(), name='new_client'),
    re_path(r'^update_client/(?P<pk>\d+)/$', ClientUpdate.as_view(), name='update_client'),
    re_path(r'^delete_client/(?P<pk>\d+)/$', ClientDelete, name='delete_client'),
    re_path(r'^add_facture/(?P<pk>\d+)/$', AddFactureClient.as_view(), name='add_facture_client'),
    re_path(r'^delete_facture/(?P<pk>\d+)/$', deleteFacture, name='delete_facture'),
    re_path(r'^update_facture/(?P<pk>\d+)/$', FactureUpdate.as_view(), name='update_facture'),

    re_path(r'^all_fournisseurs/$', FournisseurList.as_view(), name='all_fournisseurs'),
    re_path(r'^add_fournisseur/$', FournisseurADD.as_view(), name='add_fournisseur'),
    re_path(r'^update_fournisseur/(?P<pk>\d+)/$', FournisseurUpdate.as_view(), name='update_fournisseur'),
    re_path(r'^delete_fournisseur/(?P<pk>\d+)/$', FournisseurDelete, name='delete_fournisseur'),

    re_path(r'^all_produits/$', ProduitList.as_view(), name='all_produits'),
    re_path(r'^add_produit/$', ProduitAdd.as_view(), name='add_produit'),
    re_path(r'^update_produit/(?P<pk>\d+)/$', ProduitUpdate.as_view(), name='update_produit'),
    re_path(r'^delete_produit/(?P<pk>\d+)/$', ProduitDelete, name='delete_produit'),

    re_path(r'^all_categories/$', CategorieList.as_view(), name='all_categories'),
    re_path(r'^add_categorie/$', CategorieADD.as_view(), name='add_produit'),
    re_path(r'^delete_categorie/(?P<pk>\w+)/$', CategorieDelete, name='delete_categorie'),

    path('', Main.as_view(), name='main_tab')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
