from django.shortcuts import render, get_object_or_404
from bill.models import Facture


# Create your views here.

def facture_detail_view(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    total = facture.total()
    context = {'facture': facture , "total":total}
    print(context)
    return render(request, 'bill/facture_detail.html', context)
