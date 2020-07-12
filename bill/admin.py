from django.contrib import admin
from .models import Client, Produit, Facture, LigneFacture, Fournisseur

# Register your models here.
admin.site.register(Client)
admin.site.register(Facture)
admin.site.register(Produit)
admin.site.register(LigneFacture)
admin.site.register(Fournisseur)