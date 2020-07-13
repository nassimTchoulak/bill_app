from django.contrib.auth.models import User
from django.middleware.csrf import *
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, SingleTableMixin
import django_filters
from ..models import Facture, LigneFacture, Fournisseur, Client, Categorie, Produit, Commande, LigneCommande
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
import django_tables2 as tables
from django_tables2.config import RequestConfig
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Button, Div
from django.urls import reverse, reverse_lazy
from django.db.models import Avg, Sum, ExpressionWrapper, F, FloatField, Max
from bootstrap_datepicker_plus import DatePickerInput


class FournisseurTable(tables.Table):
    class Meta:
        model = Fournisseur
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nom', 'chiffre_affaire')


class ClientTable(tables.Table):
    class Meta:
        model = Client
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nom', 'prenom', 'tel', 'adresse', 'chiffre_affaire')


class Main(MultiTableMixin, TemplateView):
    template_name = "bill/main.html"

    ls_line_date = []
    ls_line_value = []
    ls = []
    ls_pie = []
    total = 0

    for i in Facture.objects.values('date').annotate(chiffre_affaire=Sum(
            ExpressionWrapper(F('lignes_facture__qte'), output_field=FloatField())
            * F('lignes_facture__produit__prix'))).order_by('date'):
        if i['chiffre_affaire'] is not None:
            ls.append({'date': i['date'].strftime("%d %b %Y "), 'chiffre': i['chiffre_affaire']})
            ls_line_date.append(i['date'].strftime("%d %b %Y "))
            ls_line_value.append(i['chiffre_affaire'])
            total += i['chiffre_affaire']

    for i in Categorie.objects.values('designation').annotate(total=Sum(
            ExpressionWrapper(F('categorie_produit__lignes_produit__qte'), output_field=FloatField())
            * F('categorie_produit__prix'))):
        if i['total'] is not None:
            ls_pie.append({'name': i['designation'], 'y': i['total'] / total})

    print(ls_pie.__str__())

    tables = [
        FournisseurTable(Fournisseur.objects.annotate(chiffre_affaire=Sum(
            ExpressionWrapper(F('fournisseur_produit__lignes_produit__qte'), output_field=FloatField())
            * F('fournisseur_produit__prix'))).order_by('-chiffre_affaire')),

        ClientTable(Client.objects.annotate(chiffre_affaire=Sum(
            ExpressionWrapper(F('facture_client__lignes_facture__qte'), output_field=FloatField())
            * F('facture_client__lignes_facture__produit__prix'))).filter(chiffre_affaire__isnull=False).order_by(
            '-chiffre_affaire'))
    ]

    table_pagination = {
        "per_page": 30
    }

    print(ls_line_date.__str__())
    extra_context = {
        'l1': ls.__str__(),
        'ls_line_date': ls_line_date.__str__(),
        'ls_line_value': ls_line_value.__str__(),
        'ls_pie': ls_pie.__str__()

    }


class ProduitClientTable(tables.Table):
    action = '{% if record.produit_image %}' + \
             ' <img width="200px" class="img-fluid" src="{{ record.produit_image.url }}" />' + \
             '{% endif %}'

    action_add = '<form  action = "{% url "panier_manager" action="1" pk=record.id %}" method="POST">  {% csrf_token %} <input class="btn btn-info" type="submit"  value= "Ajouter produit au panier" /> </form>'
    imagelink = tables.TemplateColumn(action)

    ajouter = tables.TemplateColumn(action_add)

    class Meta:
        model = Produit
        template_name = "django_tables2/bootstrap4.html"
        fields = ('id','designation', 'categorie', 'prix')


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Produit
        fields = ['designation', 'categorie', 'prix']


class FilteredPersonListView(SingleTableMixin, FilterView):
    model = Produit
    template_name = "bill/list_client.html"
    filterset_class = ProductFilter

    extra_context = {
        'titre': 'Ajoutez un produit a votre panier '
    }

    table_class = ProduitClientTable


class PanierTable(tables.Table):
    # action = '<a href="{% url "facture_table_detail" pk=record.id %}" class="btn btn-info">augmenter quantité</a>'

    action = '<form  action = "{% url "panier_manager" action="2" pk=record.produit_id %}" method="POST">  {% csrf_token %} <input class="btn btn-info" type="submit"  value= "augmenter quantité" /> </form>'
    action_add = '<form  action = "{% url "panier_manager" action="3" pk=record.produit_id %}" method="POST">  {% csrf_token %} <input class="btn btn-danger" type="submit"  value= "Supprimer" /> </form>'

    Ajouter_quantité = tables.TemplateColumn(action)
    Supprimer_ligne = tables.TemplateColumn(action_add)

    class Meta:
        model = LigneCommande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit_id', 'produit__categorie', 'produit', 'qte')


class Pannier(SingleTableMixin, FilterView):
    model = LigneCommande
    template_name = "bill/list_client.html"

    # queryset = LigneCommande.objects.filter(commande__user=request.user)

    def get_table_data(self):
        return LigneCommande.objects.filter(commande__user=self.request.user,commande__termine=False)

    extra_context = {
        'titre': ' Mon panier de produits ',
        'filter': False,
        'the_end':True
    }

    table_class = PanierTable


def Panier_manager(request, action, pk):
    get_token(request)
    if action == "1":
        print("__________")
        panier = Commande.objects.filter(user=request.user, termine=False)
        if len(panier) > 0:
            LigneCommande.objects.create(commande=panier.first(), qte=1, produit_id=pk).save()
        else:
            panier = Commande.objects.create(user=request.user, termine=False)
            panier.save()
            LigneCommande.objects.create(commande=panier, qte=1, produit_id=pk).save()

    elif action == "2":

        t = LigneCommande.objects.filter(commande__user_id=request.user.id, produit_id=pk).first()
        t.qte += 1
        t.save()
    elif action == "3":
        t = LigneCommande.objects.filter(commande__user_id=request.user.id, produit_id=pk).first()
        t.delete()

    else:
        client = Client.objects.filter(nom=request.user.last_name, prenom=request.user.first_name)
        if len(client) > 0:
            cli = client.first()
        else :
            cli = Client(nom=request.user.last_name, prenom=request.user.first_name,sexe='M',adresse=request.user.email)
            cli.save()
        panier = Commande.objects.filter(user=request.user, termine=False).first()
        panier.termine = True
        panier.client = cli
        panier.save()
        return HttpResponseRedirect("/my_commandes")



    return HttpResponseRedirect("/panier")




class MyCommandes(MultiTableMixin, TemplateView):
    pass


class CommandeClientTable(tables.Table):
    action = '{% if record.facture %} <a href="{% url "update_produit" pk=record.id %}" class="btn btn-info">Modifier</a> {% endif %}'

    detail_facture = tables.TemplateColumn(action)

    class Meta:
        model = Commande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('client','date','termine','facture','montant')


class MyCommandes(ListView):
    template_name = "bill/list_client.html"
    model = Commande

    def get_context_data(self, **kwargs):
        # Nous récupérons le contexte depuis la super-classe
        context = super(MyCommandes, self).get_context_data(**kwargs)

        table = CommandeClientTable(Commande.objects.annotate(montant=Sum(
            ExpressionWrapper(F('lignes_commande__qte'), output_field=FloatField())
            * F('lignes_commande__produit__prix'))))

        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table

        context['titre'] = "Tout Mes Commande validé & en attente  "
        return context