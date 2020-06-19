from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from ..models import Facture, Produit, Fournisseur, Categorie
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
from django.db.models import Avg, Sum, ExpressionWrapper, F, FloatField
from bootstrap_datepicker_plus import DatePickerInput


class ProduitTable(tables.Table):
    action = '<a href="{% url "update_produit" pk=record.id %}" class="btn btn-warning">Modifier</a>\
                <a href="{% url "delete_produit" pk=record.id %}" class="btn btn-danger">Supprimer</a>'
    edit = tables.TemplateColumn(action)

    class Meta:
        model = Produit
        template_name = "django_tables2/bootstrap4.html"
        fields = ('designation', 'prix', 'categorie', 'fournisseur', 'vendu')


class ProduitList(ListView):
    template_name = "bill/list.html"
    model = Produit

    def get_context_data(self, **kwargs):
        # Nous récupérons le contexte depuis la super-classe
        context = super(ProduitList, self).get_context_data(**kwargs)

        table = ProduitTable(Produit.objects.annotate(vendu=Sum('lignes_produit__qte')))

        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        context['btn_end_txt'] = ' Ajouter Un nouveau Produit'
        context['the_url'] = '/add_produit'
        context['titre'] = "Tout les Produit "
        return context


class ProduitAdd(CreateView):
    model = Produit
    template_name = 'bill/create.html'
    fields = ['designation', 'prix', 'categorie', 'fournisseur']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit', 'Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('all_produits')
        return form


class ProduitUpdate(UpdateView):
    model = Produit
    template_name = 'bill/update.html'
    fields = ('designation', 'prix', 'categorie', 'fournisseur')
    extra_context = {'titre': 'Produit'}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit', 'Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('all_produits')
        return form


def ProduitDelete(request, pk):
    obj = get_object_or_404(Produit, pk=pk)
    context = {'object': obj.__str__()}
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect("/all_produits")
    return render(request, "bill/delete.html", context)


# categories views

class CategorieTable(tables.Table):
    action = '<a href="{% url "delete_categorie" pk=record.designation %}" class="btn btn-danger">Supprimer</a>'
    edit = tables.TemplateColumn(action)

    class Meta:
        model = Categorie
        template_name = "django_tables2/bootstrap4.html"
        fields = ('designation', )


class CategorieList(ListView):
    template_name = "bill/list.html"
    model = Categorie

    def get_context_data(self, **kwargs):
        # Nous récupérons le contexte depuis la super-classe
        context = super(CategorieList, self).get_context_data(**kwargs)

        table = CategorieTable(Categorie.objects.all())

        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        context['btn_end_txt'] = ' Ajouter Une nouvelle catégorie'
        context['the_url'] = '/add_categorie'
        context['titre'] = "Tout les catégories "
        return context


def CategorieDelete(request, pk):
    obj = get_object_or_404(Categorie, pk=pk)
    context = {'object': obj.__str__()}
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect("/all_categories")
    return render(request, "bill/delete.html", context)


class CategorieADD(CreateView):
    model = Categorie
    template_name = 'bill/create.html'
    fields = ['designation']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit', 'Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('all_categories')
        return form
