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

    def __str__(self):
        return self.designation


class Produit(models.Model):
    designation = models.CharField(max_length=50)
    prix = models.FloatField(default=0)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, default=None,
                                  related_name='categorie_produit')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True,
                                    related_name='fournisseur_produit')
    produit_image = models.ImageField(upload_to='./', default=None, null=True)

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


class Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(default=utils.timezone.now)
    termine = models.BooleanField(default=False)
    # false means commmande== panier !! sinon une commande terminé # validable par admin
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, default=None, null=True,
                                related_name="commande_facture")


class LigneCommande(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    qte = models.IntegerField(default=1)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes_commande')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['produit', 'commande'], name="produit-commande")
        ]
