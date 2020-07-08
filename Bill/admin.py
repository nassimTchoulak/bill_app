from django.contrib import admin
from bill.models import Client, Produit, Facture, LigneFacture

# Register your models here.
admin.site.register(Client)
admin.site.register(Facture)
admin.site.register(Produit)
admin.site.register(LigneFacture)