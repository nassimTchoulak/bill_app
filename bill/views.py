from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Facture, LigneFacture, Client
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
from django.contrib.auth.decotators import login_required

# Create your all_views here.

@login_required
def facture_detail_view(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    total = facture.total()
    context = {'facture': facture, "total": total}
    print(context)
    return render(request, 'bill/facture_detail.html', context)


class FactureUpdate(UpdateView):
    model = Facture
    fields = ['client', 'date']
    template_name = 'bill/update.html'
    extra_context = {'titre': 'facture'}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()


        form.fields['date'] = forms.DateField(
            widget=DatePickerInput(format='%m/%d/%Y')
        )
        form.helper.add_input(Submit('submit', 'Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk': self.kwargs.get('facture_pk')})
        return form


class LigneFactureTable(tables.Table):
    action = '<a href="{% url "lignefacture_update" pk=record.id facture_pk=record.facture.id %}" class="btn btn-warning">Modifier</a>\
            <a href="{% url "lignefacture_delete" pk=record.id facture_pk=record.facture.id %}" class="btn btn-danger">Supprimer</a>'
    edit = tables.TemplateColumn(action)

    class Meta:
        model = LigneFacture
        template_name = "django_tables2/bootstrap4.html"
        fields = ('produit__designation', 'produit__id', 'produit__prix', 'qte')


class FactureDetailView(DetailView):
    template_name = 'bill/facture_table_detail.html'
    model = Facture

    def get_context_data(self, **kwargs):
        context = super(FactureDetailView, self).get_context_data(**kwargs)

        table = LigneFactureTable(LigneFacture.objects.filter(facture=self.kwargs.get('pk')))
        RequestConfig(self.request, paginate={"per_page": 2}).configure(table)
        context['table'] = table
        return context


class LigneFactureCreateView(CreateView):
    model = LigneFacture
    template_name = 'bill/create.html'
    fields = ['facture', 'produit', 'qte']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.fields['facture'] = forms.ModelChoiceField(
            queryset=Facture.objects.filter(id=self.kwargs.get('facture_pk')), initial=0)
        form.helper.add_input(Submit('submit', 'Créer', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk': self.kwargs.get('facture_pk')})
        return form


class LigneFactureUpdateView(UpdateView):
    model = LigneFacture
    template_name = 'bill/update.html'
    fields = ['facture', 'produit', 'qte']
    extra_context = {'titre': 'ligne_facture'}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()

        form.fields['facture'] = forms.ModelChoiceField(
            queryset=Facture.objects.filter(id=self.kwargs.get('facture_pk')), initial=0)
        form.fields['date'] = forms.DateField(
            widget=DatePickerInput(format='%m/%d/%Y')
        )
        form.helper.add_input(Submit('submit', 'Modifier', css_class='btn-primary'))
        form.helper.add_input(Button('cancel', 'Annuler', css_class='btn-secondary', onclick="window.history.back()"))
        self.success_url = reverse('facture_table_detail', kwargs={'pk': self.kwargs.get('facture_pk')})
        return form


class LigneFactureDeleteView(DeleteView):
    model = LigneFacture
    template_name = 'bill/delete.html'

    def get_success_url(self):
        self.success_url = reverse('facture_table_detail', kwargs={'pk': self.kwargs.get('facture_pk')})


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
        # Nous récupérons le contexte depuis la super-classe
        context = super(AllClients, self).get_context_data(**kwargs)
        # = LigneFacture.objects.values('facture__client_id').annotate(
        #    chiffre_affaire=Sum(
        #        ExpressionWrapper(F('qte'), output_field=FloatField())
        #        * F('produit__prix')))

        table = ClientTable(Client.objects.annotate(chiffre_affaire=Sum(
            ExpressionWrapper(F('facture_client__lignes_facture__qte'), output_field=FloatField())
            * F('facture_client__lignes_facture__produit__prix')))
        )

        RequestConfig(self.request, paginate={"per_page": 10}).configure(table)
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
        context['titre'] = "Tout les Facture du client" + self.kwargs.get('pk')
        return context


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

@login_required
def ClientDelete(request, pk):
    obj = get_object_or_404(Client, pk=pk)
    context = {'object': obj.__str__()}
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect("/all_clients")
    return render(request, "bill/delete.html", context)

@login_required
def deleteFacture(request, pk):
    obj = get_object_or_404(Facture, pk=pk)
    context = {'object': obj.__str__()}
    if request.method == "POST":
        obj.delete()
        return HttpResponseRedirect("/all_clients")
    return render(request, "bill/delete.html", context)
