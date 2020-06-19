from django.db import models
from django import utils
import datetime


# Create your models here.

class Client(models.Model):
    SEXE = (
        ('M', 'Masculin'),
        ('F', 'Feminin')
    )
    nom = models.CharField(max_length=50, null=True, blank=True)
    prenom = models.CharField(max_length=50, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    tel = models.CharField(max_length=10, null=True, blank=True)
    sexe = models.CharField(max_length=1, choices=SEXE)

    def __str__(self):
        return self.nom + ' ' + self.prenom


class Fournisseur(models.Model):
    nom = models.CharField(default="", null=True, max_length=50)

    def __str__(self):
        return self.nom


class Categorie(models.Model):
    designation = models.CharField(max_length=50, primary_key=True)


class Produit(models.Model):
    designation = models.CharField(max_length=50)
    prix = models.FloatField(default=0)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL,null=True,default=None,
                                  related_name='categorie_produit')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True,
                                    related_name='fournisseur_produit')

    def __str__(self):
        return self.designation


class Facture(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='facture_client')
    date = models.DateField(default=utils.timezone.now)

    def total(self):
        ls = LigneFacture.objects.filter(facture=self)
        total = 0.0
        for lig in ls:
            total += lig.qte * lig.produit.prix
        return total

    def detail_facture(self):
        return LigneFacture.objects.filter(facture=self)


class LigneFacture(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='lignes_produit')
    qte = models.IntegerField(default=1)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes_facture')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['produit', 'facture'], name="produit_facture")
        ]
