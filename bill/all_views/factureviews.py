from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .ligne_facture_views import LigneFactureTable
from ..models import Facture, LigneFacture, Client, Commande, LigneCommande
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


class FactureUpdate(UpdateView):
    model = Facture
    fields = ['client', 'date']
    template_name = 'bill/update.html'
    extra_context = {'titre': 'facture'}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        f = Facture.objects.get(id=self.kwargs.get('pk'))
        form.fields['client'] = forms.ModelChoiceField(queryset=Client.objects.filter(id=f.client.id),
                                                       initial=0)

        form.fields['date'] = forms.DateField(
            widget=DatePickerInput(format='%m/%d/%Y')
        )
        form.helper.add_input(Submit('submit', 'Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('client_detail', kwargs={'pk': f.client.id})
        return form


class FactureTable(tables.Table):
    action = '<a href="{% url "update_facture" pk=record.id %}" class="btn btn-warning">Modifier</a>\
                <a href="{% url "delete_facture" pk=record.id %}" class="btn btn-danger">Supprimer</a>\
                <a href="{% url "facture_table_detail" pk=record.id %}" class="btn btn-info">Les items</a>'
    edit = tables.TemplateColumn(action)

    class Meta:
        model = Client
        template_name = "django_tables2/bootstrap4.html"
        fields = ('id', 'date', 'total')


class AllFacturesClient(ListView):
    template_name = "bill/list.html"
    model = Facture

    def get_context_data(self, **kwargs):
        context = super(AllFacturesClient, self).get_context_data(**kwargs)

        table = FactureTable(Facture.objects.annotate(total=Sum(
            ExpressionWrapper(F('lignes_facture__qte'), output_field=FloatField())
            * F('lignes_facture__produit__prix'))).filter(client_id=self.kwargs.get('pk'))
                             )

        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
        context['table'] = table
        context['btn_end_txt'] = ' Ajouter une Nouvelle Facture '
        context['the_url'] = '/add_facture/' + self.kwargs.get('pk')
        context['titre'] = "Tout les Facture du client " + Client.objects.get(id=self.kwargs.get('pk')).nom
        return context


class AddFactureClient(CreateView):
    model = Facture
    template_name = 'bill/create.html'
    fields = ('date', 'client')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.fields['client'] = forms.ModelChoiceField(queryset=Client.objects.filter(id=self.kwargs.get('pk')),
                                                       initial=0)

        form.fields['date'] = forms.DateField(
            widget=DatePickerInput(format='%m/%d/%Y')
        )
        form.helper.add_input(Submit('submit', 'Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('client_detail', kwargs={'pk': self.kwargs.get('pk')})
        return form


def deleteFacture(request, pk):
    obj = get_object_or_404(Facture, pk=pk)
    context = {'object': obj.__str__()}
    if request.method == "POST":
        user_id = obj.client.id
        obj.delete()
        return HttpResponseRedirect("/client_detail/" + user_id.__str__())
    return render(request, "bill/delete.html", context)


class CommandeAdmin(tables.Table):
    action = '{% if record.facture %} <a href="{% url "facture_table_detail" pk=record.facture_id %}" class="btn btn-info">detail facture</a> {% else %}'+\
        '<form  action = "{% url "commande_op"  pk=record.id %}" method="POST">  {% csrf_token %} <input class="btn btn-warning" type="submit"  value= "Valider Commande" /> </form> {% endif %}'

    edit = tables.TemplateColumn(action)

    class Meta:
        model = Commande
        template_name = "django_tables2/bootstrap4.html"
        fields = ('id','client', 'date', 'termine', 'facture','facture_id', 'montant')


class CommandeAdminView(ListView):
    template_name = "bill/list.html"
    model = Commande

    def get_context_data(self, **kwargs):
        context = super(CommandeAdminView, self).get_context_data(**kwargs)

        table = CommandeAdmin(Commande.objects.annotate(montant=Sum(
            ExpressionWrapper(F('lignes_commande__qte'), output_field=FloatField())
            * F('lignes_commande__produit__prix'))).filter(termine=True))

        RequestConfig(self.request, paginate={"per_page": 30}).configure(table)
        context['table'] = table

        context['titre'] = "Tout les Commandes des clients à valider "
        return context


def Commande_op(request, pk):

    commande = Commande.objects.get(pk=pk)

    f = Facture(client=commande.client,date=commande.date)
    f.save()

    for i in LigneCommande.objects.filter(commande_id=pk):
        y = LigneFacture(facture=f,qte=i.qte,produit=i.produit)
        y.save()
    commande.facture = f
    commande.save()

    return HttpResponseRedirect("/")
