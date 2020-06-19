from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from ..models import Facture, LigneFacture, Fournisseur
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


class FournisseurTable(tables.Table):
    action = '<a href="{% url "update_fournisseur" pk=record.id %}" class="btn btn-warning">Modifier</a>\
                <a href="{% url "delete_fournisseur" pk=record.id %}" class="btn btn-danger">Supprimer</a>'
    edit = tables.TemplateColumn(action)

    class Meta:
        model = Fournisseur
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nom', 'chiffre_affaire')


class FournisseurList(ListView):
    template_name = "bill/list.html"
    model = Fournisseur

    def get_context_data(self, **kwargs):
        # Nous récupérons le contexte depuis la super-classe
        context = super(FournisseurList, self).get_context_data(**kwargs)

        table = FournisseurTable(Fournisseur.objects.annotate(chiffre_affaire=Sum(
            ExpressionWrapper(F('fournisseur_produit__lignes_produit__qte'), output_field=FloatField())
            * F('fournisseur_produit__prix')))
        )
        z= Fournisseur.objects.annotate(chiffre_affaire=Sum(
            ExpressionWrapper(F('fournisseur_produit__lignes_produit__qte'), output_field=FloatField())
            * F('fournisseur_produit__prix')))
        #table = FournisseurTable(Fournisseur.objects.filter(fournisseur_produit__lignes_produit__qte=1,fournisseur_produit__prix=))

        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        context['btn_end_txt'] = ' Ajouter Un nouveau fournisseur'
        context['the_url'] = '/add_fournisseur'
        context['titre'] = "Tout les fournissuers"
        return context


class FournisseurADD(CreateView):
    model = Fournisseur
    template_name = 'bill/create.html'
    fields = ['nom']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit', 'Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('all_fournisseurs')
        return form


class FournisseurUpdate(UpdateView):
    model = Fournisseur
    template_name = 'bill/update.html'
    fields = ('nom',)
    extra_context = {'titre': 'Fournisseur'}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit', 'Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('all_fournisseurs')
        return form


def FournisseurDelete(request, pk):
    obj = get_object_or_404(Fournisseur, pk=pk)
    context = {'object': obj.__str__()}
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect("/all_fournisseurs")
    return render(request, "bill/delete.html", context)
