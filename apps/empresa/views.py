from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def empresa_list(request):
    return render(request, 'empresa/index.html')

@login_required  
def empresa_detail(request, pk):
    return render(request, 'empresa/detail.html')

@login_required
def export_excel(request):
    return HttpResponse("Excel export")
