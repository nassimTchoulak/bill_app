from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django_tables2 import MultiTableMixin

from ..models import Facture, LigneFacture, Fournisseur, Client, Categorie
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
