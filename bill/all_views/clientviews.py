from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from ..models import Facture, LigneFacture, Client
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


class ClientTable(tables.Table):
    action = '<a href="{% url "update_client" pk=record.id %}" class="btn btn-warning">Modifier</a>\
                <a href="{% url "delete_client" pk=record.id %}" class="btn btn-danger">Supprimer</a>\
                <a href="{% url "client_detail" pk=record.id %}" class="btn btn-info">Les factures</a>'
    edit = tables.TemplateColumn(action)

    class Meta:
        model = Client
        template_name = "django_tables2/bootstrap4.html"
        fields = ('nom', 'prenom', 'adresse',
                  'tel', 'sexe', 'chiffre_affaire')


class AllClients(ListView):
    template_name = "bill/list.html"
    model = Client

    def get_context_data(self, **kwargs):
        context = super(AllClients, self).get_context_data(**kwargs)
        table = ClientTable(Client.objects.annotate(chiffre_affaire=Sum(
            ExpressionWrapper(F('facture_client__lignes_facture__qte'), output_field=FloatField())
            * F('facture_client__lignes_facture__produit__prix')))
        )
        RequestConfig(self.request, paginate={"per_page": 30}).configure(table)
        context['table'] = table
        context['btn_end_txt'] = ' Ajouter Un nouveau Client '
        context['the_url'] = '/add_client'
        context['titre'] = "Tout les Clients"
        return context


class AddClient(CreateView):
    model = Client
    template_name = 'bill/create.html'
    fields = ['nom', 'prenom', 'adresse', 'tel', 'sexe']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        # form.fields['facture'] = forms.ModelChoiceField(, initial=0)
        form.helper.add_input(Submit('submit', 'Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('all_clients')
        return form


class ClientUpdate(UpdateView):
    model = Client
    template_name = 'bill/update.html'
    fields = ('nom', 'prenom', 'adresse',
              'tel', 'sexe')
    extra_context = {'titre': 'client'}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.helper.add_input(Submit('submit', 'Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('all_clients')
        return form


def ClientDelete(request, pk):
    obj = get_object_or_404(Client, pk=pk)
    context = {'object': obj.__str__()}
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect("/all_clients")
    return render(request, "bill/delete.html", context)
